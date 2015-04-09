#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, defer

import os
from os import listdir, makedirs, path
from os.path import isfile, join
from io import StringIO

import sys, signal, json, logging

sys.path.append('/opt/marcopolo')
from marco_conf import conf

__author__ = 'Diego Martín'

offered_services = []

def reload_services(signal, frame):
	signal.signal(signal.SIGUSR1, signal.SIG_IGN)
	global offered_services
	offered_services = []
	logging.info("Reloading services")
	
	servicefiles = [ f for f in listdir(conf.CONF_DIR + conf.SERVICES_DIR) if isfile(join('/etc/marcopolo/polo/services',f)) ]

	for service in servicefiles:
		try:
		    with open(join(conf.CONF_DIR+conf.SERVICES_DIR, service), 'r', encoding='utf-8') as f:
		        offered_services.append(json.load(f))
		except ValueError:
		    logging.debug(str.format("The file {0} does not have a valid JSON structures", conf.SERVICES_DIR+service))

	logging.info("Reloaded: Offering " + str(len(offered_services)) + " services")
	signal.signal(signal.SIGUSR1, reload_services)

class Polo(DatagramProtocol):
	"""
	Twisted inherited class in charge of listening on the multicast group
	"""
	
	def startProtocol(self):
		"""
		Operations to be performed before starting to listen
		"""
		logging.info("Starting service polod")
		global offered_services
		#offered_services = []

		#List all files in the service directory
		servicefiles = [ f for f in listdir(conf.CONF_DIR + conf.SERVICES_DIR) if isfile(join('/etc/marcopolo/polo/services',f)) ]
		
		for service in servicefiles:
			try:
			    with open(join(conf.CONF_DIR+conf.SERVICES_DIR, service), 'r', encoding='utf-8') as f:
			        offered_services.append(json.load(f))
			except ValueError:
			    logging.debug(str.format("The file {0} does not have a valid JSON structures", conf.SERVICES_DIR+service))

		#if conf.DEBUG:
		#	for s in offered_services:
		#		print(s['id'])
		logging.info("Offering " + str(len(offered_services)) + " services")

		#self.transport.setTTL(2) Para salir más allá de la subred
		self.transport.joinGroup(conf.MULTICAST_ADDR)
		self.transport.setTTL(conf.HOPS) #Go beyond the network

	def datagramReceived(self, datagram, address):
		"""
		When a datagram is received the command is parsed and a response is generated
		"""
		global offered_services
		try:
			message_dict = json.loads(datagram.decode('utf-8'))
		except ValueError:
			return
		
		command = message_dict["Command"]

		if command == 'Discover' or command == 'Marco':
			self.response_discover(command, address)
		elif command == 'Request-for':
			self.response_request_for(command, message_dict["Params"], address)
		elif command == 'Services':
			offered_services(command, address)
		else:
			print("Unknown command: " + datagram, file=sys.stderr)

	def response_discover(self, command, address):
		global offered_services
		response_dict = {}
		response_dict["Command"] = "Polo"
		response_dict["node_alive"]= True
		response_dict["multicast_group"] = conf.MULTICAST_ADDR
		response_dict["services"] = offered_services#conf.SERVICES
		
		json_msg = json.dumps(response_dict, separators=(',',':'))
		msg = bytes(json_msg, 'utf-8')

		self.transport.write(msg, address)


	def response_request_for(self, command, param, address):
		global offered_services
		match = next((s for s in offered_services if s['id'] == param), None)
		command_msg = json.dumps({'Command':'OK', 'Params':json.dumps(match)})

		self.transport.write(bytes(command_msg, 'utf-8'), address)

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
	os.close(0)
	os.close(1)
	os.close(2)
	logging.basicConfig(filename=conf.LOGGING_DIR+'polod.log', level=conf.LOGGING_LEVEL.upper(), format=conf.LOGGING_FORMAT)
	reactor.listenMulticast(conf.PORT, Polo(), listenMultiple=True)
	reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)
	reactor.run()
