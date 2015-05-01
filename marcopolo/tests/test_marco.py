import sys

sys.path.append('/opt/marcopolo/')
from marco import marcod
from marco_conf.utils import Node
from twisted.trial import unittest
from mock import MagicMock, patch

import socket

class TestMarco(unittest.TestCase):
	def setUp(self):
		self.marco = marcod.Marco()
		self.marco.socket_bcast = MagicMock(name='socket', spec=socket.socket)
		self.marco.socket_mcast = MagicMock(name='socket', spec=socket.socket)
		self.marco.socket_ucast = MagicMock(name='socket', spec=socket.socket)

	def test_discover_senderror(self):
		self.marco.socket_mcast.sendto.return_value = -1
		self.assertRaises(marcod.MarcoException, self.marco.discover)


	def test_discover(self):
		self.counter = 0
		def raise_timeout_if(max_iter):
			if self.counter > max_iter:
				raise socket.timeout
			else:
				self.counter += 1
		
		#self.marco.socket_mcast.recvfrom.side_effect = raise_timeout_if(1)
		from itertools import cycle, chain
		self.marco.socket_mcast.recvfrom = MagicMock(side_effect=[(bytes("{\"Command\":\"Polo\"}"), '1.1.1.1'), socket.timeout])
		
		compare = set()
		n = Node()
		n.address = '1.1.1.1'
		compare.add(n)
		self.assertEqual(self.marco.discover().pop().address, n.address)

