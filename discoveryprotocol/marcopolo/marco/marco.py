from marco_conf import conf

import sys, time, string
import socket

def marco():
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
    time.sleep(2)

if __name__ == "__main__":
    marcocast()

