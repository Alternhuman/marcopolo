#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, defer

import socket, sys, json, logging, os, signal #time, string were necessary
from os import path, makedirs, listdir
from copy import copy

sys.path.append('/opt/marcopolo/')
from marco_conf import utils, conf

class Marco:
	def __init__(self):
		"""
		Initializes all the data structures and sockets, setting timeouts
		"""
		error = False
		try:
			self.socket_bcast = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
			self.socket_bcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			self.socket_bcast.settimeout(conf.TIMEOUT/1000.0) #https://docs.python.org/2/library/socket.html#socket.socket.settimeout
			
			self.socket_mcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			self.socket_mcast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2) #If not otherwise specified, multicast datagrams are sent with a default value of 1, to prevent them to be forwarded beyond the local network. To change the TTL to the value you desire (from 0 to 255)
			self.socket_mcast.settimeout(conf.TIMEOUT/1000.0) #https://docs.python.org/2/library/socket.html#socket.socket.settimeout
			
			self.socket_ucast = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
			self.socket_ucast.settimeout(conf.TIMEOUT/1000.0) #https://docs.python.org/2/library/socket.html#socket.socket.settimeout
			#TODO binding exception
			self.nodes = set()
		
		except Exception as e:
			error = True

		if error:
			raise MarcoException("Error in initialization")

	def __del__(self):
		"""
		Destroys all socket connections prior deleting
		"""
		self.socket_bcast.close()
		self.socket_mcast.close()
		self.socket_ucast.close()

	def marco(self, max_nodes=None, exclude=[], timeout=None, retries=0):
		"""
		Sends a `marco` message to all nodes, which reply with a Polo message. Upon receiving all responses (those arriving before the timeout), a collection of the response information is returned.
    	
    	:param int max_nodes: Maximum number of nodes to be returned. If set to `None`, no limit is applied.

	    :param list exclude: List of nodes to be excluded from the returned ValueError.

	    :param int timeout: If set, overrides the default timeout value.

	    :param int retries: If set to a value greater than 0, retries the *retries* times if the first attempt is unsuccessful

	    :returns: A list of all responding nodes.
		"""
		counter = 0
		
		#Python 2 and 3 compatibility in byte encoding
		if sys.version_info[0] < 3:
			discover_msg = bytes(json.dumps({'Command': 'Marco'}).encode('utf-8'))
		else:
			discover_msg = bytes(json.dumps({'Command': 'Marco'}), 'utf-8')

		#Send to group IP
		if -1 == self.socket_mcast.sendto(discover_msg, (conf.MULTICAST_ADDR, conf.PORT)):
			raise MarcoException("Error on multicast sending")
		
		#Timeout check
		error = None
		if timeout:
			try:
				self.socket_mcast.settimeout(int(timeout)/1000.0)
			except ValueError:
				error = True
			if error:
				raise MarcoException("Invalid timeout value")

		#max_nodes check
		nodes = set()
		error=None
		if max_nodes:
			try:
				max_nodes = int(max_nodes)
			except ValueError:
				error = True
			
			if error:
				raise MarcoException("Invalid max_nodes value")

		
		#exclude check
		if exclude and not (isinstance(exclude, (list, tuple))):
			raise MarcoException("Invalud exclude value. Must be instance of array or set()")
		
		error = None
		if retries:
			try:
				retries = int(retries)
				attempts = 0
			except ValueError:
				error = True

			if error:
				raise MarcoException("Invalid retries value")
		else:
			attempts = 0

		stop = False
		while attempts < retries + 1  and not stop:

			#Looping until timeout is raised or max_nodes is reached
			while True:
				try:
					msg, address = self.socket_mcast.recvfrom(conf.FRAME_SIZE)
				except socket.timeout:
					attempts += 1
					break
				
				error = None
				
				try:
					json_data = json.loads(msg.decode('utf-8'))
				except ValueError:
					error = True
				
				if error:
					raise MarcoException("Malformed message")

				if json_data.get("Command", "") == "Polo" and address not in exclude:

					n = utils.Node()
					n.address = address[0] # Address includes both IP and port. The latter is rather irrelevant
					n.params = json_data.get("Params", {})
					nodes.add(n)
					stop = True
				
				if max_nodes:
					counter +=1
					if counter >= max_nodes:
						stop = True
						break

		if conf.DEBUG:
			debstr = ""
			for node in nodes:
				debstr = str.format("There's a node at {0} joining the multicast group {1} with the services: ", node.address, node.multicast_group)
				
				for service in n.services:
					debstr += str.format("{0}. Version: {1} ", service["id"], service["version"])

			logging.debug(debstr)
		
		
		return copy(nodes)

	def services(self, addr, timeout=None, retries=0):
		"""
		Searches for the services available in a certain node identified by its address
		
		:param string addr: Address of the node
		
		:param int port: UDP port of the Polo instance. If not given, the default is the port in the conffile
		
		:returns: An array with all detected nodes
		"""

		#Validation of addr
		if addr == None or addr == '':
			logging.debug('Address cannot be empty: %s', addr)
			raise MarcoException('Address cannot be empty: %s', addr)
		
		error = None
		try:
			socket.gethostbyname(addr) # Gethostbyname throws a gaierror if neither a valid IP address or DNS name is passed. Easiest way to perform both checks
		except socket.gaierror:
			logging.debug('Invalid address or DNS name: %s', addr)
			error = True
		
		if error:
			raise MarcoException('Invalid address or DNS name: %s', addr)

		error = None

		if timeout:
			try:
				self.socket_mcast.settimeout(int(timeout)/1000.0)
			except ValueError:
				error = True
			if error:
				raise MarcoException("Invalid timeout value")

		discover_msg = bytes(json.dumps({'Command': 'Services'}))
		
		if -1 == self.socket_ucast.sendto(discover_msg, (addr, conf.PORT)):
			raise MarcoException("Error on multicast sending")

		try:
			msg, address = self.socket_ucast.recvfrom(conf.FRAME_SIZE)
		
		except socket.timeout:
			pass

		try:
			json_data = json.loads(msg.decode('utf-8'))
		except ValueError:
			raise MarcoException("Error in response")
		
		if conf.DEBUG:
			logging.debug("There's a node at {0} joining the multicast group", address)

		n = utils.Node()
		n.address = address[0]
		n.services = json_data.get("Params", [])
		
		return n


	def request_for(self, service, node=None, max_nodes=None, exclude=[], timeout=None):
		"""
		Request all nodes offering a certain service or the details for one single node
		
		:param string service: Name of the requested service
		
		:param string node: Address or name of the desired node
		
		:returns: an array with all the available nodes
		"""
		
		nodes = set()
		if sys.version_info[0] < 3:
			command_msg	= bytes(json.dumps({'Command':'Request-For', 'Params':service}).encode('utf-8'))
		else:
			command_msg = bytes(json.dumps({'Command':'Request-For', 'Params':service}), 'utf-8')

		if not isinstance(service, str):
			logging.info('Bad formatted request')
			raise MarcoException('Bad formatted request')

		if(node): ##If node is defined only that node is requested TODO: Really necessary?
			if timeout:
				try:
					self.socket_ucast.settimeout(int(timeout)/1000.0)
				except ValueError:
					error = True
				if error:
					raise MarcoException("Invalid timeout value")
			
			try: #Validation
				socket.gethostbyname(node) # Gethostbyname throws a gaierror if neither a valid IP address or DNS name is passed. Easiest way to perform both checks
			except socket.gaierror:
				logging.info('Bad address')
				raise MarcoException('Bad address')

			if -1 == self.socket_ucast.sendto(command_msg, node):
				raise MarcoException("Error on multicast sending")

			try:
			    response = self.socket_ucast.recv(conf.FRAME_SIZE)
			except socket.timeout:
			    return

			n = utils.Node()
			n.address = node
			n.services = []

			try:
				n.services.append(json.loads(response))
			except ValueError:
				raise MarcoException("Error on response")
			nodes.append(n)
			return nodes
		else:
			#Multicast request
			error = None
			if timeout:
				try:
					self.socket_mcast.settimeout(int(timeout)/1000.0)
				except ValueError:
					error = True
				if error:
					raise MarcoException("Invalid timeout value")

			if max_nodes:
				try:
					max_nodes = int(max_nodes)
				except ValueError:
					error = True
			
				if error:
					raise MarcoException("Invalid max_nodes value")

			if exclude and not (isinstance(exclude, (list, tuple))):
				raise MarcoException("Invalud exclude value. Must be instance of array or set()")

			
			self.socket_mcast.sendto(command_msg, (conf.MULTICAST_ADDR, conf.PORT))
			counter = 0
			while True:
				try:
					response, address = self.socket_mcast.recvfrom(conf.FRAME_SIZE)
				except socket.timeout:
					break

				try:
					response = json.loads(response.decode('utf-8'))
				except ValueError:
					continue
				if response.get("Command", "") == 'OK' and address not in exclude:

					n = utils.Node()
					#print(address[0])
					n.address = address[0]
					n.params = response.get("Params", {})
					#n.services = []
					#n.services.append(json.loads(response["Params"])) ##TODO

					nodes.add(n)
				if max_nodes:
					counter +=1
					if counter >= max_nodes:
						break
			return nodes

	def request_one(self, service, max_nodes=None, exclude=[], timeout=None):
		return self.request_for(service, max_nodes=1, exclude=exclude, timeout=timeout)


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
		nodes = self.marco.request_for(command["Params"])

		if len(nodes) > 0:
			self.transport.write(bytes(json.dumps([{"Address": n.address, "Params": n.services} for n in nodes]).encode('utf-8')), address)
		else:
			self.transport.write(bytes(json.dumps([]), 'utf-8'), address)
	def marcoInThread(self, address, command):

		nodes = self.marco.marco(max_nodes=command.get("max_nodes", None), 
								 exclude=command.get("exclude", []),
								 timeout=command.get("timeout", None)
								 )
		self.transport.write(bytes(json.dumps([n.address for n in nodes]).encode('utf-8')), address)

	def servicesInThread(self, command, address):
		services = self.marco.services(addr=command.get("node", None), 
									   timeout=command.get("timeout", 0)
									   )
		
		self.transport.write(bytes(json.dumps([service for service in services]).encode('utf-8')), address)
	
	def datagramReceived(self, data, address):
		try:
			command = json.loads(data.decode('utf-8'))
		except ValueError:
			return
		if command.get("Command", None) == None:
			self.transport.write(bytes(json.dumps({"Error": True}).encode('utf-8')), address)

		else:
			if command["Command"] == "Marco":
				reactor.callInThread(self.marcoInThread, address, command)

			elif command["Command"] == "Request-for" or command["Command"] == "Request-For":
				reactor.callInThread(self.requestForInThread, command, address)

			elif command["Command"] == "Services":
				reactor.callInThread(self.servicesInThread, command, address)
			
			else:
				self.transport.write(bytes(json.dumps({"Error": True}).encode('utf-8')), address)
		

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


	logging.basicConfig(filename=conf.LOGGING_DIR+'marcod.log', level=conf.LOGGING_LEVEL.upper(), format=conf.LOGGING_FORMAT)
	server = reactor.listenUDP(conf.MARCOPORT, MarcoBinding(), interface='127.0.1.1')
	reactor.run()
