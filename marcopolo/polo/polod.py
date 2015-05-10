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

sys.path.append('/opt/marcopolo')
from marco_conf import conf

__author__ = 'Diego Martín'

offered_services = []
temporal_services = []
def reload_services(sig, frame):
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

class PoloBinding(DatagramProtocol):
	def startProtocol(self):
		pass

	def datagramReceived(self, datagram, address):
		datos = datagram.decode('utf-8')
		datos_dict = json.loads(datos)
		if datos_dict['Command'] == 'Register':
			self.register_service(datos['Params'])

	def register_service(self, service_id):
		global temporal_services
		temporal_services.add({'Params':service_id})

	def remove_service(self, service_id):
		global temporal_services
		temporal_services = [service for service in temporal_services if not service['Params'] == service_id]


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

		
		self.attempts = 0
		def handler(arg):
			logging.error("Error on joining the multicast group, %s. %d retries" % (conf.MULTICAST_ADDR, self.attempts))
			self.attempts += 1
			time.sleep(3)
			if self.attempts < conf.RETRIES:
				self.transport.joinGroup(conf.MULTICAST_ADDR).addErrback(handler)
			else:
				logging.error("Could not joing the multicast group after %d attempts. Leaving" % (conf.RETRIES))
				reactor.stop()

		
		self.transport.joinGroup(conf.MULTICAST_ADDR).addErrback(handler)
		
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
			self.polo(command, address)
		elif command == 'Request-for' or command == 'Request-For':
			self.response_request_for(command, message_dict["Params"], address)
		elif command == 'Services':
			response_services(command, address)
		else:
			print("Unknown command: " + datagram.decode('utf-8'))#, file=sys.stderr)

	def polo(self, command, address):
		global offered_services
		response_dict = {}
		response_dict["Command"] = "Polo"
		response_dict["Params"] = ""
		#response_dict["node_alive"]= True
		#response_dict["multicast_group"] = conf.MULTICAST_ADDR
		#response_dict["services"] = offered_services#conf.SERVICES
		
		json_msg = json.dumps(response_dict, separators=(',',':'))
		msg = bytes(json_msg, 'utf-8')

		self.transport.write(msg, address)
	
	def response_services(self, command, param, address):
		global offered_services
		response_services = []
		for service in offered_services:
			response_services.append(service['id'])

		self.transport.write(json.dumps({'Command': 'OK', 'Services': response_services}))
	
	def response_request_for(self, command, param, address):
		global offered_services
		match = next((s for s in offered_services if s['id'] == param), None)
		if match:
			command_msg = json.dumps({'Command':'OK', 'Params':json.dumps(match)})

			self.transport.write(bytes(command_msg, 'utf-8'), address)
			return

		global temporal_services
		match = next((s for s in temporal_services if s['id'] == param), None)
		if match:
			command_msg = json.dumps({'Command':'OK', 'Params':json.dumps(match)})

			self.transport.write(bytes(command_msg, 'utf-8'), address)
			return

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
	#os.close(0)
	#os.close(1)
	#os.close(2)
	logging.basicConfig(filename=conf.LOGGING_DIR+'polod.log', level=conf.LOGGING_LEVEL.upper(), format=conf.LOGGING_FORMAT)
	
	def start_multicast():
		reactor.listenMulticast(conf.PORT, Polo(), listenMultiple=True)
	reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)
	reactor.callWhenRunning(start_multicast)
	reactor.run()

