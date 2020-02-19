"""
Test the functionality of the Wikipedia search resolver.
"""

import os
import random
import string
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nltk.corpus import stopwords

from apd.extractors.local.entity_extractor import EntityExtractor
from apd.scorers.local.tf_scorer import TFScorer
from apd.filters.local.threshold_filter import ThresholdFilter
from apd.resolvers.external.wikipedia_search_resolver import WikipediaSearchResolver

from nlp.document import Document
from nlp.tokenizer import Tokenizer
from nlp.term_weighting.tf import TF

class TestWikipediaSearchResolver(unittest.TestCase):
	"""
	Test the implementation and results of the Wikipedia search resolver.
	"""

	def test_year_check(self):
		"""
		Test that when checking for a year, the function returns a boolean.
		"""

		article = 'Youssouf Koné (footballer, born 1995)'
		resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, [ ])
		self.assertTrue(resolver._has_year(article))

	def test_year_check_range(self):
		"""
		Test that when checking for a year in a range, the function returns `True`.
		"""

		article = '2019–20 Premier League'
		resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, [ ])
		self.assertTrue(resolver._has_year(article))

		article = '2019-20 Premier League'
		resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, [ ])
		self.assertTrue(resolver._has_year(article))

	def test_year_check_short_number(self):
		"""
		Test that when checking for a year with a short number, the function does not detect a year.
		"""

		article = 'Area 51'
		resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, [ ])
		self.assertFalse(resolver._has_year(article))

	def test_year_check_long_number(self):
		"""
		Test that when checking for a year with a long number, the function does not detect a year.
		"""

		article = '1234567890'
		resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, [ ])
		self.assertFalse(resolver._has_year(article))

