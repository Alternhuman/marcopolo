#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse, socket, json
from sys import exit
import sys

from marcopolo.bindings import marco
from marcopolo.marco_conf.utils import Node

TIMEOUT = 4000

def main(args=None):
    parser = argparse.ArgumentParser(description="Discovery of MarcoPolo nodes in the subnet")

    parser.add_argument('-d', '--discover', dest="address", type=str, help="Multicast group where to discover", nargs='?', default="224.0.0.1")
    parser.add_argument('-s', '--service', dest="service", type=str,     help="Name of the service to look for", nargs='?')
    parser.add_argument('-S', '--services', dest="services", help="Discover all services in a node", nargs='?')
    parser.add_argument('-n', '--node', dest="node", help="Perform the discovery on only one node, identified by its ip/dns name", nargs="?")
    parser.add_argument('--sh', '--shell', dest="shell", help="Print output so it can be used as an interable list in a shell", nargs='?')
    #parser.add_argument('-v', '--verbose', dest="verbose", help="Verbose mode")
    args = parser.parse_args(args)

    if args.service:
        
        m = marco.Marco()

        try:
            nodes = m.request_for(args.service)
        except marco.MarcoTimeOutException:
            print("No connection to the resolver")
            sys.exit(1)
        if len(nodes) > 0:

            cadena = ""
            for node in nodes:
                cadena += node.address + "\n" if not args.shell else " "

            print(cadena[:-1])
        else:
            print("There are no nodes available for the requested query")

        sys.exit(0)

    else:

        m = marco.Marco()
        try:
            nodes = m.marco()
        except marco.MarcoTimeOutException:
            print("No connection to the resolver")
            sys.exit(1)
        
        cadena = ""
        if len(nodes) > 0:
            for node in nodes:
                cadena += node.address + "\n" if not args.shell else " "
            print(cadena[:-1])
        else:
            print("There are no nodes available for the requested query")

if __name__ == "__main__":
    main(sys.argv)

