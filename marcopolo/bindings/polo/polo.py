#!/usr/bin/env python

import json, socket, sys, os
import socket, re # Address validation
sys.path.append('/opt/marcopolo/')

from marco_conf import conf
BINDING_PORT = conf.POLO_BINDING_PORT

TIMEOUT = 4000

def verify_parameters(service, multicast_groups):
	error = False
	if type(service) != type(''):
		raise PoloException("The name of the service %s is invalid" % service)

	if service is None or len(service) < 1:
		error = True

	if error:
		raise PoloException("The name of the service %s is invalid" % service)

	error = False
	faulty_ip = ''

	for ip in multicast_groups:
		if type(ip) != type(''):
			error = True
			faulty_ip = ip
			break
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
		raise PoloException("Invalid multicast group address '%s'" % str(faulty_ip))

class PoloException(Exception):
	pass

class Polo(object):
	def __init__(self):
		self.polo_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.polo_socket.settimeout(TIMEOUT/1000.0)

	def publish_service(self, service, multicast_groups=set(), permanent=False, root=False):
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
		#Verify user input
		error = False
		if type(service) != type(''):
			raise PoloException("The name of the service %s is invalid" % service)

		if service is None or len(service) < 1:
			error = True

		if error:
			raise PoloException("The name of the service %s is invalid" % service)
		
		error = False
		faulty_ip = ''

		for ip in multicast_groups:
			if type(ip) != type(''):
				error = True
				faulty_ip = ip
				break
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
			raise PoloException("Invalid multicast group address '%s'" % str(faulty_ip))

		if type(permanent) is not bool:
			raise PoloException("permanent must be boolean")

		if type(root) is not bool:
			raise PoloException("root must be boolean")
		
		message_dict = {}
		message_dict["Command"]= "Register"
		message_dict["Args"] = {"service": service, 
								"multicast_groups":[g for g in multicast_groups], 
								"permanent": permanent, 
								"root":root,
								"uid": os.geteuid()}
		
		error = False
		try:
			message_str = json.JSONEncoder(allow_nan=False).encode(message_dict) # https://docs.python.org/2/library/json.html#infinite-and-nan-number-values
		except Exception:
			error = True

		if error:
			raise PoloInternalException("Error in JSON Encoder")
		
		error = False
		try:
			unicode_msg = message_str.encode('utf-8')
		except UnicodeError:
			error = True
		
		if error:
			raise PoloInternalException("Error in codification")

		error = False
		try:
			if -1 == self.polo_socket.sendto(unicode_msg, ('127.0.0.1', BINDING_PORT)):
				error = True
		except Exception:
			error = True

		if error:
			raise PoloInternalException("Error during internal communication")

		error = False
		try:
			data, address = self.polo_socket.recvfrom(2048)
		except socket.timeout:
			error = True

		if error or data == -1:
			raise PoloInternalException("Error during internal communication")
		error = False
		
		try:
			data_dec = data.decode('utf-8')
		except Exception:
			error = True

		if error:
			raise PoloInternalException("Error during internal communication")

		try:
			parsed_data = json.loads(data_dec)#json.JSONDecoder(parse_constant=False).decode(data)
		except ValueError:
			error = True

		if error:
			raise PoloInternalException("Error during internal communication")

		if parsed_data.get("OK") is not None:
			return parsed_data.get("OK")

		elif parsed_data.get("Error") is not None:
			raise PoloException("Error in publishing %s: '%s'" % (service, parsed_data.get("Error")))
		
		else:
			raise PoloInternalException("Error during internal communication")

		return None



	def unpublish_service(self, service, multicast_groups=[], delete_file=False):
		"""
		Removes a service. If the service is permanent, the file is only deleted if `delete_file` is set to `True`
		
		:param string service: Name of the service

		:param list multicast_groups: List of the groups where the service is to be deleted. By default deletes the service from all groups

		:param boolean delete_file: Removes the file service if the service is `permanent`. Otherwise it is ignored.
		
		"""
		verify_parameters(service, multicast_groups)

		if type(delete_file) is not bool:
			raise PoloException("delete_file must be boolean")

		message_dict = {}
		message_dict["Command"]= "Unpublish"
		message_dict["Args"] = {"service": service, 
								"multicast_groups":[g for g in multicast_groups], 
								"delete_file": delete_file,
								"uid": os.geteuid()}

		error = False
		try:
			message_str = json.JSONEncoder(allow_nan=False).encode(message_dict) # https://docs.python.org/2/library/json.html#infinite-and-nan-number-values
		except Exception:
			error = True

		if error:
			raise PoloInternalException("Error in JSON Encoder")
		error  = False
		try:
			unicode_msg = message_str.encode('utf-8')
		except UnicodeError:
			error = True

		if error:
			raise PoloInternalException("Error in codification")

		error = False
		
		try:
			if -1 == self.polo_socket.sendto(unicode_msg, ('127.0.0.1', BINDING_PORT)):
				error = True
		except Exception:
			error = True

		if error:
			raise PoloInternalException("Error during internal communication")

		error = False
		try:
			data, address = self.polo_socket.recvfrom(2048)
		except socket.timeout:
			error = True

		if error or data == -1:
			raise PoloInternalException("Error during internal communication")

		try:
			data_dec = data.decode('utf-8')
		except Exception:
			error = True

		if error:
			raise PoloInternalException("Error during internal communication")

		try:
			parsed_data = json.loads(data_dec)#json.JSONDecoder(parse_constant=False).decode(data)
		except ValueError:
			error = True

		if error:
			raise PoloInternalException("Error during internal communication")

		if parsed_data.get("OK") is not None:
			return parsed_data.get("OK")

		elif parsed_data.get("Error") is not None:
			raise PoloException("Error in publishing %s: '%s'" % (service, parsed_data.get("Error")))
		
		else:
			raise PoloInternalException("Error during internal communication")

		return None



		return 0


	def service_info(self, service):
		"""
		Returns a dictionary with all the information from a service
		:param string service: The name of the service

		"""

	def have_service(self, service):
		"""
		Returns true if the requested service is set to be offered
		:param string service: The name of the service.

			Please not that in order to check for an user service, it must be written as user:service


		"""
		pass

	def set_permanent(self, service, permanent=True):
		"""
		Changes the status of a service (permanent/not permanent)
		:param string service: The name of the service

		:param bool permanent: Indicates whether the service must be permanent or not

		"""

class PoloInternalException(Exception):
	pass