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
					print(s)
					if not verify.match(s['id']):
						fileservices.append(s)
			except ValueError:
				logging.debug(str.format("The file {0} does not have a valid JSON structures", conf.SERVICES_DIR+service))

		user_services[username] = user_services[username] + fileservices

def reload_services(sig, frame):
	signal.signal(signal.SIGUSR1, signal.SIG_IGN)
	global offered_services
	offered_services = []
	logging.info("Reloading services")
	
	servicefiles = [ f for f in listdir(conf.CONF_DIR + conf.SERVICES_DIR) if isfile(join('/etc/marcopolo/polo/services',f)) ]

	for service in servicefiles:
		try:
			with open(join(conf.CONF_DIR+conf.SERVICES_DIR, service), 'r', encoding='utf-8') as f:
				service = json.load(f)
				service["permanent"] = True
				offered_services.append(json.load(f))
		except ValueError:
			logging.debug(str.format("The file {0} does not have a valid JSON structures", conf.SERVICES_DIR+service))

	for user in user_services:
		reload_user_services(user)

	logging.info("Reloaded: Offering " + str(len(offered_services)) + " services")
	
	signal.signal(signal.SIGUSR1, reload_services)

def sanitize_path(path_str):
	return path.normpath("/"+path_str).lstrip('/')

def is_superuser(user):
	groups = [g.gr_name for g in grp.getgrall() if user.pw_name in g.gr_mem]
	gid = user.pw_gid
	groups.append(grp.getgrgid(gid).gr_name)
	return 'marcopolo' in groups or user.pw_uid == 0

def validate_user(uid):
	"""Returns a `pwd` structure if the uid is present in the passwd database.
	Otherwise `None` is returned
	
	:param string uid: The user identifier of the service

	"""

	if type(uid) != type(0):
		return False

	if uid < 0:
		return False
	try:
		user = pwd.getpwuid(uid)
	except KeyError:
		return False
	return user

