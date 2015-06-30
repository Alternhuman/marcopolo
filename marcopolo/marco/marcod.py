#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor, defer

import sys, logging, os, signal
from os import path, makedirs, listdir


from marcopolo.marco_conf import utils

from marcopolo.marco import conf
from marcopolo.marco.marcobinding import MarcoBinding

def graceful_shutdown():
    logging.info('Stopping service marcod')

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    
    pid = os.getpid()


    logging.basicConfig(filename=os.path.join(conf.LOGGING_DIR, conf.LOGGING_FILENAME), 
                        level=conf.LOGGING_LEVEL.upper(), 
                        format=conf.LOGGING_FORMAT)
    
    server = reactor.listenUDP(conf.MARCOPORT, MarcoBinding(), interface=conf.BINDING_IFACE)
    reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)
    reactor.run()

if __name__ == "__main__":
    main(sys.argv)

