"""
Test the functionality of the corpus comparison package-level functions.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from corpus import DummyComparisonExtractor

class TestPackage(unittest.TestCase):
	"""
	Test the functionality of the corpus comparison package-level functions.
	"""

	def test_init_to_list_one_corpus(self):
		"""
		Test that when providing a single general corpus, it is stored as a list with that corpus.
		"""

		extractor = DummyComparisonExtractor([ 'a' ])
		self.assertEqual([ 'a' ], extractor.general)

	def test_init_to_list_multiple_corpora(self):
		"""
		Test that when providing multiple general corpus, they are stored as a list with those corpora.
		"""

		extractor = DummyComparisonExtractor([ 'a', 'b' ])
		self.assertEqual([ 'a', 'b' ], extractor.general)