class PoloBinding(DatagramProtocol):
	def startProtocol(self):
		pass

	def datagramReceived(self, datagram, address):
		"""
		Receives datagrams from bindings, and verifies the `Command` field.
		It emits a response based on the value (if necessary)
		"""
		datos = datagram.decode('utf-8')
		
		try:
			datos_dict = json.loads(datos)
		except ValueError:
			self.transport.write(json.dumps({"Error":"Malformed JSON"}).encode('utf-8'), address)
			logging.debug("Malformed JSON")
		
		if datos_dict.get("Command") is None:
			self.transport.write(json.dumps({"Error":"Missing command"}).encode('utf-8'), address)
			logging.debug("Missing command")
			return
		command = datos_dict["Command"];
		if command == 'Register':
			args = datos_dict.get("Args", {})
			self.publish_service(address,
								args.get("service", ''), 
								args.get("uid", -1),
								multicast_groups=args.get("multicast_groups", set()),
								permanent=args.get("permanent", False),
								root=args.get("root", False))
		elif command == 'Unpublish':
			args = datos_dict.get("Args", {})
			self.unpublish_service(address,
									args.get("service", ''),
									args.get("uid", -1),
									multicast_groups=args.get("multicast_groups", set()),
									delete_file=args.get("delete_file", False)
									)
			
		
		#If any of the previous conditions is satisfied, the request is considered malformed
		self.transport.write(self.write_error("Malformed request. Commands missing").encode('utf-8'), address)
		
	def write_error(self, error):
		"""
		Creates an `Error` return value
		"""

		return json.dumps({"Error": error})

	def publish_service(self, address, service, uid, multicast_groups=set(), permanent=False, root=False):
		"""
		Registers a service during execution time.
		
		:param string service: Indicates the unique identifier of the service.
		
			If `root` is true, the published service will have the same identifier as the value of the parameter. Otherwise, the name of the user will be prepended (`<user>:<service>`).
		
		:param set multicast_groups: Indicates the groups where the service shall be published.
		
			Note that the groups must be defined in the polo.conf file, or otherwise the method will throw an exception.
		:param bool permanent: If set to true a file will be created and the service will be permanently offered until the file is deleted.
		
		:param bool root: Stores the file in the marcopolo configuration directory.
		
			This feature is only available to privileged users, by default root and users in the marcopolo group.
		"""
		
		error = False # Python does not allow throwing an exception insided an exception, so we use a flag
		
		#Verification of services
		if type(service) != type(''):
			error=True
			return
		
		#The service must be something larger than 1 character
		if service is None or len(service) < 1:
			error = True

		if error:
			self.transport.write(self.write_error("The name of the service %s is invalid" % service).encode('utf-8'), address)
			return
		
		error = False
		faulty_ip = ''
		#The IP addresses must be represented in valid dot notation and belong to the range 224-239
		for ip in multicast_groups:
			#The IP must be a string
			if type(ip) != type(''):
				error = True
				faulty_ip = ip
				break
			
			#Instead of parsing we ask the socket module
			try:
				socket.inet_aton(ip)
			except socket.error:
				error = True
				faulty_ip = ip
				break
			
			try:
				first_byte = int(re.search("\d{3}", ip).group(0))
				if first_byte < 224 or first_byte > 239:
					error = True
					faulty_ip = ip
			except (AttributeError, ValueError):
				error = True
				faulty_ip = ip
				break

		if error:
			self.transport.write(self.write_error("Invalid multicast group address '%s'" % str(faulty_ip)).encode('utf-8'), address)
			return
		
		if type(permanent) is not bool:
			self.transport.write(self.write_error("permanent must be boolean").encode('utf-8'), address)
			return
		
		if type(root) is not bool:
			return self.transport.write(self.write_error("root must be boolean").encode('utf-8'), address)

		#UID verification
		if validate_user(uid) is None:
			self.transport.write(self.write_error("wrong user").encode('utf-8'), address)
			return
		
		
		#Final entry with all service parameters
		service_dict = {}
		service_dict["id"] = service

		#Root service
		if root is True:
			if service in [s['id'] for s in offered_services]:
				self.transport.write(self.write_error("Service %s already exists" % service).encode('utf-8'), address)
				return

			#Only root or members of the `marcopolo` group can publish root services
			if not is_superuser(user):
				self.transport.write(self.write_error("Permission denied").encode('utf-8'), address)
				return
			
			if permanent is True:

				services_dir = path.join(conf.CONF_DIR, conf.SERVICES_DIR)
				if not path.exists(services_dir):
					makedirs(services_dir)
					os.chown(services_dir, 0, grp.getgrnam(name).gr_gid)

				service_file = sanitize_path(service)
				if path.isfile(path.join(services_dir, service_file)):
					self.transport.write(self.write_error("Service %s already exists" % service).encode('utf-8'), address)
					return

				try:
					f = open(path.join(services_dir, service_file), 'w')
					f.write(json.dumps(service_dict))
					os.fchown(f.fileno(), user.pw_uid, user.pw_gid)
					f.close()
				except Exception as e:
					print(e)
					self.transport.write(self.write_error("Could not write file").encode('utf-8'), address)
					return
			
			offered_services.append({"id":service, "permanent":permanent})
			self.transport.write(json.dumps({"OK":service}).encode('utf-8'), address)
			return

		
		if user_services.get(user.pw_name, None):
			if service in [s['id'] for s in  user_services[user.pw_name]]:
				self.transport.write(self.write_error("Service already exists").encode('utf-8'), address)
				return

		folder = user.pw_dir
		deploy_folder = path.join(folder, conf.POLO_USER_DIR)
		
		if permanent is True:
			if not path.exists(deploy_folder):
				makedirs(deploy_folder)
				os.chown(deploy_folder, user.pw_uid, user.pw_gid)
			
			service_file = sanitize_path(service)
			if path.isfile(path.join(deploy_folder, service_file)):
				self.transport.write(self.write_error("Service already exists").encode('utf-8'), address)
				return
			
			try:
				f = open(path.join(deploy_folder, service_file), 'w')
				f.write(json.dumps(service_dict))
				os.fchown(f.fileno(), user.pw_uid, user.pw_gid)
				f.close()
			except Exception as e:
				logging.debug(e)
				self.transport.write(self.write_error("Could not write service file").encode('utf-8'), address)
				return

		if user_services.get(user.pw_name, None) is None:
			user_services[user.pw_name] = []

		user_services[user.pw_name].append({"id":service, "permanent":permanent})

		self.transport.write(json.dumps({"OK":user.pw_name+":"+service}).encode('utf-8'), address)

	def unpublish_service(self, service, uid, multicast_groups=[], delete_file=False):
		#Determine whether it is a root or a user service

		user = validate_user(uid)

		if user is None:
			self.transport.write(self.write_error("wrong user").encode('utf-8'), address)
			return
		
		if verify.match(service):
			#user service
			try:
				user, service_name = verify.match(service).groups()
			except (IndexError, ValueError):
				return
			if user_services.get(user, None) is not None:
				match = next((s for s in user_services[user] if s['id'] == service_name), None)
				if match:
					is_permanent = match.get("permanent", False)
					
					if delete_file and is_permanent:
						folder = user.pw_dir
						deploy_folder = path.join(folder, conf.POLO_USER_DIR)
						if path.exists(deploy_folder) and isfile(path.join(deploy_folder, service_name)):
							try:
								os.remove(path.join(deploy_folder, service_name))
							except Exception as e:
								print(e)
						else:
							self.transport.write(self.write_error("Could not find service file").encode('utf-8'), address)
				
					user_services[user].remove(match)
					self.transport.write(json.dumps({"OK":user.pw_name+":"+service}).encode('utf-8'), address)
					return
				else:
					self.transport.write(self.write_error("Could not find service").encode('utf-8'), address)
					return
			else:
				self.transport.write(self.write_error("Could not find service").encode('utf-8'), address)
				return
		else:
			pass #user services
		

	def remove_service(self, service_id):
		pass

