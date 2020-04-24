"""
Test the functionality of the package-level functions.
"""

import json
import os
import sys
import unittest

from datetime import datetime

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

import association

class TestPackage(unittest.TestCase):
	"""
	Test the functionality of the package-level functions.
	"""

	def test_support_empty_transactions(self):
		"""
		Test that when the transactions are empty, the support is always 0.
		"""

		self.assertEqual(0, association.support([ ], { }))

	def test_support_empty_itemset(self):
		"""
		Test that when the itemset is empty, the support is 1.
		"""

		self.assertEqual(1, association.support([ { } ], { }))

	def test_support_whole(self):
		"""
		Test that when the itemset appears in all transactions, the support is 1.
		"""

		self.assertEqual(1, association.support([ { 'A' } ], { 'A' }))

	def test_support_whole_partial(self):
		"""
		Test that when the itemset appears in all transactions, even if it is not always the only item, the support is 1.
		"""

		self.assertEqual(1, association.support([ { 'A' }, { 'A', 'B' } ], { 'A' }))

	def test_support_partial(self):
		"""
		Test that when the itemset appears in some of the transactions, the support is a fraction.
		"""

		self.assertEqual(0.5, association.support([ { 'A' }, { 'B' } ], { 'A' }))

	def test_support_repeated(self):
		"""
		Test that when the itemset appears repeatedly in some of the transactions, the support considers it only once.
		"""

		self.assertEqual(0.5, association.support([ { 'A', 'A' }, { 'B' } ], { 'A' }))

	def test_confidence_empty_transactions(self):
		"""
		Test that when the transactions are empty, the confidence is always 0.
		"""

		self.assertEqual(0, association.confidence([ ], { }, { }))

	def test_confidence_unknown_antecedent(self):
		"""
		Test that when the antecedent never appears, the confidence is 0.
		"""

		self.assertEqual(0, association.confidence([ { 'A', 'B' }, { 'A', 'B', 'C' } ], { 'D' }, { }))

	def test_confidence_empty_consequent(self):
		"""
		Test that when the consequent is empty and the antecedent is known, the confidence is 1.
		"""

		self.assertEqual(1.0, association.confidence([ { 'A', 'B' }, { 'A', 'B', 'C' } ], { 'A' }, { }))

	def test_confidence_whole(self):
		"""
		Test that when the antecedent and consequent always appear together, the confidence is 1.
		"""

		self.assertEqual(1.0, association.confidence([ { 'A', 'B' }, { 'A', 'B', 'C' } ], { 'A' }, { 'B' }))

	def test_confidence_partial(self):
		"""
		Test that when the antecedent and consequent do not always appear together, the confidence is a fraction.
		"""

		self.assertEqual(0.5, association.confidence([ { 'A', 'B' }, { 'A', 'B', 'C' } ], { 'A', 'B' }, { 'C' }))

	def test_confidence_antecedent_condition(self):
		"""
		Test that transactions without the antecedent are not used to compute the confidence.
		"""

		self.assertEqual(0.5, association.confidence([ { 'A', 'B' }, { 'A', 'B', 'C' }, { 'B', 'C' } ], { 'A', 'B' }, { 'C' }))
