from marco_conf import conf

import sys, time, string
import socket
from marco_conf import utils
import json
from io import StringIO
class Marco:
    def __init__(self):
        self.socket_bcast = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        self.socket_bcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.socket_mcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket_mcast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2) #If not otherwise specified, multicast datagrams are sent with a default value of 1, to prevent them to be forwarded beyond the local network. To change the TTL to the value you desire (from 0 to 255)
        self.socket_mcast.bind(('', 0)) # Usaremos el mismo socket para recibir los datos de cada nodo
        self.socket_mcast.settimeout(conf.TIMEOUT) #https://docs.python.org/2/library/socket.html#socket.socket.settimeout
        self.nodes = set()

    def discover(self):
        discover_msg = bytes(str("Discover"), 'utf-8')

        discover_msg = bytes(json.dumps({'command': 'Discover'}), 'utf-8')
        self.socket_mcast.sendto(discover_msg, (conf.MULTICAST_ADDR, conf.PORT))

        stop = True

        while stop:
            try:
                msg, address = self.socket_mcast.recvfrom(4096)
            except socket.timeout:
                stop = False
                break

            json_data = json.load(StringIO(msg.decode('utf-8')))

            n = utils.Node()
            n.address = address
            n.multicast_group = str(json_data["multicast_group"])
            n.services = json_data["services"]

            self.nodes.add(n)
        for node in self.nodes:
            print(str.format("There's a node at {0} joining the multicast group {1} with the services: ", node.address, node.multicast_group))
            for service in n.services:
                print(str.format("{0}. Version: {1} ", service["id"], service["version"]))

    def services(self, addr, port=conf.PORT):

        if addr == None or addr == '':
            raise InvalidURLException

        services_msg = bytes(str("Services"))
        self.socket_mcast.sendto(services_msg, (addr, conf.PORT))

        stop = True

        while stop:
            try:
                msg, address = self.socket_mcast.recvfrom(4096)
            except socket.timeout:
                stop = False
                break
            print(msg)

            json_data = json.load(StringIO(msg.decode('utf-8')))

            n = utils.Node()
            n.address = address
            n.multicast_group = str(json_data["multicast_group"])
            n.services = json.loads(json_data["services"])
            self.nodes.add(n)
        for node in n:
            print("There's a node at {0} joining the multicast group")

    def marcocast(self):
        data = bytes(str(time.time()), 'utf-8')
        self.socket_mcast.sendto(data, (conf.MULTICAST_ADDR, conf.PORT))
        stop = True
        while stop:
            try:
                data,address = self.socket_mcast.recvfrom(4096)
            except socket.timeout:
                stop = False
                break

            n = utils.Node()
            n.address = address
            n.services = json.load(StringIO(data.decode('utf-8')))
            self.nodes.add(n)
        """print("Lista de nodos")
        for node in self.nodes:
            print(str.format("Nodo en {0}:{1} con los servicios:", node.address[0], node.address[1]), file=sys.stdout)
            #print(node.address, node.services)
            for key in node.services:
                #print(node.services[key])
                print(str.format("{0} v{1}", node.services[key]['id'], node.services[key]['version']))
                #print(str.format("{0} v{1}", service, service))"""


class InvalidURLException(Exception):
    pass

#Discover

if __name__ == "__main__":
    #Marco().marcocast()
    Marco().discover()


