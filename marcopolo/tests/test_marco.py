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
		#from itertools import cycle, chain
		self.marco.socket_mcast.recvfrom = MagicMock(side_effect=[(bytes("{\"Command\":\"Polo\"}"), '1.1.1.1'), socket.timeout])
		
		compare = set()
		n = Node()
		n.address = '1.1.1.1'
		compare.add(n)
		self.assertEqual(self.marco.discover().pop().address, n.address)


	def test_discover_multiple(self):
		MAX = 10
		side_effects = [(bytes("{\"Command\":\"Polo\"}"), '1.1.1.1')  for n in range(0,MAX+1) if n < MAX-2]

		side_effects.append(socket.timeout())
		self.marco.socket_mcast.recvfrom = MagicMock(side_effect=side_effects)

		n = Node()
		n.address = '1.1.1.1'

		for node in self.marco.discover():
			self.assertEqual(node.address, n.address)

	def test_service(self):
		side_effects = [(bytes("{\"Address\":\"1.1.1.1\", \"multicast_group\":\"240.0.0.0\", \"services\":\"[]\"}"), '1.1.1.1'), socket.timeout]
		self.marco.socket_mcast.recvfrom = MagicMock(side_effect=side_effects)

		self.assertEqual(self.marco.services('1.1.1.1').address, '1.1.1.1')

	def test_service_fail_send(self):
		self.marco.socket_mcast.sendto = MagicMock(return_value=-1)

		self.assertRaises(marcod.MarcoException, self.marco.services, '1.1.1.1')

	def test_service_empty_address(self):
		self.assertRaises(marcod.MarcoException, self.marco.services, '')

	def test_service_wrong_address(self):
		self.assertRaises(marcod.MarcoException, self.marco.services, '1.1.1.1.1')

	def test_service_wrong_dns_name(self):
		self.assertRaises(marcod.MarcoException, self.marco.services, 'node.wrong.address.1.')

	def test_request_service_bad_request(self):
		self.assertRaises(marcod.MarcoException, self.marco.request_service, 1495)

	def test_request_service_bad_address(self):
		self.assertRaises(marcod.MarcoException, self.marco.request_service, {"service":'dummy', "node":'1.1.1.1.'})

	def test_request_service_sendto_error(self):
		self.marco.sendto = MagicMock(return_value=-1)
		self.assertRaises(marcod.MarcoException, self.marco.request_service, {"service":'dummy', "node":'1.1.1.1.'})

	def test_request_service(self):
		self.marco.recv = MagicMock(return_value = bytes('{['))

		self.assertRaises(marcod.MarcoException, self.marco.request_service, {"service":'dummy', "node":'1.1.1.1.'})
	#testnodedefined
		
