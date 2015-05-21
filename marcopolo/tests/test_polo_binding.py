import sys

sys.path.append('/opt/marcopolo/')
from bindings.polo import polo

from twisted.trial import unittest

from mock import MagicMock, patch

from unittest import skip

class TestRegisterService(unittest.TestCase):
	pass


@skip
class TestRegisterService(unittest.TestCase):
	def setUp(self):
		self.polo = polo.Polo()
		self.polo.polo_socket.sendto = MagicMock(return_value=0)
		
	def test_register_success(self):
		self.polo.polo_socket.recv = MagicMock(return_value = bytes("{\"Return\":\"OK\", \"Args\":\"Registered\"}"))
		
		self.assertEqual(self.polo.register_service("dummy"), (True, "Registered"))

	def test_register_fail(self):
		self.polo.polo_socket.recv = MagicMock(return_value = bytes("{\"Return\":\"Error\", \"Args\":\"Service already exists\"}"))
		self.assertEqual(self.polo.register_service("dummy"), (False, "Service already exists"))

	def test_wrong_json(self):
		self.polo.polo_socket.recv = MagicMock(return_value = bytes("[{\"Return\":\"OK\", \"Args\":\"Registered\"}]"))
		self.assertRaises(polo.PoloInternalException, self.polo.register_service, "dummy")

	def test_malformed_json(self):
		self.polo.polo_socket.recv = MagicMock(return_value = bytes("[{\"Return\":\"OK\""))
		self.assertRaises(polo.PoloInternalException, self.polo.register_service, "dummy")

	def test_connection_fail(self):
		self.polo.polo_socket.sendto = MagicMock(return_value = -1)
		self.assertRaises(polo.PoloInternalException, self.polo.register_service, "dummy")

class TestRemoveService(unittest.TestCase):
	def setUp(self):
		self.polo = polo.Polo()
	
	
	@skip
	def test_remove_success(self):
		self.assertFalse(self.polo.remove_service("dummy"))


	def test_remove_failure(self):
		self.assertFalse(self.polo.remove_service("dummy"))

	def test_have_service(self):
		pass
