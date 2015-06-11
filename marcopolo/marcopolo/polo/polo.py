from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, defer

import os
from os import listdir, makedirs, path
from os.path import isfile, join
from io import StringIO

import sys, signal, json, logging
from twisted.internet.error import MulticastJoinError
import time
import pwd, grp
import re

#sys.path.append('/opt/marcopolo')
sys.path.append('/opt/')
from marcopolo.marco_conf import conf


class Polo(DatagramProtocol):
    """
    Twisted-inherited class in charge of receiving Marco requests on the defined multicast groups
    """
    
    def __init__(self, offered_services=[], user_services={}, multicast_group=conf.MULTICAST_ADDR, verify_regexp=conf.VERIFY_REGEXP):
        """
        Creates the ``Polo`` instance with the data structures to work with.
        If defined, the ``offered_services`` and ``user_services`` variables will be treated 
        as references to a list and dictionary respectively (i.e. the values will be modified, but
        the object reference will never be altered).
        
        :param list offered_services: A list of dictionaries which comprises all the root services.
        
        :param dict user_services: A dictionary of all the user services (the key is the user name 
            and the value is a list of services like that of offered_services).
        
        :param str multicast_group: The IPv4 address of the multicast group to join to. **Important**: The multicast_addr is not validated until the reactor is started.
        
        :param str verify_regexp: Regular expression used to verify an user service.
        """
        #super(Polo).__init__()
        self.offered_services = offered_services
        self.user_services = user_services
        self.verify = re.compile(verify_regexp)#re.compile('^([\d\w]+):([\d\w]+)$')
        self.multicast_group = multicast_group

    def reload_services(self):
        """
        Reloads both root and user services (calling :func:`reload_user_services`). The services stored in a file are loaded again, 
        whereas dynamic services are kept intact.
        """
        del self.offered_services[:] #http://stackoverflow.com/a/1400622/2628463
        
        logging.info("Reloading services in polo instance for group %s" % self.multicast_group)
        
        #Load list of filenames
        servicefiles = [ f for f in listdir(conf.CONF_DIR + conf.SERVICES_DIR) if isfile(join('/etc/marcopolo/polo/services',f)) ]

        service_ids = set()
        for service_file in servicefiles:
            try:
                with open(join(conf.CONF_DIR+conf.SERVICES_DIR, service_file), 'r', encoding='utf-8') as f:
                    service = json.load(f)
                    service["permanent"] = True
                    service["params"] = service.get("params", {})
                    service["file"] = service_file
                    groups = service.get("groups",[])
                    if self.multicast_group in groups or len(groups) == 0:
                        if not self.verify.match(service['id']):
                            if service['id'] in service_ids:
                                logging.warning("Service %s already published. The service in the file %s will not be added"  
                                    % (service['id'], service_file))
                            else:
                                service_ids.add(service['id'])
                                self.offered_services.append(service)

            except ValueError as e:
                logging.debug(str.format("The file {0} does not have a valid JSON structure", conf.SERVICES_DIR+service_file))
            except Exception as e:
                logging.warning("Unknown error: %s" % e)

        self.reload_user_services()

        logging.info("Polo instance for group " + self.multicast_group + ".Reloaded: Offering " + str(len(self.offered_services)) + " services")

    def reload_user_services(self):
        """
        Iterates through all the users who have services and calls 
        reload_user_services_iter for each of them
        """
        for user in self.user_services:
            self.reload_user_services_iter(user)

    def reload_user_services_iter(self, user):
        """
        Reloads the services for a given user

        :param str user: The name of the user
        """
        logging.info("Reloading user services")
        #Loads the user pwd structure
        try:
            user = pwd.getpwnam(user)
        except KeyError:
            return
        
        #Check if the user home path exists
        if path.exists(user.pw_dir):
            #The services must be stored in $HOME/.polo/
            polo_dir = path.join(user.pw_dir,conf.POLO_USER_DIR)
            username = user.pw_name
            self.user_services[username] = [service for service in self.user_services.get(username, []) if service[1] == False]
            
            servicefiles = [ join(polo_dir, f) for f in listdir(polo_dir) if isfile(join(polo_dir,f)) ]
            
            fileservices = []
            for service in servicefiles:
                try:
                    with open(service, 'r', encoding='utf-8') as f:
                        s = json.load(f)
                        s["permanent"] = True
                        s["params"] = s.get("params", {})
                        s["file"] = service
                        if not self.verify.match(s['id']):
                            fileservices.append(s)
                except ValueError:
                    logging.warning(str.format("The file {0} does not have a valid JSON structure", 
                                             conf.SERVICES_DIR+service))

            self.user_services[username] = self.user_services[username] + fileservices

    
    def startProtocol(self):
        """
        Operations to be performed before starting to listen
        """
        logging.info("Starting service polod")
        logging.info("Loading services")

        #List all files in the service directory
        services_dir = join(conf.CONF_DIR, conf.SERVICES_DIR)
        servicefiles = [ f for f in listdir(conf.CONF_DIR + conf.SERVICES_DIR) if isfile(join(services_dir,f)) ]
        
        service_ids = set()
        for service in servicefiles:
            try:
                with open(join(conf.CONF_DIR+conf.SERVICES_DIR, service), 'r', encoding='utf-8') as f:
                    s = json.load(f)
                    
                    s["permanent"] = True
                    s["params"] = s.get("params", {})
                    s["file"] = service
                    groups = s.get("groups",[])
                    if self.multicast_group in groups or len(groups) == 0:
                        if not self.verify.match(s['id']):
                            if s['id'] in service_ids:
                                logging.warning("Service %s already published. The service in the file %s will not be published" % (s['id'], service))
                            else:
                                service_ids.add(s['id'])
                                self.offered_services.append(s)
                    #if not self.verify.match(s['id']):
                    #   self.offered_services.append(s)
                        else:
                            logging.warning("The service %s does not have a valid id", s['id'])
            except ValueError:
                logging.warning(str.format("The file {0} does not have a valid JSON structure", conf.SERVICES_DIR+service))
            except Exception as e:
                logging.error("Unknown error %s", e)
        
        if conf.DEBUG:
            for s in self.offered_services:
                logging.debug("%s:%s"% (s['id'], s['params']))
        logging.info("Offering " + str(len(self.offered_services)) + " services")
        
        self.attempts = 0

        self.transport.joinGroup(self.multicast_group).addErrback(self.handler)
        
        self.transport.setTTL(conf.HOPS) #Go beyond the network. TODO
    
    def handler(self, arg):
        """
        An 'errback' that is called when the multicast subscription is unsuccessful.
        It schedules a retry and increments an attempt counter.

        :param object arg: The arg passed in the addErrback() call

        """
        #TODO: http://stackoverflow.com/questions/808560/how-to-detect-the-physical-connected-state-of-a-network-cable-connector
        logging.error("Error on joining the multicast group, %s. %d retries" % (conf.MULTICAST_ADDR, self.attempts))
        self.attempts += 1
        reactor.callLater(3, self.retry)
        
    def retry(self):
        """
        Tries to join the multicast group if it unsuccessful
        """

        if self.attempts < conf.RETRIES or conf.RETRIES < 0:
            self.transport.joinGroup(conf.MULTICAST_ADDR).addErrback(self.handler)
        else:
            logging.error("Could not joing the multicast group after %d attempts. Leaving" % (conf.RETRIES))
        
        

    def datagramReceived(self, datagram, address):
        """
        When a datagram is received the command is parsed and a response is generated

        :param bytes datagram: The byte stream with the message

        :param tuple address: A tuple with the requesting address and port
        """
        try:
            message_dict = json.loads(datagram.decode('utf-8'))
        except ValueError:
            logging.info("Datagram received from [%s:%s]. Invalid JSON structure" % (address[0], address[1]))
            return
        
        command = message_dict.get("Command", "")

        if command == 'Discover' or command == 'Marco':
            self.polo(command, address)
        elif command == 'Request-for' or command == 'Request-For':
            self.response_request_for(command, message_dict["Params"], address)
        elif command == 'Services':
            response_services(command, address)
        else:
            logging.info("Datagram received from [%s:%s]. Unknown command %s " % (address[0], address[1], datagram.decode('utf-8')))

    def polo(self, command, address):
        """
        Replies to `Polo` requests
        
        :param str command: The command that triggered this action
        
        :param tuple address: A tuple with the requesting address and port
        
        """
        response_dict = {}
        response_dict["Command"] = "Polo"
        response_dict["Params"] = conf.POLO_PARAMS
        
        json_msg = json.dumps(response_dict, separators=(',',':'))
        msg = json_msg.encode('utf-8')

        self.transport.write(msg, address)
    
    def response_services(self, command, param, address):
        """
        Replies to `Services` requests
        """

        response_services = []
        for service in self.offered_services:
            response_services.append(service['id'])

        self.transport.write(json.dumps({'Command': 'OK', 'Services': response_services}).encode('utf-8'), address)
    
    def response_request_for_user(self, command, user, service, address):
        """
        Handles user request-for requests

        :param str user: The name of the user
        :param str command: The command that triggered this action
        :param str service: The service name
        :param tuple address: A tuple with the requesting address and port

        If the user has not been added to the list of services before this request,
        reload_user_services_iter(user) is called
        """
        if self.user_services.get(user, None) is None:
            self.reload_user_services_iter(user)

        match = next((s for s in self.user_services.get(user, []) if s['id'] == service), None)
        
        if match:
            command_msg = json.dumps({'Command':'OK', 'Params': match.get("params", {})})
            self.transport.write(command_msg.encode('utf-8'), address)
            return

    def response_request_for(self, command, service, address):
        """
        Handles request-for requests

        :param str command: The command that triggered this action
        :param str service: The id of the service
        :param tuple address: A tuple with the requesting address and port
        """
        
        if self.verify.match(service):
            try:
                user, service = self.verify.match(service).groups()
            except (IndexError, ValueError):
                return
            self.response_request_for_user(command, user, service, address)
            return

        match = next((s for s in self.offered_services if s['id'] == service), None)
        if match:
            command_msg = json.dumps({'Command':'OK', 'Params':match.get("params", {})})

            self.transport.write(command_msg.encode('utf-8'), address)
            return