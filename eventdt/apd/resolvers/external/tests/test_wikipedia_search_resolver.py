"""
Test the functionality of the Wikipedia search resolver.
"""

import os
import random
import re
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

	def test_remove_brackets(self):
		"""
		Test that when removing brackets, they are completely removed.
		"""

		article = 'Youssouf Koné (footballer, born 1995)'
		resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, [ ])
		self.assertEqual('Youssouf Koné', resolver._remove_brackets(article).strip())

	def test_remove_unclosed_brackets(self):
		"""
		Test that when removing brackets that are not closed, they are not removed.
		"""

		article = 'Youssouf Koné (footballer, born 1995'
		resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, [ ])
		self.assertEqual('Youssouf Koné (footballer, born 1995', resolver._remove_brackets(article).strip())

	def test_get_first_sentence(self):
		"""
		Test that when getting the first sentence from text, only the first sentence is returned.
		"""

		text = "Memphis Depay (Dutch pronunciation: [ˈmɛmfɪs dəˈpɑi]; born 13 February 1994), \
				commonly known simply as Memphis,[2] is a Dutch professional \
				footballer and music artist who plays as a forward and captains \
				French club Lyon and plays for the Netherlands national team. \
				He is known for his pace, ability to cut inside, dribbling, \
				distance shooting and ability to play the ball off the ground."

		resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, [ ])
		self.assertEqual("Memphis Depay (Dutch pronunciation: [ˈmɛmfɪs dəˈpɑi]; born 13 February 1994), commonly known simply as Memphis,[2] is a Dutch professional footballer and music artist who plays as a forward and captains French club Lyon and plays for the Netherlands national team.",
						 re.sub('([ \t]+)', ' ', resolver._get_first_sentence(text)).strip())

	def test_get_first_sentence_full(self):
		"""
		Test that when getting the first sentence from a text that has only one sentence, the whole text is returned.
		"""

		text = "Youssouf Koné (born 5 July 1995) is a Malian professional footballer who plays for French side Olympique Lyonnais and the Mali national team as a left-back."

		resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, [ ])
		self.assertEqual(text, resolver._get_first_sentence(text))

	def test_get_first_sentence_full_without_period(self):
		"""
		Test that when getting the first sentence from a text that has only one sentence, but without punctuation, the whole text is returned.
		"""

		text = "Youssouf Koné (born 5 July 1995) is a Malian professional footballer who plays for French side Olympique Lyonnais and the Mali national team as a left-back"

		resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, [ ])
		self.assertEqual(text, resolver._get_first_sentence(text))
