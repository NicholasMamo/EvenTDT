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

	def test_minsup_one(self):
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

	def test_minconf_one(self):
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

	def test_filter_itemsets_minsup_negative(self):
		"""
		Test that when the minimum support is negative, a ValueError is raised.
		"""

		self.assertRaises(ValueError, filter_itemsets, [ ], { }, -1)

	def test_filter_itemsets_minsup_zero(self):
		"""
		Test that when the minimum support is zero, no ValueError is raised.
		"""

		filter_itemsets([ ], { }, 0)

	def test_filter_itemsets_minsup_one(self):
		"""
		Test that when the minimum support is one, no ValueError is raised.
		"""

		filter_itemsets([ ], { }, 1)

	def test_filter_itemsets_minsup_high(self):
		"""
		Test that when the minimum support is bigger than 1, a ValueError is raised.
		"""

		self.assertRaises(ValueError, filter_itemsets, [ ], { }, 1.1)

	def test_filter_itemsets_empty_transactions(self):
		"""
		Test that when filtering a list of itemsets with empty transactions, an empty list is returned.
		"""

		itemsets = [ { letter } for letter in string.ascii_letters + string.digits ]
		self.assertEqual([ ], filter_itemsets([ ], itemsets, 0.1))

	def test_filter_itemsets_empty_transactions_minsup_zero(self):
		"""
		Test that when filtering a list of itemsets with empty transactions, but with a support of 0, the original itemsets are returned.
		"""

		itemsets = [ { letter } for letter in string.ascii_letters + string.digits ]
		self.assertEqual(itemsets, filter_itemsets([ ], itemsets, 0))

	def test_filter_itemsets_empty_itemsets(self):
		"""
		Test that when filtering an empty list of itemsets, anoher empty list is returned.
		"""

		transactions = [ { letter } for letter in string.ascii_letters + string.digits ]
		self.assertEqual([ ], filter_itemsets(transactions, [ ], 0.1))

	def test_filter_itemsets_minsup_equal(self):
		"""
		Test that when filtering itemsets, those with a support equal to the minimum support are returned.
		"""

		transactions = [ { 'A' }, { 'B' } ]
		itemsets = [ { letter } for letter in string.ascii_letters + string.digits ]
		self.assertEqual([ { 'A' }, { 'B' } ], filter_itemsets(transactions, itemsets, 0.5))

	def test_filter_itemsets_minsup_higher(self):
		"""
		Test that when filtering itemsets, those with a support higher than the minimum support are returned.
		"""

		transactions = [ { 'A' }, { 'B' }, { 'A', 'B', 'C' } ]
		itemsets = [ { letter } for letter in string.ascii_letters + string.digits ]
		self.assertEqual([ { 'A' }, { 'B' } ], filter_itemsets(transactions, itemsets, 0.5))

	def test_filter_itemsets_minsup_lower(self):
		"""
		Test that when filtering itemsets, those with a support lower than the minimum support are excluded returned.
		"""

		transactions = [ { 'A' }, { 'B' }, { 'A', 'B' }, { 'C' } ]
		itemsets = [ { letter } for letter in string.ascii_letters + string.digits ]
		self.assertEqual([ { 'A' }, { 'B' } ], filter_itemsets(transactions, itemsets, 0.5))

	def test_filter_itemsets_multi(self):
		"""
		Test that when filtering itemsets with multiple items, the same rules are respected.
		"""

		vocabulary = [ [ letter ] for letter in string.ascii_letters + string.digits ]
		itemsets = get_itemsets(vocabulary, 2)
		transactions = [ { 'A', 'B' }, { 'B', 'C', 'D' } ]
		self.assertEqual([ { 'A', 'B' }, { 'B', 'C' }, { 'B', 'D'}, { 'C', 'D' } ], filter_itemsets(transactions, itemsets, 0.5))

	def test_next_rules_empty_antecedent(self):
		"""
		Test that when the antecedent is empty, no rules are created.
		"""

		self.assertEqual([ ], next_rules({ }, { 'A' }))

	def test_next_rules_empty_consequent(self):
		"""
		Test that when the consequent is empty, all new rules' consequents are unit items.
		"""

		antecedent = [ letter for letter in string.ascii_letters + string.digits ]
		rules = next_rules(antecedent, { })
		self.assertTrue(all(len(consequent) == 1 for _, consequent in rules))
		self.assertTrue(all(len(rule_antecedent) == len(antecedent) -1 for rule_antecedent, _ in rules))
		self.assertEqual(len(antecedent), len(rules))
		self.assertEqual(set(antecedent), set(list(consequent)[0] for _, consequent in rules))

	def test_next_rules_no_consequent(self):
		"""
		Test that when no consequent is given, it is treated as an empty consequent.
		"""

		antecedent = [ letter for letter in string.ascii_letters + string.digits ]
		rules = next_rules(antecedent)
		self.assertTrue(all(len(consequent) == 1 for _, consequent in rules))
		self.assertTrue(all(len(rule_antecedent) == len(antecedent) -1 for rule_antecedent, _ in rules))
		self.assertEqual(len(antecedent), len(rules))
		self.assertEqual(set(antecedent), set(list(consequent)[0] for _, consequent in rules))

	def test_next_rules_overlapping(self):
		"""
		Test that when the antecedent and the consequent have overlapping items, they are ignored in the consequent.
		"""

		antecedent = { 'A', 'B' }
		consequent = { 'A' }
		rules = next_rules(antecedent, consequent)
		self.assertEqual(2, len(rules))
		self.assertTrue(({ 'B' }, { 'A' }) in rules)
		self.assertTrue(({ 'A' }, { 'A', 'B' }) in  rules)

	def test_next_rules_duplicate_antecedent(self):
		"""
		Test that when there are duplicate items in the antecedent, they are removed.
		"""

		antecedent = { 'A', 'A', 'B' }
		consequent = { 'C' }
		rules = next_rules(antecedent, consequent)
		self.assertEqual(2, len(rules))
		self.assertTrue(({ 'A' }, { 'B', 'C' }) in rules)
		self.assertTrue(({ 'B' }, { 'A', 'C' }) in  rules)

	def test_next_rules_count(self):
		"""
		Test that the number of next rules is equivalent to the length of the antecedent.
		"""

		antecedent = [ letter for letter in string.ascii_letters ]
		consequent = { letter for letter in string.digits }
		rules = next_rules(antecedent, consequent)
		self.assertEqual(len(antecedent), len(rules))
