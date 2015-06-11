import sys

sys.path.append('/opt/marcopolo/')
from bindings.marco import marco
from marco_conf.utils import Node

from twisted.trial import unittest
from mock import MagicMock, patch

import json, socket

def side_effect_timeout(self,arg):
    raise socket.timeout()

class TestRequestFor(unittest.TestCase):
    def setUp(self):
        self.marco = marco.Marco()
        self.marco.marco_socket.sendto = MagicMock(return_value=0)
        self.marco.marco_socket.recvfrom = MagicMock(return_value = (bytes("[{\"Address\":\"1\", \"Params\":\"service\"}]"), '1'))
    
    def test_request(self):
        self.assertIsInstance(self.marco.request_for("deployer"), set)

    def test_request_content(self):
        s = set()
        n = Node()
        n.address = "1"
        n.services = ["service"]
        s.add(n)
        self.assertEqual(self.marco.request_for("deployer").pop().address, n.address)
        #TODO: self.assertEqual(self.marco.request_for("deployer").pop().services, n.services)
    
    def test_timeout(self):

        self.marco.marco_socket.recvfrom.side_effect = socket.timeout()
        self.assertRaises(marco.MarcoTimeOutException, self.marco.request_for, "deployer")
    
    def test_malformed_json(self):
        self.marco.marco_socket.recvfrom = MagicMock(return_value = (bytes("[{Address\":\"1\", \"Params\":\"service\"}]"), '1'))
        self.assertRaises(marco.MarcoInternalError, self.marco.request_for, "deployer")

class TestMarco(unittest.TestCase):
    def setUp(self):
        self.marco = marco.Marco()
        self.marco.marco_socket.sendto = MagicMock(return_value=0)
        #self.marco.marco_socket.recv = MagicMock(return_value = bytes("[[\"1.1.1.1\", 100], [\"1.2.2.2\", 200]]"))
        self.marco.marco_socket.recv = MagicMock(return_value = bytes("[{\"Address\":\"1.1.1.1\", \"Params\":\"1\"}]"))
    
    def test_marco(self):
        print(self.marco.marco())
        #self.assertEqual(self.marco.marco(), ['1.1.1.1', '1.2.2.2'])
    
    def test_marco_timeout(self):
        self.marco.marco_socket.recv = MagicMock(return_value = (bytes("[{\"Address\":\"1\", \"Params\":\"service\"}]"), '1'))
        self.marco.marco_socket.recv.side_effect = socket.timeout()
        self.assertRaises(marco.MarcoTimeOutException, self.marco.marco)

    def test_malformed_json(self):
        self.marco.marco_socket.recv = MagicMock(return_value = bytes("[{"))
        self.assertRaises(marco.MarcoInternalError, self.marco.marco)
    
        