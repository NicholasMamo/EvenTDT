"""
Test the functionality of the Apriori algorithm.
"""

import json
import os
import sys
import unittest

from datetime import datetime

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from apriori import *

class TestApriori(unittest.TestCase):
	"""
	Test the functionality of the Apriori algorithm.
	"""

	def test_minsup_negative(self):
		"""
		Test that when the minimum support is negative, a ValueError is raised.
		"""

		self.assertRaises(ValueError, apriori, [ ], -1, 0)

	def test_minsup_zero(self):
		"""
		Test that when the minimum support is zero, no ValueError is raised.
		"""

		apriori([ ], 0, 0)

	def test_minsup_zero(self):
		"""
		Test that when the minimum support is one, no ValueError is raised.
		"""

		apriori([ ], 1, 0)

	def test_minsup_high(self):
		"""
		Test that when the minimum support is bigger than 1, a ValueError is raised.
		"""

		self.assertRaises(ValueError, apriori, [ ], 2, 0)

	def test_minconf_negative(self):
		"""
		Test that when the minimum confidence is negative, a ValueError is raised.
		"""

		self.assertRaises(ValueError, apriori, [ ], 0, -1)

	def test_minconf_zero(self):
		"""
		Test that when the minimum confidence is zero, no ValueError is raised.
		"""

		apriori([ ], 0, 0)

	def test_minconf_zero(self):
		"""
		Test that when the minimum confidence is one, no ValueError is raised.
		"""

		apriori([ ], 0, 1)

	def test_minconf_high(self):
		"""
		Test that when the minimum confidence is bigger than 1, a ValueError is raised.
		"""

		self.assertRaises(ValueError, apriori, [ ], 0, 2)
