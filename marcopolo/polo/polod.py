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

polo_instances = {}
polobinding_instances = {}


def reload_services(sig, frame):
	"""
	Captures the ``SIGUSR1`` signal and reloads the services\
	in each ``Polo`` object. The signal is ignored \
	during processing.

	:param signal sig: The signal identifier

	:param object frame: TODO
	"""
	signal.signal(signal.SIGUSR1, signal.SIG_IGN)
	for polo in polo_instances:
		polo.reload_services()
	signal.signal(signal.SIGUSR1, reload_services)

def sanitize_path(path_str):
	"""
	Prevents unwanted directory traversing and other bash vulnerabilities.

	:param str path_str: The path to be sanitized.

	:returns: The sanitized path.

	:rtype: str
	"""
	return path.normpath("/"+path_str).lstrip('/')

#TODO
def sigint_handler(signal, frame):
	"""
	A ``SIGINT`` handler.

	:param signal sig: The signal identifier

	:param object frame: TODO
	"""
	reactor.stop()
	sys.exit(0)

@defer.inlineCallbacks
def graceful_shutdown():
	"""
	Stops the reactor gracefully
	"""
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
		"""
		Starts a ``Polo`` instance for each multicast group configured in\ 
		conf.MULTICAST_ADDRS, initializing all the data structures
		"""
		for group in conf.MULTICAST_ADDRS:
			offered_services[group] = []
			user_services[group] = {}
			polo = Polo(offered_services[group], user_services[group], group)
			polo_instances[group]=polo
			reactor.listenMulticast(conf.PORT, polo, listenMultiple=False, interface=group)
	
	def start_binding():
		"""
		Starts the ``PoloBinding``
		"""
		polobinding = PoloBinding(offered_services, 
									  user_services, 
									  conf.MULTICAST_ADDRS
								)
		reactor.listenUDP(conf.POLO_BINDING_PORT, polobinding, interface="127.0.0.1")

	reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)
	reactor.callWhenRunning(start_multicast)
	reactor.callWhenRunning(start_binding)
	reactor.run()

