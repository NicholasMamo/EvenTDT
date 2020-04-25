"""
Test the functionality of the Apriori algorithm.
"""

import json
import os
import string
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

	def test_get_itemsets_length_float(self):
		"""
		Test that when the length of itemsets is a float, a ValueError is raised.
		"""

		self.assertRaises(ValueError, get_itemsets, [ ], 1.2)

	def test_get_itemsets_length_rounded_float(self):
		"""
		Test that when the length of itemsets is an integer with a decimal, no ValueError is raised.
		"""

		get_itemsets([ ], 1.0)

	def test_get_itemsets_length_integer(self):
		"""
		Test that when the length of itemsets is an integer, no ValueError is raised.
		"""

		get_itemsets([ ], 1)

	def test_get_itemsets_length_zero(self):
		"""
		Test that when the length of itemsets is zero, a ValueError is raised.
		"""

		self.assertRaises(ValueError, get_itemsets, [ ], 0)

	def test_get_itemsets_length_negative(self):
		"""
		Test that when the length of itemsets is negative, a ValueError is raised.
		"""

		self.assertRaises(ValueError, get_itemsets, [ ], -1)

	def test_get_itemsets_empty(self):
		"""
		Test that when an empty list of itemsets is given, nothing is returned.
		"""

		self.assertEqual([ ], get_itemsets([ ], 1))

	def test_get_itemsets_empty_itemsets(self):
		"""
		Test that when a list of empty itemsets is given, nothing is returned.
		"""

		self.assertEqual([ ], get_itemsets([ { } ], 1))

	def test_get_itemsets_tautological(self):
		"""
		Test that when a list of itemsets having the same length as the given length is given, nothing is returned.
		"""

		self.assertEqual([ ], get_itemsets([ { letter } for letter in string.ascii_letters + string.digits ], 1))

	def test_get_itemsets_large(self):
		"""
		Test that when a list of itemsets of unit items is given and the given length is larger than 2, nothing is returned.
		"""

		self.assertEqual([ ], get_itemsets([ { letter } for letter in string.ascii_letters + string.digits ], 3))

	def test_get_itemsets_duplicates(self):
		"""
		Test that when the list of itemsets has duplicates and all have the same length as the given length is given, nothing is returned.
		"""

		self.assertEqual([ ], get_itemsets([ { letter } for letter in string.ascii_letters + string.digits ] * 2, 1))

	def test_get_itemsets_count(self):
		"""
		Test that the number of new itemsets is given by n(n-1)/2.
		"""

		vocabulary = [ { letter } for letter in string.ascii_letters + string.digits ]
		itemsets = get_itemsets(vocabulary, 2)
		self.assertEqual(len(vocabulary) * (len(vocabulary) - 1) / 2., len(itemsets))
		self.assertTrue({ 'A', 'B' } in itemsets)
		self.assertTrue({ 'A', 'a' } in itemsets)
		self.assertTrue({ 'a', 'A' } in itemsets)
		self.assertTrue({ '1', 'A' } in itemsets)

	def test_get_itemsets_list(self):
		"""
		Test that itemsets are returned even when they are given as lists, not sets.
		"""

		vocabulary = [ [ letter ] for letter in string.ascii_letters + string.digits ]
		itemsets = get_itemsets(vocabulary, 2)
		self.assertEqual(len(vocabulary) * (len(vocabulary) - 1) / 2., len(itemsets))
