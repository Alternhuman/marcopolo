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
        self.assertRaises(marcod.MarcoException, self.marco.marco)


    def test_discover(self):
        self.marco.socket_mcast.recvfrom = MagicMock(side_effect=[(bytes("{\"Command\":\"Polo\"}"), ('1.1.1.1', 1339)), socket.timeout])
        #self.marco.socket_mcast.recvfrom.return_value = (bytes("{\"Command\":\"Polo\"}"), ('1.1.1.1', 1339))
        #self.marco.socket_mcast.recvfrom.side_effect= [(bytes("{\"Command\":\"Polo\"}"), ('1.1.1.1', 1339)), socket.timeout]
        
        compare = set()
        n = Node()
        n.address = '1.1.1.1'
        compare.add(n)
        #print(self.marco.marco().pop())
        self.assertEqual(self.marco.marco().pop().address, n.address)


    def test_discover_multiple(self):
        MAX = 10
        side_effects = [(bytes("{\"Command\":\"Polo\"}"), ('1.1.1.1', 1339))  for n in range(0,MAX+1) if n < MAX-2]

        side_effects.append(socket.timeout())
        self.marco.socket_mcast.recvfrom = MagicMock(side_effect=side_effects)

        n = Node()
        n.address = '1.1.1.1'

        for node in self.marco.marco():
            self.assertEqual(node.address, n.address)

    def test_service(self):
        side_effects = [(bytes("{\"Address\":\"1.1.1.1\", \"multicast_group\":\"240.0.0.0\", \"Params\":\"[]\"}"), ('1.1.1.1', 1338)), socket.timeout]
        self.marco.socket_ucast.recvfrom = MagicMock(side_effect=side_effects)

        self.assertEqual(self.marco.services('1.1.1.1').address, '1.1.1.1')

    def test_service_fail_send(self):
        self.marco.socket_ucast.sendto = MagicMock(return_value=-1)

        self.assertRaises(marcod.MarcoException, self.marco.services, '1.1.1.1')

    def test_service_empty_address(self):
        self.assertRaises(marcod.MarcoException, self.marco.services, '')

    def test_service_wrong_address(self):
        self.assertRaises(marcod.MarcoException, self.marco.services, '1.1.1.1.1')

    def test_service_wrong_dns_name(self):
        self.assertRaises(marcod.MarcoException, self.marco.services, 'node.wrong.address.1.')

    def test_request_service_bad_request(self):
        self.assertRaises(marcod.MarcoException, self.marco.request_for, 1495)

    #def test_request_service_bad_address_2(self):
    #   self.assertRaises(marcod.MarcoException, self.marco.request_for, service='dummy', node='1.1.1.1.')

    def test_request_service_sendto_error(self):
        self.marco.socket_ucast.sendto = MagicMock(return_value=-1)
        self.assertRaises(marcod.MarcoException, self.marco.request_for, service='dummy', node='1.1.1.1.')

    def test_request_service(self):
        self.marco.socket_ucast.recv = MagicMock(return_value = bytes('{['.encode('utf-8')))

        self.assertRaises(marcod.MarcoException, self.marco.request_for, service='dummy', node='1.1.1.1.')
    #testnodedefined
        
class TestParamsMarco(unittest.TestCase):
    def setUp(self):
        self.marco = marcod.Marco()
        self.marco.socket_bcast = MagicMock(name='socket', spec=socket.socket)
        self.marco.socket_mcast = MagicMock(name='socket', spec=socket.socket)
        self.marco.socket_ucast = MagicMock(name='socket', spec=socket.socket)

    def test_marco_bad_timeout(self):

        self.assertRaises(marcod.MarcoException, self.marco.marco,timeout='a')

    def test_marco_bad_max_nodes(self):

        self.assertRaises(marcod.MarcoException, self.marco.marco, max_nodes='a')

    def test_marco_max_nodes(self):
        self.marco.socket_mcast.sendto = MagicMock(return_value=10)
        
        MAX = 40
        side_effects = [(bytes("{\"Command\":\"Polo\"}"), ('1.1.1.1', 1339))  for n in range(0,MAX) if n < MAX-1]
        
        side_effects.append(socket.timeout())
        self.marco.socket_mcast.recvfrom= MagicMock(side_effect=side_effects)
        
        nodes = self.marco.marco(max_nodes=MAX/2)

        self.assertEqual(MAX/2, len(nodes))

    def test_marco_bad_exclude(self):

        
        self.assertRaises(marcod.MarcoException, self.marco.marco, exclude=1)

    def test_marco_exclude(self):
        MAX = 40
        side_effects = [(bytes("{\"Command\":\"Polo\"}"), '1.1.1.1')  for n in range(0,MAX) if n < MAX-1]
        side_effects.append((bytes("{\"Command\":\"Polo\"}"), ('2.2.2.2', 1338)))
        side_effects.append(socket.timeout())
        self.marco.socket_mcast.recvfrom= MagicMock(side_effect=side_effects)

        self.assertEqual(len(self.marco.marco(exclude=['1.1.1.1'])), 1)

    def test_marco_bad_retries(self):
        MAX = 'a'
        self.assertRaises(marcod.MarcoException, self.marco.marco, retries=MAX)

    def test_marco_retries(self):
        MAX = 3
        side_effects = [socket.timeout  for n in range(0,MAX-1)]
        side_effects.append((bytes("{\"Command\":\"Polo\"}"), ('2.2.2.2', 1338)))
        side_effects.append(socket.timeout())
        self.marco.socket_mcast.recvfrom= MagicMock(side_effect=side_effects)
        
        self.assertEqual(len(self.marco.marco(retries=MAX)), 1)

    def test_marco_retries_2(self):
        MAX = 3
        side_effects = [socket.timeout  for n in range(0,MAX)]
        side_effects.append(socket.timeout())

        self.marco.socket_mcast.recvfrom= MagicMock(side_effect=side_effects)
        
        self.assertNotEqual(len(self.marco.marco(retries=MAX)), 1)

