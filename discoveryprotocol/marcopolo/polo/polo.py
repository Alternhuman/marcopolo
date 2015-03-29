__author__ = 'martin'

import socket, sys, struct
from marco_conf import conf
import json
from io import StringIO

class Polo:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) #socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #TODO: Uncomment when more nodes are available
        self.mreq = struct.pack("4sl", socket.inet_aton(conf.MULTICAST_ADDR), socket.INADDR_ANY) # See comment at bottom
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)
        self.socket.bind(('', conf.PORT))

        from os import listdir
        from os.path import isfile, join

        self.services = []

        servicefiles = [ f for f in listdir('/etc/marcopolo/polo/services') if isfile(join('/etc/marcopolo/polo/services',f)) ]
        for service in servicefiles:

            try:
                with open(join(conf.SERVICES_DIR, service), 'r', encoding='utf-8') as f:
                    self.services.append(json.load(f))
            except ValueError:
                print(str.format("El archivo {0} no cuenta con una estructura JSON válida", conf.SERVICES_DIR+service))

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

    def response_discover(self, command, address):
        response_dict = {}
        response_dict["node_alive"]= True
        response_dict["multicast_group"] = conf.MULTICAST_ADDR
        response_dict["services"] = self.services#conf.SERVICES
        json_msg = json.dumps(response_dict, separators=(',',':'))
        msg = bytes(json_msg, 'utf-8')
        self.socket.sendto(msg, address)

    def polo(self):
        while True:
            try:
                command, address = self.socket.recvfrom(4096)

                command = command.decode('utf-8')

                command = json.load(StringIO(command))["command"]

                if command == 'Discover':
                    self.response_discover(command, address)
                elif command == 'Services':
                    self.services(command, address)
                else:
                    print("Unknown command")

            except KeyboardInterrupt:
                self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, self.mreq)
                self.socket.close()
                sys.exit(0)



if __name__ == "__main__":
  Polo().polo()