import json, socket, sys

sys.path.append('/opt/marcopolo/')
TIMEOUT = 4000

class Polo(object):
	def __init__(self):
		self.polo_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.polo_socket.settimeout(TIMEOUT/1000.0)

	def register_service(self, service, permanent=False):
		"""
		Registration of a service during execution time
		The parameter service indicates the unique identifier of the service
		If permanent is set to true a file will be created and the service will be 
		permanently offered unless the file is deleted
		"""
		if not permanent:
			message = {'Command': 'Register', 'Params': service}
			message_bytes = bytes(json.dumps(message).encode('utf-8'))
			if -1 == self.polo_socket.sendto(message_bytes, ('127.0.1.1', 1337)):
				raise PoloInternalException("Internal socket error")

			try:
				response_bytes = self.polo_socket.recv(4096)
			except socket.timeout:
				raise PoloInternalException("Error on comunication with the service")
			
			error = None
			try:
				response = json.loads(response_bytes.decode('utf-8'))
			except ValueError:
				error = True
			if error:
				raise PoloInternalException("Internal error on while parsing")

			error = None
			try:
				if response["Return"] == "OK":
					return (True, response["Args"])
				elif response["Return"] == "Error":
					return (False, response["Args"])
			except TypeError:
				error = True
			if error: 
				raise PoloInternalException("Wrong response format")

	def remove_service(self, service, permanent=True):
		"""
		A service is removed, permanently or temporarily
		"""
		pass

	def have_service(self, service):
		"""
		Returns true if the requested service is set to be offered
		Note: the fact that a service is not offered does not imply that the service is
		not on the configuration files
		"""
		pass

class PoloInternalException(Exception):
	pass