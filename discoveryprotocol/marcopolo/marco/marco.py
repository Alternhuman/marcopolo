from marco_conf import conf

import sys, time, string
import socket
from marco_conf import utils

class Marco:
    def __init__(self):
        self.socket_mcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket_mcast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.socket_mcast.bind(('', 0)) # Usaremos el mismo socket para recibir los datos de cada nodo
        self.socket_mcast.settimeout(2.0) #https://docs.python.org/2/library/socket.html#socket.socket.settimeout
        self.nodes = set()

        #self.socket_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        #self.socket_recv.bind(('', conf.PORT))

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
            self.nodes.add(n)
            print(data.decode('utf-8'), file=sys.stderr)
        for node in self.nodes:
            print(node.address)


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


