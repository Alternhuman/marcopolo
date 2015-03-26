__author__ = 'martin'

import socket, sys
from marco_conf import conf

def polo():
  s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
  s.bind(('', conf.PORT))

  while 1:
    m=s.recvfrom(4096)

    #print(isinstance(m[0].decode('utf-8'), str))
    print(m[0].decode('utf-8'), file=sys.stderr)


if __name__ == "__main__":
  polo()