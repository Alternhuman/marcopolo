#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, defer

import os
from os import listdir
from os.path import isfile, join
from io import StringIO

import sys, signal, json, logging

from marco_conf import conf

__author__ = 'Diego Martín'

class Polo(DatagramProtocol):
	"""
	Twisted inherited class in charge of listening on the multicast group
	"""
	
	def startProtocol(self):
		"""
		Operations to be performed before starting to listen
		"""
		logging.info("Starting service polod")
		self.services = []

		#List all files in the service directory
		servicefiles = [ f for f in listdir(conf.CONF_DIR + conf.SERVICES_DIR) if isfile(join('/etc/marcopolo/polo/services',f)) ]
		
		for service in servicefiles:
			try:
			    with open(join(conf.CONF_DIR+conf.SERVICES_DIR, service), 'r', encoding='utf-8') as f:
			        self.services.append(json.load(f))
			except ValueError:
			    logging.debug(str.format("The file {0} does not have a valid JSON structures", conf.SERVICES_DIR+service))

		#if conf.DEBUG:
		#	for s in self.services:
		#		print(s['id'])
		logging.info("Offering " + str(len(self.services)) + " services")

		#self.transport.setTTL(2) Para salir más allá de la subred
		self.transport.joinGroup(conf.MULTICAST_ADDR)
		self.transport.setTTL(conf.HOPS) #Go beyond the network

	def datagramReceived(self, datagram, address):
		"""
		When a datagram is received the command is parsed and a response is generated
		"""
		
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
			self.services(command, address)
		else:
			print("Unknown command: " + datagram, file=sys.stderr)

	def response_discover(self, command, address):
		response_dict = {}
		response_dict["Command"] = "Polo"
		response_dict["node_alive"]= True
		response_dict["multicast_group"] = conf.MULTICAST_ADDR
		response_dict["services"] = self.services#conf.SERVICES
		
		json_msg = json.dumps(response_dict, separators=(',',':'))
		msg = bytes(json_msg, 'utf-8')

		self.transport.write(msg, address)


	def response_request_for(self, command, param, address):
		match = next((s for s in self.services if s['id'] == param), None)
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
	os.close(0)
	os.close(1)
	os.close(2)
	logging.basicConfig(filename=conf.LOGGING_DIR+'polod.log', level=conf.LOGGING_LEVEL.upper(), format=conf.LOGGING_FORMAT)
	reactor.listenMulticast(conf.PORT, Polo(), listenMultiple=True)
	reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)
	reactor.run()