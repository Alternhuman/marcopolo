#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, defer

import socket, sys, json, logging, os, signal #time, string were necessary
from os import path, makedirs, listdir
import copy

sys.path.append('/opt/marcopolo/')
from marco_conf import utils, conf

class Marco:
	def __init__(self):
		self.socket_bcast = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
		self.socket_bcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.socket_bcast.settimeout(conf.TIMEOUT/1000.0) #https://docs.python.org/2/library/socket.html#socket.socket.settimeout
		self.socket_bcast.bind(('',0))

		self.socket_mcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.socket_mcast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2) #If not otherwise specified, multicast datagrams are sent with a default value of 1, to prevent them to be forwarded beyond the local network. To change the TTL to the value you desire (from 0 to 255)
		self.socket_mcast.bind(('', 0)) # Usaremos el mismo socket para recibir los datos de cada nodo
		self.socket_mcast.settimeout(conf.TIMEOUT/1000.0) #https://docs.python.org/2/library/socket.html#socket.socket.settimeout

		self.socket_ucast = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
		self.socket_ucast.settimeout(conf.TIMEOUT/1000.0) #https://docs.python.org/2/library/socket.html#socket.socket.settimeout
		self.socket_ucast.bind(('',0))
		#TODO binding exception
		self.nodes = set()

	def __del__(self):
		self.socket_bcast.close()
		self.socket_mcast.close()
		self.socket_ucast.close()

	def discover(self):
		if sys.version_info[0] < 3:
			discover_msg = bytes(json.dumps({'Command': 'Marco'}).encode('utf-8'))
		else:
			discover_msg = bytes(json.dumps({'Command': 'Marco'}), 'utf-8')

		if -1 == self.socket_mcast.sendto(discover_msg, (conf.MULTICAST_ADDR, conf.PORT)):
			raise MarcoException("Error on multicast sending")

		nodos = set()
		while True:
			try:
				msg, address = self.socket_mcast.recvfrom(4096)
			except socket.timeout:
				break
			error = None
			
			try:
				json_data = json.loads(msg.decode('utf-8'))
			except ValueError:
				error = True
			
			if error:
				raise MarcoException("Malformed message")

			if json_data["Command"] == "Polo":

				n = utils.Node()
				n.address = address
				#n.multicast_group = str(json_data["multicast_group"])
				#n.services = json_data["services"]

				nodos.add(n)

		if conf.DEBUG:
			debstr = ""
			for node in nodos:
				debstr = str.format("There's a node at {0} joining the multicast group {1} with the services: ", node.address, node.multicast_group)
				
				for service in n.services:
					debstr += str.format("{0}. Version: {1} ", service["id"], service["version"])

			logging.debug(debstr)
		
		
		return copy.copy(nodos)

	def services(self, addr, port=conf.PORT):
		"""
		Searches for the services available in a certain node identified by its address
		@param addr Address of the node
		@port UDP port of the Polo instance. If not given, the default is the port in the conffile
		@return An array with all detected nodes
		"""

		#Validation of addr
		if addr == None or addr == '':
			logging.debug('Address cannot be empty: %s', addr)
			raise MarcoException('Address cannot be empty: %s', addr)

		try:
			socket.gethostbyname(addr) # Gethostbyname throws a gaierror if neither a valid IP address or DNS name is passed. Easiest way to perform both checks
		except socket.gaierror:
			logging.debug('Invalid address or DNS name: %s', addr)
			raise MarcoException('Invalid address or DNS name: %s', addr)

		discover_msg = bytes(json.dumps({'Command': 'Services'}))
		if -1 == self.socket_mcast.sendto(discover_msg, (addr, conf.PORT)):
			raise MarcoException("Error on multicast sending")

		try:
			msg, address = self.socket_mcast.recvfrom(4096)
		except socket.timeout:
			pass

		try:
			json_data = json.loads(msg.decode('utf-8'))
		except ValueError:
			return
		
		if conf.DEBUG:
			logging.debug("There's a node at {0} joining the multicast group", address)

		n = utils.Node()
		n.address = address
		n.multicast_group = str(json_data["multicast_group"])
		n.services = json.loads(json_data["services"]) ##TODO: Is a reparse really necessary?
		
		return n


	def request_service(self, service, node=None):
		"""
		Request all nodes offering a certain service or the details for one single node
		@service Name of the requested service
		@node Address or name of the desired node
		@return an array with all the available nodes
		"""
		nodes = set()

		command_msg = bytes(json.dumps({'Command':'Request-For', 'Params':service}))

		if not isinstance(service, str):
			logging.info('Bad formatted request')
			raise MarcoException('Bad formatted request')

		if(node): ##If node is defined only that node is requested
			
			try: #Validation
				socket.gethostbyname(node) # Gethostbyname throws a gaierror if neither a valid IP address or DNS name is passed. Easiest way to perform both checks
			except socket.gaierror:
				logging.info('Bad address')
				raise MarcoException('Bad address')

			if -1 == self.socket_ucast.sendto(command_msg, node):
				raise MarcoException("Error on multicast sending")

			try:
			    response = self.socket_ucast.recv(4096)
			except socket.timeout:
			    return

			n = utils.Node()
			n.address = node
			n.services = []
			
			try:
				n.services.add(json.loads(response.decode('utf-8')))
			except ValueError:
				raise MarcoException("Error on response")
			nodes.add(n)
			return nodes
		else:
			#Multicast request
			self.socket_mcast.sendto(command_msg, (conf.MULTICAST_ADDR, conf.PORT))

			while True:
				try:
					response, address = self.socket_mcast.recvfrom(4096)
				except socket.timeout:
					break

				try:
					response = json.loads(response.decode('utf-8'))
				except ValueError:
					continue
				if response["Command"] == 'OK':

					n = utils.Node()
					n.address = address
					n.services = []
					n.services.append(json.loads(response["Params"])) ##TODO

					nodes.add(n)
			return nodes
		return nodes

