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

__author__ = 'Diego Martín'

offered_services = []
user_services = {}

verify = re.compile('^([\d\w]+):([\d\w]+)$')

def reload_user_services(user):
	try:
		user = pwd.getpwnam(user)
	except KeyError:
		return
	
	if path.exists(user.pw_dir):
		polo_dir = path.join(user.pw_dir,conf.POLO_USER_DIR)
		username = user.pw_name
		user_services[username] = [service for service in user_services.get(username, []) if service[1] == False]
		
		servicefiles = [ join(polo_dir, f) for f in listdir(polo_dir) if isfile(join(polo_dir,f)) ]
		
		fileservices = []
		for service in servicefiles:
			try:
				with open(service, 'r', encoding='utf-8') as f:
					s = json.load(f)
					s["permanent"] = True
					if not verify.match(s['id']):
						fileservices.append(s)

			except ValueError:
				logging.debug(str.format("The file {0} does not have a valid JSON structures", conf.SERVICES_DIR+service))

		user_services[username] = user_services[username] + fileservices

def reload_services(sig, frame):
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
		reload_user_services(user)

	logging.info("Reloaded: Offering " + str(len(offered_services)) + " services")
	
	signal.signal(signal.SIGUSR1, reload_services)

def sanitize_path(path_str):
	return path.normpath("/"+path_str).lstrip('/')


class Polo(DatagramProtocol):

	def __init__(self, offered_services, user_services):
		super(Polo).__init__()
		self.offered_services = offered_services
		self.user_services = user_services

	"""
	Twisted-inherited class in charge of receiving Marco requests on the defined multicast groups
	"""
	
	def startProtocol(self):
		"""
		Operations to be performed before starting to listen
		"""
		logging.info("Starting service polod")
		#global offered_services

		#List all files in the service directory
		servicefiles = [ f for f in listdir(conf.CONF_DIR + conf.SERVICES_DIR) if isfile(join('/etc/marcopolo/polo/services',f)) ]
		
		for service in servicefiles:
			try:
			    with open(join(conf.CONF_DIR+conf.SERVICES_DIR, service), 'r', encoding='utf-8') as f:
			        s = json.load(f)
			        s["permanent"] = True
			        if not verify.match(s['id']):
			        	self.offered_services.append(s)
			except ValueError:
			    logging.debug(str.format("The file {0} does not have a valid JSON structures", conf.SERVICES_DIR+service))

		if conf.DEBUG:
			for s in self.offered_services:
				print(s['id'])
		logging.info("Offering " + str(len(self.offered_services)) + " services")

		
		self.attempts = 0
		def handler(arg):
			#TODO: http://stackoverflow.com/questions/808560/how-to-detect-the-physical-connected-state-of-a-network-cable-connector
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
		#global offered_services
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
			logging.info("Unknown command: " + datagram.decode('utf-8'))

	def polo(self, command, address):
		"""
		Replies to `Polo` requests
		"""
		#global offered_services
		response_dict = {}
		response_dict["Command"] = "Polo"
		response_dict["Params"] = conf.POLO_PARAMS
		
		json_msg = json.dumps(response_dict, separators=(',',':'))
		msg = json_msg.encode('utf-8')

		self.transport.write(msg, address)
	
	def response_services(self, command, param, address):
		"""
		Replies to `Services` requests
		"""
		#TODO: User services

		#global offered_services
		response_services = []
		for service in self.offered_services:
			response_services.append(service['id'])

		self.transport.write(json.dumps({'Command': 'OK', 'Services': response_services}).encode('utf-8'), address)
	
	def response_request_for_user(self, user, service, address):
		if self.user_services.get(user, None) is None:
			reload_user_services(user)

		match = next((s for s in self.user_services.get(user, []) if s['id'] == service), None)
		print(self.user_services.get(user, None))
		print(user)
		print(self.user_services)
		if match:
			command_msg = json.dumps({'Command':'OK', 'Params': match.get("Params", {})})
			self.transport.write(command_msg.encode('utf-8'), address)
			return

	def response_request_for(self, command, param, address):

		if verify.match(param):
			try:
				user, service = verify.match(param).groups()
			except (IndexError, ValueError):
				return
			self.response_request_for_user(user, service, address)
			return

		#global offered_services
		match = next((s for s in self.offered_services if s['id'] == param), None)
		if match:
			command_msg = json.dumps({'Command':'OK', 'Params':json.dumps(match)})

			self.transport.write(command_msg.encode('utf-8'), address)
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
	
	logging.basicConfig(filename=conf.LOGGING_DIR+'polod.log', level=conf.LOGGING_LEVEL.upper(), format=conf.LOGGING_FORMAT)
	
	def start_multicast():
		p = Polo(offered_services, user_services)
		reactor.listenMulticast(conf.PORT, p, listenMultiple=False)
	
	def start_binding():
		p = PoloBinding(offered_services, user_services)
		reactor.listenUDP(conf.POLO_BINDING_PORT, p, interface="127.0.0.1")

	reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)
	reactor.callWhenRunning(start_multicast)
	reactor.callWhenRunning(start_binding)
	reactor.run()

