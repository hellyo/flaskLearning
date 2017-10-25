import unittest
from app.models import User
class UserModelTestCase(unittest.TestCase):
	def test_password_setter(self):
		u = User(password = 'cat')
		self.assertTrue(u.password_hash is not None)

	def test_no_password_getter(self):
		u = User(password='cat')
		with self.assertRaises(AttributeError)
			u.password
	
	def test_passwordCheck(self):
		u = User(password='cat')
		self.assertTrue(u.checkIn('cat'))
		self.assertFalse(u.checkIn('dog'))
	
	def test_password_random(self):
		u = User(password='cat')
		u2 = User(password='cat')
		self.assertTrue(u.password_hash !=u2.password_hash)
	