#Own exceptions. Just for the name
#class InvalidAddrException(Exception):
#    pass

#class InvalidServiceName(Exception):
#	pass

class MarcoException(Exception):
	pass


class MarcoBinding(DatagramProtocol):
	"""
	Twisted class for an asynchronous socket server
	"""
	def __init__(self):
		self.marco = Marco() #Own instance of Marco
		logging.info("Starting service marcod")

	def requestForInThread(self, command, address):
		nodes = self.marco.request_service(command["Params"])
		self.transport.write(bytes(json.dumps([{"Address": n.address, "Params": n.services} for n in nodes]), 'utf-8'), address)

	def marcoInThread(self, address):
		nodes = self.marco.discover()
		self.transport.write(bytes(json.dumps([n.address[0] for n in nodes]), 'utf-8'), address)

	def servicesInThread(self, command, address):
		services = self.marco.services(command["Params"])
		self.transport.write(bytes(json.dumps([service for service in services]), 'utf-8'), address)
	
	def datagramReceived(self, data, address):
		
		try:
			command = json.loads(data.decode('utf-8'))
		except ValueError:
			return
		if command["Command"] == "Marco":
			reactor.callInThread(self.marcoInThread, address)

		elif command["Command"] == "Request-for" or command["Command"] == "Request-For":
			reactor.callInThread(self.requestForInThread, command, address)

		elif command["Command"] == "Services":
			reactor.callInThread(self.servicesInThread, command, address)
		
		else:
			self.transport.write(bytes(json.dumps({"Error": True}), 'utf-8'), address)
		

@defer.inlineCallbacks
def graceful_shutdown():
	yield logging.info('Stopping service marcod')

if __name__ == "__main__":
	signal.signal(signal.SIGHUP, signal.SIG_IGN)
	
	pid = os.getpid()
	
	if not path.exists('/var/run/marcopolo'):
		makedirs('/var/run/marcopolo')
	
	f = open(conf.PIDFILE_MARCO, 'w')
	f.write(str(pid))
	f.close()

	#Closing std(in|out|err)
	#os.close(0)
	#os.close(1)
	#os.close(2)

	logging.basicConfig(filename=conf.LOGGING_DIR+'marcod.log', level=conf.LOGGING_LEVEL.upper(), format=conf.LOGGING_FORMAT)
	server = reactor.listenUDP(conf.MARCOPORT, MarcoBinding(), interface='127.0.1.1')
	reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)
	reactor.run()
