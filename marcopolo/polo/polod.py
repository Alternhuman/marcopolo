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

offered_services = []
user_services = {}

verify = re.compile('^([\d\w]+):([\d\w]+)$')

polo = Polo(offered_services, user_services, conf.VERIFY_REGEXP)
polobinding = PoloBinding(offered_services, user_services, conf.VERIFY_REGEXP)


def reload_services(sig, frame):
	print("Reloading")
	signal.signal(signal.SIGUSR1, signal.SIG_IGN)
	global offered_services
	del offered_services[:] #http://stackoverflow.com/a/1400622/2628463
	logging.info("Reloading services")
	
	servicefiles = [ f for f in listdir(conf.CONF_DIR + conf.SERVICES_DIR) if isfile(join('/etc/marcopolo/polo/services',f)) ]

	for service in servicefiles:
		try:
			with open(join(conf.CONF_DIR+conf.SERVICES_DIR, service), 'r', encoding='utf-8') as f:
				service = json.load(f)
				service["permanent"] = True
				offered_services.append(json.load(f))
		except ValueError:
			logging.debug(str.format("The file {0} does not have a valid JSON structure", conf.SERVICES_DIR+service.get("id")))

	for user in user_services:
		polo.reload_user_services(user)

	logging.info("Reloaded: Offering " + str(len(offered_services)) + " services")
	
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
	#signal.signal(signal.SIGINT, sigint_handler)
	#Closing std(in|out|err)
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
		reactor.listenMulticast(conf.PORT, polo, listenMultiple=False)
	
	def start_binding():
		reactor.listenUDP(conf.POLO_BINDING_PORT, polobinding, interface="127.0.0.1")

	reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)
	reactor.callWhenRunning(start_multicast)
	reactor.callWhenRunning(start_binding)
	reactor.run()

