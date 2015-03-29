from marco_conf import conf

import sys, time, string
import socket
from marco_conf import utils
import json
from io import StringIO
class Marco:
    def __init__(self):
        self.socket_mcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket_mcast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.socket_mcast.bind(('', 0)) # Usaremos el mismo socket para recibir los datos de cada nodo
        self.socket_mcast.settimeout(0.5) #https://docs.python.org/2/library/socket.html#socket.socket.settimeout
        self.nodes = set()

    def marcocast(self):
        data = bytes(str(time.time()), 'utf-8')
        self.socket_mcast.sendto(data, (conf.MULTICAST_ADDR, conf.PORT))

        while 1:
            try:
                data,address = self.socket_mcast.recvfrom(4096)
            except socket.timeout:
                break

            n = utils.Node()
            n.address = address
            n.services = json.load(StringIO(data.decode('utf-8')))
            self.nodes.add(n)
        print("Lista de nodos")
        for node in self.nodes:
            print(str.format("Nodo en {0}:{1} con los servicios:", node.address[0], node.address[1]), file=sys.stdout)
            #print(node.address, node.services)
            for key in node.services:
                #print(node.services[key])
                print(str.format("{0} v{1}", node.services[key]['id'], node.services[key]['version']))
                #print(str.format("{0} v{1}", service, service))


if __name__ == "__main__":
    Marco().marcocast()

"""def marco():
  s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) #TODO: IPv6?
  s.bind(('', 0))
  s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  #print(conf.PORT, file=sys.stderr)
  while 1:
    data = bytes(str(time.time()), 'utf-8')
    print(s.sendto(data, ('<broadcast>', conf.PORT)))

    time.sleep(2)

def marcocast():
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
  while 1:
    data = bytes(str(time.time()), 'utf-8')
    s.sendto(data, (conf.MULTICAST_ADDR, conf.PORT))
    time.sleep(2)"""