class TestParamsRequestFor(unittest.TestCase):
    def setUp(self):
        self.marco = marcod.Marco()
        self.marco.socket_bcast = MagicMock(name='socket', spec=socket.socket)
        self.marco.socket_mcast = MagicMock(name='socket', spec=socket.socket)
        self.marco.socket_ucast = MagicMock(name='socket', spec=socket.socket)

    def test_request_for_bad_timeout(self):
        self.assertRaises(marcod.MarcoException, self.marco.request_for,'dummy',timeout='a')

    def test_request_for_timeout(self):
        self.marco.socket_mcast.recvfrom= MagicMock(side_effect=socket.timeout)
        self.assertEqual(self.marco.request_for('dummy',timeout=1000), set())

    def test_request_for_bad_max_nodes(self):

        self.assertRaises(marcod.MarcoException, self.marco.request_for, 'dummy', max_nodes='a')

    def test_request_for_max_nodes(self):
        self.marco.socket_mcast.sendto = MagicMock(return_value=10)
        
        MAX = 40
        side_effects = [(bytes("{\"Command\":\"OK\"}"), '1.1.1.1')  for n in range(0,MAX) if n < MAX-1]
        
        side_effects.append(socket.timeout())
        self.marco.socket_mcast.recvfrom= MagicMock(side_effect=side_effects)
        
        nodes = self.marco.request_for('dummy',max_nodes=MAX/2)

        self.assertEqual(MAX/2, len(nodes))

    def test_request_for_bad_exclude(self):
        self.assertRaises(marcod.MarcoException, self.marco.request_for,'dummy', exclude=1)

    def test_request_for_exclude(self):
        MAX = 40
        side_effects = [(bytes("{\"Command\":\"OK\"}"), '1.1.1.1')  for n in range(0,MAX) if n < MAX-1]
        side_effects.append((bytes("{\"Command\":\"OK\"}"), '2.2.2.2'))
        side_effects.append(socket.timeout())
        self.marco.socket_mcast.recvfrom= MagicMock(side_effect=side_effects)

        self.assertEqual(len(self.marco.request_for('dummy', exclude=['1.1.1.1'])), 1)


class TestParametersRequestOne(unittest.TestCase):
    def setUp(self):
        self.marco = marcod.Marco()
        self.marco.socket_bcast = MagicMock(name='socket', spec=socket.socket)
        self.marco.socket_mcast = MagicMock(name='socket', spec=socket.socket)
        self.marco.socket_ucast = MagicMock(name='socket', spec=socket.socket)

    def test_request_one_bad_timeout(self):
        self.assertRaises(marcod.MarcoException, self.marco.request_one,'dummy',timeout='a')

    def test_request_one_timeout(self):
        self.marco.socket_mcast.recvfrom= MagicMock(side_effect=socket.timeout)
        self.assertEqual(self.marco.request_one('dummy',timeout=1000), set())

    def test_request_one_bad_exclude(self):
        self.assertRaises(marcod.MarcoException, self.marco.request_one,'dummy', exclude=1)

    def test_request_one_length(self):
        MAX = 40
        side_effects = [(bytes("{\"Command\":\"OK\"}"), '1.1.1.1')  for n in range(0,MAX) if n < MAX-1]
        side_effects.append((bytes("{\"Command\":\"OK\"}"), '2.2.2.2'))
        side_effects.append(socket.timeout())
        self.marco.socket_mcast.recvfrom = MagicMock(side_effect=side_effects)
        self.assertEqual(len(self.marco.request_one('dummy')), 1)

class TestServices(unittest.TestCase):
    def setUp(self):
        self.marco = marcod.Marco()
        self.marco.socket_bcast = MagicMock(name='socket', spec=socket.socket)
        self.marco.socket_mcast = MagicMock(name='socket', spec=socket.socket)
        self.marco.socket_ucast = MagicMock(name='socket', spec=socket.socket)

    def test_services_bad_addr(self):
        self.assertRaises(marcod.MarcoException, self.marco.services, '')
        self.assertRaises(marcod.MarcoException, self.marco.services, '1.1.1.1.1')

    def test_services_bad_timeout(self):
        self.assertRaises(marcod.MarcoException, self.marco.services, '1.1.1.1', timeout='a')

    def test_services_timeout(self):
        side_effects = [(bytes("{\"Command\":\"OK\", \"Params\":[\"dummy\"]}"), '1.1.1.1'), socket.timeout]
        
        self.marco.socket_ucast.recvfrom = MagicMock(side_effect = side_effects)
        
        self.assertEqual(self.marco.services('1.1.1.1', 1).services, ['dummy'])

    