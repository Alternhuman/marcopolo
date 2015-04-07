#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, defer
from marco_conf import utils, conf

import socket, sys, json #time, string were necessary
from io import StringIO


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

		self.nodes = set()

	def __del__(self):
		self.socket_bcast.close()
		self.socket_mcast.close()
		self.socket_ucast.close()

	def discover(self):
		discover_msg = bytes(json.dumps({'Command': 'Discover'}), 'utf-8')
		self.socket_mcast.sendto(discover_msg, (conf.MULTICAST_ADDR, conf.PORT))

		while True:
			try:
				msg, address = self.socket_mcast.recvfrom(4096)
			except socket.timeout:
				break

			json_data = json.load(StringIO(msg.decode('utf-8')))

			if json_data["Command"] == "Polo":

				n = utils.Node()
				n.address = address
				n.multicast_group = str(json_data["multicast_group"])
				n.services = json_data["services"]

				self.nodes.add(n)

		if conf.DEBUG:
			for node in self.nodes:
				print(str.format("There's a node at {0} joining the multicast group {1} with the services: ", node.address, node.multicast_group),file=sys.stderr)
				for service in n.services:
					print(str.format("{0}. Version: {1} ", service["id"], service["version"]))
		
		import copy
		return copy.copy(self.nodes)

	def services(self, addr, port=conf.PORT):
		"""
		Searches for the services available in a certain node identified by its address
		@param addr Address of the node
		@port UDP port of the Polo instance. If not given, the default is the port in the conffile
		@return An array with all detected nodes
		"""

		#Validation of addr
		if addr == None or addr == '':
			raise InvalidAddrException

		try:
			socket.gethostbyname(addr) # Gethostbyname throws a gaierror if neither a valid IP address or DNS name is passed. Easiest way to perform both checks
		except socket.gaierror:
			raise InvalidAddrException

		discover_msg = bytes(json.dumps({'command': 'Services'}), 'utf-8')
		self.socket_mcast.sendto(discover_msg, (addr, conf.PORT))

		while True:
			try:
				msg, address = self.socket_mcast.recvfrom(4096)
			except socket.timeout:
				break

			json_data = json.load(StringIO(msg.decode('utf-8')))

			n = utils.Node()
			n.address = address
			n.multicast_group = str(json_data["multicast_group"])
			n.services = json.loads(json_data["services"])
			self.nodes.add(n)

			if conf.DEBUG:
				for node in n:
					print("There's a node at {0} joining the multicast group")


	def request_service(self, service, node=None):
		"""
		Request all nodes offering a certain service or the details for one single node
		@service Name of the requested service
		@node Address or name of the desired node
		@return an array with all the available nodes
		"""
		nodes = set()

		command_msg = bytes(json.dumps({'Command':'Request-for', 'Params':service}), 'utf-8')

		if not isinstance(service, str):
			raise InvalidServiceName

		if(node): ##If node is defined only that node is requested
			
			try: #Validation
				socket.gethostbyname(addr) # Gethostbyname throws a gaierror if neither a valid IP address or DNS name is passed. Easiest way to perform both checks
			except socket.gaierror:
				raise InvalidAddrException

			self.socket_ucast.sendto(command_msg, node)

			try:
			    response = self.socket_ucast.recv(4096)
			except socket.timeout:
			    return


			n = utils.Node()
			n.address = node
			n.services = []
			n.services.add(json.load(StringIO(response.decode('utf-8'))))

			nodes.add(n)

		else:
			#Multicast request
			self.socket_mcast.sendto(command_msg, (conf.MULTICAST_ADDR, conf.PORT))

			while True:
				try:
					response, address = self.socket_mcast.recvfrom(4096)
				except socket.timeout:
					break

			response = json.load(StringIO(response.decode('utf-8')))

			if response["Command"] == 'OK':

				n = utils.Node()
				n.address = address
				n.services = []
				n.services.append(json.load(StringIO(response["Params"])))

				nodes.add(n)

		return nodes

#Own exceptions. Just for the name
class InvalidAddrException(Exception):
    pass

class InvalidServiceName(Exception):
	pass


class MarcoBinding(DatagramProtocol):
	"""
	Twisted class for an asynchronous socket server
	"""

	def __init__(self):
		self.marco = Marco() #Own instance of Marco

	def datagramReceived(self, data, address):
		
		nodes_with_service = self.marco.request_service(data.decode('utf-8'))
		nodes = []
		
		for service in nodes_with_service:
			nodes.append(service.address)
		print(nodes)
		
		self.transport.write(bytes(json.dumps(nodes), 'utf-8'), address)

	def stopService():
		del self.marco


@defer.inlineCallbacks
def graceful_shutdown():
    yield server.stopService()

if __name__ == "__main__":
	server = reactor.listenUDP(1338, MarcoBinding(), interface='127.0.1.1')
	reactor.run()
	reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)