class Polo(DatagramProtocol):
	"""
	Twisted-inherited class in charge of receiving Marco requests on the defined multicast groups
	"""
	
	def startProtocol(self):
		"""
		Operations to be performed before starting to listen
		"""
		logging.info("Starting service polod")
		global offered_services

		#List all files in the service directory
		servicefiles = [ f for f in listdir(conf.CONF_DIR + conf.SERVICES_DIR) if isfile(join('/etc/marcopolo/polo/services',f)) ]
		
		for service in servicefiles:
			try:
			    with open(join(conf.CONF_DIR+conf.SERVICES_DIR, service), 'r', encoding='utf-8') as f:
			        s = json.load(f)
			        s["permanent"] = True
			        if not verify.match(s['id']):
			        	offered_services.append(s)
			except ValueError:
			    logging.debug(str.format("The file {0} does not have a valid JSON structures", conf.SERVICES_DIR+service))

		if conf.DEBUG:
			for s in offered_services:
				print(s['id'])
		logging.info("Offering " + str(len(offered_services)) + " services")

		
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
		msg = json_msg.encode('utf-8')

		self.transport.write(msg, address)
	
	def response_services(self, command, param, address):
		global offered_services
		response_services = []
		for service in offered_services:
			response_services.append(service['id'])

		self.transport.write(json.dumps({'Command': 'OK', 'Services': response_services}).encode('utf-8'), address)
	
	def response_request_for_user(self, user, service, address):
		if user_services.get(user, None) is None:
			reload_user_services(user)

		match = next((s for s in user_services.get(user, []) if s['id'] == service), None)
		print(user_services.get(user, None))
		print(user)
		print(user_services)
		if match:
			print("Found")
			command_msg = json.dumps({'Command':'OK', 'Params': json.dumps(match)})
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

		global offered_services
		match = next((s for s in offered_services if s['id'] == param), None)
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
	#os.close(0)
	#os.close(1)
	#os.close(2)
	logging.basicConfig(filename=conf.LOGGING_DIR+'polod.log', level=conf.LOGGING_LEVEL.upper(), format=conf.LOGGING_FORMAT)
	
	def start_multicast():
		reactor.listenMulticast(conf.PORT, Polo(), listenMultiple=False)
	
	def start_binding():
		reactor.listenUDP(conf.POLO_BINDING_PORT, PoloBinding(), interface="127.0.0.1") #, 

	reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)
	reactor.callWhenRunning(start_multicast)
	reactor.callWhenRunning(start_binding)
	reactor.run()

