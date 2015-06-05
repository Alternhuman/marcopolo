#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, defer

import os
from os import listdir, makedirs, path
from os.path import isfile, join
from io import StringIO

import sys, signal, json, logging
from twisted.internet.error import MulticastJoinError
import time
import pwd, grp
import re

sys.path.append('/opt/marcopolo')
from marco_conf import conf

from polobinding import PoloBinding
from polo import Polo
__author__ = 'Diego Martín'

offered_services = {}
user_services = {}

#verify = re.compile('^([\d\w]+):([\d\w]+)$')

polo_instances = {}
polobinding_instances = {}



def reload_services(sig, frame):
	signal.signal(signal.SIGUSR1, signal.SIG_IGN)
	polo.reload_services()
	signal.signal(signal.SIGUSR1, reload_services)

def sanitize_path(path_str):
	return path.normpath("/"+path_str).lstrip('/')

#TODO
def sigint_handler(signal, frame):
    reactor.stop()
    sys.exit(0)

@defer.inlineCallbacks
def graceful_shutdown():
	yield logging.info('Stopping service polod')

if __name__ == "__main__":
	pid = os.getpid()
	
	if not path.exists('/var/run/marcopolo'):
		makedirs('/var/run/marcopolo')
	
	f = open(conf.PIDFILE_POLO, 'w')
	f.write(str(pid))
	f.close()

	signal.signal(signal.SIGHUP, signal.SIG_IGN)
	signal.signal(signal.SIGUSR1, reload_services)
	
	logging.basicConfig(filename=conf.LOGGING_DIR+'polod.log', level=conf.LOGGING_LEVEL.upper(), format=conf.LOGGING_FORMAT)
	
	def start_multicast():
		for group in conf.MULTICAST_ADDRS:
			offered_services[group] = []
			user_services[group] = {}
			polo = Polo(offered_services[group], user_services[group], group)
			reactor.listenMulticast(conf.PORT, polo, listenMultiple=False, interface=group)
	
	def start_binding():
		polobinding = PoloBinding(offered_services[conf.MULTICAST_ADDR], 
									  user_services[conf.MULTICAST_ADDR], 
									  conf.MULTICAST_ADDR)
		reactor.listenUDP(conf.POLO_BINDING_PORT, polobinding, interface="127.0.0.1")

	reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)
	reactor.callWhenRunning(start_multicast)
	reactor.callWhenRunning(start_binding)
	reactor.run()

