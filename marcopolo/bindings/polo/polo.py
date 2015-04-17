import json, socket, sys

sys.path.append('/opt/marcopolo/')
TIMEOUT = 4000

class Polo(object):
	def __init__(self):
		self.polo_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.polo_socket = socket.settimeout(TIMEOUT/1000.0)

	def register_service(self, service, permanent=False):
		"""
		Registration of a service during execution time
		The parameter service indicates the unique identifier of the service
		If permanent is set to true a file will be created and the service will be 
		permanently offered unless the file is deleted
		"""
		if not permanent:
			message = {'Command': 'Register', 'Params': service}
			message_bytes = bytes(json.loads(message), 'utf-8')
			self.polo_socket.sendto(message_bytes, ('127.0.1.1', 1337))

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


