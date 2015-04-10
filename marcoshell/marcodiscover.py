#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, socket, json
from sys import exit

TIMEOUT = 4000

parser = argparse.ArgumentParser(description="Discovery of MarcoPolo nodes in the subnet")

parser.add_argument('-d', '--discover', dest="address", type=str, help="Multicast group where to discover", nargs='?', default="224.0.0.1")
parser.add_argument('-s', '--service', dest="service", type=str,	 help="Name of the service to look for", nargs='?')
parser.add_argument('-S', '--services', dest="services", help="Discover all services in a node", nargs='?')
parser.add_argument('-n', '--node', dest="node", help="Perform the discovery on only one node, identified by its ip/dns name", nargs="?")
#parser.add_argument('-v', '--verbose', dest="verbose", help="Verbose mode")
args = parser.parse_args()


if __name__ == "__main__":

  service_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
  service_socket.settimeout(TIMEOUT/1000.0) 

  if args.service:
    
    service_socket.sendto(bytes(json.dumps({"Command": "Request-for", "Params":args.service}), 'utf-8'), ('127.0.1.1', 1338))
    try:
      data = service_socket.recv(4096)
    except socket.timeout:
      print("No response from resolver")
      exit(1)
    addresses = json.loads(data.decode('utf-8'))
    
    cadena = ""
    if len(addresses) > 0:
      for address in addresses:
        cadena += address + "\n"
      print(cadena)

    else:
      print("There are no nodes available for the requested query")
    print(nodes)

  else:
    service_socket.sendto(bytes(json.dumps({"Command": "Marco"}), 'utf-8'), ('127.0.1.1', 1338))
    try:
      data = service_socket.recv(4096)
    except socket.timeout:
      print("No response from resolver")
      exit(1)
    nodes = json.loads(data.decode('utf-8'))
    
    cadena = ""
    if len(nodes) > 0:
      for node in nodes:
        cadena += node + "\n"
      print(cadena[:-1])
    else:
      print("There are no nodes available for the requested query")
