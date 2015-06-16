import sys

sys.path.insert(0, '../')

from marcopolo.polo import polod

from marcopolo.polo import tokenprovider

from twisted.trial import unittest
from mock import MagicMock, patch

class TestPolo(unittest.TestCase):
    def setUp(self):
        pass

class TestPoloBinding(unittest.TestCase):
    pass

class TestTokenProvider(unittest.TestCase):
	def setUp(self):
		pass

	def test_len_secret(self):
		length = 32
		self.assertEqual(length, len(tokenprovider.generate_secret(length)))

	def test_create_token(self):
		secret = tokenprovider.generate_secret(32)
		self.assertIsInstance(tokenprovider.create_token(1, secret), str)

	def test_bad_token_length(self):
		self.assertRaises(ValueError, tokenprovider.generate_secret, 31)

	def test_create_bad_token(self):
		self.assertRaises(ValueError, tokenprovider.create_token, 'dummy', '')

	def test_bad_secret(self):
		self.assertRaises(ValueError, tokenprovider.create_token, 123, 'aaaa')

	def test_decrypt_token(self):
		secret = tokenprovider.generate_secret(32)
		value = 12323
		token = tokenprovider.create_token(value, secret)
		self.assertEqual(value, tokenprovider.decrypt_token(token, secret))
		