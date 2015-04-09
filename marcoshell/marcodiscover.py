#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

parser = argparse.ArgumentParser(description="Discovery of MarcoPolo nodes in the subnet")

parser.add_argument('-d', '--discover', dest="address", help="Multicast group where to discover", nargs='?', default="224.0.0.1")
parser.add_argument('-s', '--service', dest="service", help="Name of the service to look for", nargs='?')
parser.add_argument('-n', '--node', dest="node", help="Perform the discovery on only one node, identified by its ip/dns name", nargs="?")
args = parser.parse_args()


if __name__ == "__main__":
  import socket, json
  service_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
  
  if args.service:
    
    service_socket.sendto(bytes(args.service, 'utf-8'), ('127.0.1.1', 1338))
    data = service_socket.recv(4096)
    services = json.loads(data.decode('utf-8'))
    print(services)

  else:
    service_socket.sendto(bytes(json.dumps({"Command": "Marco"}), 'utf-8'), ('127.0.1.1', 1338))
    data = service_socket.recv(4096)
    services = json.loads(data.decode('utf-8'))
