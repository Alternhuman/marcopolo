__author__ = 'martin'

import socket, sys, struct
from marco_conf import conf

class Polo:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) #socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.mreq = struct.pack("4sl", socket.inet_aton(conf.MULTICAST_ADDR), socket.INADDR_ANY) # WAT?
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)


        self.socket.bind(('', conf.PORT))
        """
        https://docs.python.org/2/library/struct.html#format-characters
        struct.pack interpreta cadenas de caracteres como conjuntos de datos binarios
        4sl especifica el formato de conversión s = char[], l = signed long = 4 four-letter string plus long

        El objetivo es empaquetar esta estructura:
        struct ip_mreq {
            struct in_addr imr_multiaddr;   /* IP multicast address of group */
            struct in_addr imr_interface;   /* local IP address of interface */
        };
        http://stackoverflow.com/a/16419856
        """

    def polo(self):
        while 1:
            try:
                data,address = self.socket.recvfrom(4096)

                print(data.decode('utf-8'), file=sys.stderr)

                self.socket.sendto(bytes("Hola", 'utf-8'), address)
            except KeyboardInterrupt:
                self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, self.mreq)
                self.socket.close()
                sys.exit(0)



if __name__ == "__main__":
  Polo().polo()