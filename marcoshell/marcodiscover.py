#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

parser = argparse.ArgumentParser(description="Discovery of MarcoPolo nodes in the subnet")

parser.add_argument('-d', '--discover', dest="address", help="Multicast group where to discover", nargs='?', default="224.0.0.1")
parser.add_argument('-s', '--service0', dest="service", help="Name of the service to look for", nargs='?')
args = parser.parse_args()

print(args)

if args.service:
  import socket, json
  from io import StringIO
  service_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
  service_socket.sendto(bytes(args.service, 'utf-8'), ('127.0.1.1', 1338))
  data = service_socket.recv(4096)
  services = json.load(StringIO(data.decode('utf-8')))
  print(services)
