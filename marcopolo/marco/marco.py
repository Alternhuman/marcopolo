from __future__ import division
from __future__ import absolute_import
import socket, sys, json, logging, os
from os import path
from copy import copy

from marcopolo.marco_conf import utils
from marcopolo.marco import conf

import six

class MarcoException(Exception):
    pass

class Marco:
    def __init__(self):
        """
        Initializes all the data structures and sockets, setting timeouts and other socket options
        """
        error = False
        try:
            self.socket_bcast = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
            self.socket_bcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.socket_bcast.settimeout(conf.TIMEOUT/1000.0) #https://docs.python.org/2/library/socket.html#socket.socket.settimeout
            
            self.socket_mcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.socket_mcast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2) #If not otherwise specified, multicast datagrams are sent with a default value of 1, to prevent them to be forwarded beyond the local network. To change the TTL to the value you desire (from 0 to 255)
            self.socket_mcast.settimeout(conf.TIMEOUT/1000.0) #https://docs.python.org/2/library/socket.html#socket.socket.settimeout
            
            self.socket_ucast = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
            self.socket_ucast.settimeout(conf.TIMEOUT/1000.0) #https://docs.python.org/2/library/socket.html#socket.socket.settimeout
            self.nodes = set()
        
        except Exception as e:
            error = True

        if error:
            logging.error("Error in initialization: %s" % e)
            raise MarcoException("Error in initialization: %s" % e)

    def __del__(self):
        """
        Destroys all socket connections prior deleting
        """
        self.socket_bcast.close()
        self.socket_mcast.close()
        self.socket_ucast.close()

    def marco(self, max_nodes=None, exclude=[], timeout=None, params={}, retries=0, group=conf.MULTICAST_ADDR):
        """
        Sends a `marco` message to all nodes, which reply with a Polo message. \
        Upon receiving all responses (those arriving before the timeout), \
        a collection of the response information is returned.
        
        :param list exclude: List of nodes to be excluded from the returned ValueError.

        :param int timeout: If set, overrides the default timeout value.

        :param int retries: If set to a value greater than 0, retries the *retries* times if the first attempt is unsuccessful

        :param int max_nodes: Maximum number of nodes to be returned. If set to `None`, no limit is applied.
        
        :returns: A list of all responding nodes.
        """
        if group is None:
            group = conf.MULTICAST_ADDR

        counter = 0
        
        #Python 2 and 3 compatibility in byte encoding
        #if sys.version_info[0] < 3:
        discover_msg = json.dumps({'Command': 'Marco'}).encode('utf-8')
        #else:
        #    discover_msg = bytes(json.dumps({'Command': 'Marco'}), 'utf-8')

        #Send to group IP
        if -1 == self.socket_mcast.sendto(discover_msg, (group, conf.POLOPORT)):
            raise MarcoException("Error on multicast sending")
        
        #Timeout check
        error = None
        if timeout:
            try:
                self.socket_mcast.settimeout(int(timeout)/1000.0)
            except ValueError:
                error = True
            if error:
                raise MarcoException("Invalid timeout value")

        #max_nodes check
        nodes = set()
        error=None
        if max_nodes:
            try:
                max_nodes = int(max_nodes)
            except ValueError:
                error = True
            
            if error:
                raise MarcoException("Invalid max_nodes value")

        
        #exclude check
        if exclude and not (isinstance(exclude, (list, tuple))):
            raise MarcoException("Invalud exclude value. Must be instance of array or set()")
        
        error = None
        if retries:
            try:
                retries = int(retries)
                attempts = 0
            except ValueError:
                error = True

            if error:
                raise MarcoException("Invalid retries value")
        else:
            attempts = 0

        stop = False
        while attempts < retries + 1  and not stop:

            #Looping until timeout is raised or max_nodes is reached
            while True:
                try:
                    msg, address = self.socket_mcast.recvfrom(conf.FRAME_SIZE)
                except socket.timeout:
                    attempts += 1
                    break
                
                error = None
                
                try:
                    json_data = json.loads(msg.decode('utf-8'))
                except ValueError:
                    error = True
                
                if error:
                    raise MarcoException("Malformed message")

                if json_data.get("Command", "") == "Polo" and address not in exclude:

                    n = utils.Node()
                    n.address = address[0] # IP address.
                    n.params = json_data.get("Params", {})

                    if type(params) != type({}):
                        raise MarcoException("params must be a dictionary")

                    for name, value in params.items():
                        if n.params.get(name, None) != value:
                            break
                    else:
                        nodes.add(n)

                    stop = True
                
                if max_nodes:
                    counter +=1
                    if counter >= max_nodes:
                        stop = True
                        break

        if conf.DEBUG:
            debstr = ""
            for node in nodes:
                debstr = "There is a node at %s joining the multicast group %s with the services: " % (node.address, node.multicast_group)
                
                for service in n.services:
                    debstr += "%s. Version: %s " % (service["id"], service["version"])

            logging.debug(debstr)
        
        
        return copy(nodes)

    def services(self, addr, timeout=None, retries=0):
        """
        Searches for the services available in a certain node identified by its address
        
        :param string addr: Address of the node
        
        :param int port: UDP port of the Polo instance. If not given, the default is the port in the conffile
        
        :returns: An array with all detected nodes
        """

        #Validation of addr
        if addr == None or addr == '':
            logging.debug('Address cannot be empty: %s', addr)
            raise MarcoException('Address cannot be empty: %s', addr)
        
        error = None
        try:
            socket.gethostbyname(addr) # Gethostbyname throws a gaierror if neither a valid IP address or DNS name is passed. Easiest way to perform both checks
        except socket.gaierror:
            logging.debug('Invalid address or DNS name: %s', addr)
            error = True
        
        if error:
            raise MarcoException('Invalid address or DNS name: %s', addr)

        error = None

        if timeout:
            try:
                self.socket_mcast.settimeout(int(timeout)/1000.0)
            except ValueError:
                error = True
            if error:
                raise MarcoException("Invalid timeout value")

        discover_msg = json.dumps({'Command': 'Services'}).encode('utf-8')
        
        if -1 == self.socket_ucast.sendto(discover_msg, (addr, conf.POLOPORT)):
            raise MarcoException("Error on multicast sending")

        try:
            msg, address = self.socket_ucast.recvfrom(conf.FRAME_SIZE)
        except socket.timeout:
            return 

        try:
            json_data = json.loads(msg.decode('utf-8'))
        except ValueError:
            raise MarcoException("Error in response")
        
        if conf.DEBUG:
            logging.debug("There's a node at {0} joining the multicast group", address)

        n = utils.Node()
        n.address = address[0]
        n.services = json_data.get("Params", [])
        
        return n


    def request_for(self, service, node=None, max_nodes=None, exclude=[], params={}, timeout=None, group=conf.MULTICAST_ADDR):
        """
        Request all nodes offering a certain service or the details for one single node
        
        :param string service: Name of the requested service
        
        :param string node: Address or name of the desired node
        
        :returns: an array with all the available nodes
        """
        
        nodes = set()
        #if sys.version_info[0] < 3:
        command_msg = json.dumps({'Command':'Request-For', 'Params':service}).encode('utf-8')
        #else:
        #    command_msg = bytes(json.dumps({'Command':'Request-For', 'Params':service}), 'utf-8')

        if not isinstance(service, six.string_types):
            logging.info('Bad formatted request')
            raise MarcoException('Bad formatted request')

        if(node):
            if timeout:
                try:
                    self.socket_ucast.settimeout(int(timeout)/1000.0)
                except ValueError:
                    error = True
                if error:
                    raise MarcoException("Invalid timeout value")
            
            try: #Validation
                socket.gethostbyname(node) # Gethostbyname throws a gaierror if neither a valid IP address or DNS name is passed. Easiest way to perform both checks
            except socket.gaierror:
                logging.info('Bad address')
                raise MarcoException('Bad address')

            if -1 == self.socket_ucast.sendto(command_msg, node):
                raise MarcoException("Error on multicast sending")

            try:
                response = self.socket_ucast.recv(conf.FRAME_SIZE)
            except socket.timeout:
                return

            n = utils.Node()
            n.address = node
            n.services = []



            try:
                n.services.append(json.loads(response))
            except ValueError:
                raise MarcoException("Error on response")
            nodes.append(n)
            return nodes
        else:
            #Multicast request
            error = None
            if timeout:
                try:
                    self.socket_mcast.settimeout(int(timeout)/1000.0)
                except ValueError:
                    error = True
                if error:
                    raise MarcoException("Invalid timeout value")

            if max_nodes:
                try:
                    max_nodes = int(max_nodes)
                except ValueError:
                    error = True
            
                if error:
                    raise MarcoException("Invalid max_nodes value")

            if exclude and not (isinstance(exclude, (list, tuple))):
                raise MarcoException("Invalud exclude value. Must be instance of array or set()")

            
            self.socket_mcast.sendto(command_msg, (group, conf.POLOPORT))
            counter = 0
            while True:
                try:
                    response, address = self.socket_mcast.recvfrom(conf.FRAME_SIZE)
                except socket.timeout:
                    break

                try:
                    response = json.loads(response.decode('utf-8'))
                except ValueError:
                    continue
                if response.get("Command", "") == 'OK' and address not in exclude:
                    n = utils.Node()
                    n.address = address[0]
                    n.params = response.get("Params", {})
                    
                    if type(params) != type({}):
                        raise MarcoException("params must be a dictionary")

                    for name, value in params.items():
                        if n.params.get(name, None) != value:
                            break
                    else:
                        nodes.add(n)

                if max_nodes:
                    counter +=1
                    if counter >= max_nodes:
                        break
            return nodes

    def request_one(self, service, max_nodes=None, exclude=[], timeout=None):
        return self.request_for(service, max_nodes=1, exclude=exclude, timeout=timeout)



