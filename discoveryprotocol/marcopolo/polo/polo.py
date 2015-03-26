__author__ = 'martin'

import socket, sys, struct
from marco_conf import conf

def polo():
  s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
  s.bind(('', conf.PORT))

  while 1:
    m=s.recvfrom(4096)

    #print(isinstance(m[0].decode('utf-8'), str))
    print(m[0].decode('utf-8'), file=sys.stderr)

def polocast():
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind(('', conf.PORT))
  mreq = struct.pack("4sl", socket.inet_aton(conf.MULTICAST_ADDR), socket.INADDR_ANY) # WAT?
  s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

  while 1:
      print(s.recv(4096))

if __name__ == "__main__":
  polocast()