import sys

sys.path.append('/opt/marcopolo/')
from bindings.polo import polo

from twisted.trial import unittest

from mock import MagicMock, patch



class TestRegisterService(unittest.TestCase):
    pass

class TestRegisterService(unittest.TestCase):
    def setUp(self):
        self.polo = polo.Polo()
        self.polo.polo_socket.sendto = MagicMock(return_value=0)
        
    def test_register_success(self):
        #self.polo.polo_socket.recv = MagicMock(return_value = bytes("{\"Return\":\"OK\", \"Args\":\"Registered\"}"))
        self.polo.polo_socket.recv = MagicMock(return_value = bytes("{\"OK\":\"dummy\"}"))
        
        self.assertEqual(self.polo.publish_service("dummy"), "dummy")

    def test_register_fail(self):
        self.polo.polo_socket.recv = MagicMock(return_value = bytes("{\"Error\":\"Error\", \"Args\":\"Service already exists\"}"))
        self.assertRaises(polo.PoloException, self.polo.publish_service, "dummy")

    def test_wrong_json(self):
        self.polo.polo_socket.recv = MagicMock(return_value = bytes("[{\"Return\":\"OK\", \"Args\":\"Registered\"}]"))
        self.assertRaises(polo.PoloInternalException, self.polo.publish_service, "dummy")

    def test_malformed_json(self):
        self.polo.polo_socket.recv = MagicMock(return_value = bytes("[{\"Return\":\"OK\""))
        self.assertRaises(polo.PoloInternalException, self.polo.publish_service, "dummy")

    def test_connection_fail(self):
        self.polo.polo_socket.sendto = MagicMock(return_value = -1)
        self.assertRaises(polo.PoloInternalException, self.polo.publish_service, "dummy")

# class TestRemoveService(unittest.TestCase):
#   def setUp(self):
#       self.polo = polo.Polo()
    
    
    
#   def test_remove_success(self):
#       self.assertFalse(self.polo.unpublish_service("dummy"))


#   def test_remove_failure(self):
#       self.assertFalse(self.polo.unpublish("dummy"))

#   def test_have_service(self):
#       pass
