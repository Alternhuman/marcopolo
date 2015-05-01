import sys

sys.path.append('/opt/marcopolo/')

from polo import polod

from twisted.trial import unittest
from mock import MagicMock, patch

class TestPolo(unittest.TestCase):
	def setUp(self):
		pass

class TestPoloBinding(unittest.TestCase):
	pass