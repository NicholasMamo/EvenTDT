"""
Run unit tests on the :class:`~objects.ordered_enum.OrderedEnum` class.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from ordered_enum import OrderedEnum

class LogLevel(OrderedEnum):
	"""
	The logger's logging level.
	It is based on a :class:`~objects.ordered_enum.OrderedEnum`.

	Valid logging levels:

		#. `INFO` - Information and higher-level logging only
		#. `WARNING` - Warnings and higher-level logging only
		#. `ERROR` - Errors and higher-level logging only
	"""

	INFO = 1
	WARNING = 2
	ERROR = 3

class TestOrderedEnum(unittest.TestCase):
	"""
	Test the :class:`~objects.ordered_enum.OrderedEnum` class.
	"""

	def test_ge_less(self):
		"""
		Test the greater than or equal comparison when the value is less.
		"""

		self.assertFalse(1 >= LogLevel.WARNING)

	def test_ge_equal(self):
		"""
		Test the greater than or equal comparison when the value is equal.
		"""

		self.assertTrue(2 >= LogLevel.WARNING)

	def test_ge_greater(self):
		"""
		Test the greater than or equal comparison when the value is greater.
		"""

		self.assertTrue(3 >= LogLevel.WARNING)

	def test_le_less(self):
		"""
		Test the less than or equal comparison when the value is less.
		"""

		self.assertTrue(1 <= LogLevel.WARNING)

	def test_le_equal(self):
		"""
		Test the less than or equal comparison when the value is equal.
		"""

		self.assertTrue(2 <= LogLevel.WARNING)

	def test_le_greater(self):
		"""
		Test the less than or equal comparison when the value is greater.
		"""

		self.assertFalse(3 <= LogLevel.WARNING)

	def test_g_less(self):
		"""
		Test the greater than comparison when the value is less.
		"""

		self.assertFalse(1 > LogLevel.WARNING)

	def test_g_equal(self):
		"""
		Test the greater than comparison when the value is equal.
		"""

		self.assertFalse(2 > LogLevel.WARNING)

	def test_g_greater(self):
		"""
		Test the greater than comparison when the value is greater.
		"""

		self.assertTrue(3 > LogLevel.WARNING)

	def test_l_less(self):
		"""
		Test the less than comparison when the value is less.
		"""

		self.assertTrue(1 < LogLevel.WARNING)

	def test_l_equal(self):
		"""
		Test the less than comparison when the value is equal.
		"""

		self.assertFalse(2 < LogLevel.WARNING)

	def test_l_greater(self):
		"""
		Test the less than comparison when the value is greater.
		"""

		self.assertFalse(3 < LogLevel.WARNING)

	def test_eq_less(self):
		"""
		Test the equality comparison when the value is less.
		"""

		self.assertFalse(1 == LogLevel.WARNING)

	def test_eq_equal(self):
		"""
		Test the equality comparison when the value is equal.
		"""

		self.assertTrue(2 == LogLevel.WARNING)

	def test_eq_greater(self):
		"""
		Test the equality comparison when the value is greater.
		"""

		self.assertFalse(3 == LogLevel.WARNING)
