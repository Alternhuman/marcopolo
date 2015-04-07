#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

from os import listdir
from os.path import isfile, join
from io import StringIO
import sys, signal
import json

from marco_conf import conf

__author__ = 'Diego Martín'

class Polo(DatagramProtocol):
	def startProtocol(self):
		#self.transport.setTTL(2) Para salir más allá de la subred
		self.transport.joinGroup(conf.MULTICAST_ADDR)
		self.services = []

		servicefiles = [ f for f in listdir('/etc/marcopolo/polo/services') if isfile(join('/etc/marcopolo/polo/services',f)) ]
		
		for service in servicefiles:
			try:
			    with open(join(conf.SERVICES_DIR, service), 'r', encoding='utf-8') as f:
			        self.services.append(json.load(f))
			except ValueError:
			    print(str.format("El archivo {0} no cuenta con una estructura JSON válida", conf.SERVICES_DIR+service))

		for s in self.services:
		    print(s['id'])

		print("Ofreciendo " + str(len(self.services)) + " servicios")

	def datagramReceived(self, datagram, address):
		message_dict = json.load(StringIO(datagram.decode('utf-8')))
		command = message_dict["Command"]

		if command == 'Discover' or command == 'Marco':
			self.response_discover(command, address)
		elif command == 'Request-for':
			self.response_request_for(command, message_dict["Params"], address)
		elif command == 'Services':
			self.services(command, address)
		else:
			print("Unknown command", file=sys.stderr)

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

if __name__ == "__main__":
	#signal.signal(signal.SIGINT, sigint_handler)
	reactor.listenMulticast(conf.PORT, Polo(), listenMultiple=True)
	reactor.run()
