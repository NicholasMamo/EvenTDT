"""
Test the functionality of the token resolver.
"""

import os
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nltk.corpus import stopwords

from apd.extractors.local.entity_extractor import EntityExtractor
from apd.extractors.local.token_extractor import TokenExtractor
from apd.scorers.local.tf_scorer import TFScorer
from apd.filters.local.threshold_filter import ThresholdFilter
from apd.resolvers.local.token_resolver import TokenResolver

from nlp.document import Document
from nlp.tokenizer import Tokenizer

class TestResolvers(unittest.TestCase):
	"""
	Test the implementation and results of the different resolvers.
	"""

	def test_token_resolver(self):
		"""
		Test the token resolver.
		"""

		"""
		Create the test data
		"""
		tokenizer = Tokenizer(min_length=1, stem=False)
		posts = [
			"Manchester United falter against Tottenham Hotspur",
			"Manchester United unable to avoid defeat to Tottenham",
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		candidates = TokenExtractor().extract(corpus)
		scores = TFScorer().score(candidates)
		scores = ThresholdFilter().filter(scores, 0)
		resolved, unresolved = TokenResolver().resolve(scores, corpus, tokenizer)

		self.assertTrue('Manchester' in resolved)
		self.assertTrue('United' in resolved)
		self.assertTrue('Tottenham' in resolved)
		self.assertTrue('Hotspur' in resolved)

	def test_reuse_tokenizer(self):
		"""
		Test that when the tokenizer is re-used, no candidates should be unresolved.
		"""

		"""
		Create the test data
		"""
		tokenizer = Tokenizer(min_length=1, stem=False)
		posts = [
			"Manchester United falter against Tottenham Hotspur",
			"Manchester United unable to avoid defeat to Tottenham",
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		candidates = TokenExtractor().extract(corpus)
		scores = TFScorer().score(candidates)
		scores = ThresholdFilter().filter(scores, 0)
		resolved, unresolved = TokenResolver().resolve(scores, corpus, tokenizer)

		self.assertEqual(len(scores), len(resolved))

	def test_different_tokenizer(self):
		"""
		Test that when a different tokenizer is used than the one used in extraction, it is used.
		"""

		"""
		Create the test data
		"""
		tokenizer = Tokenizer(min_length=1, stem=False)
		posts = [
			"Manchester United falter against Tottenham Hotspur",
			"Manchester United unable to avoid defeat to Tottenham",
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		candidates = TokenExtractor().extract(corpus)
		scores = TFScorer().score(candidates)
		scores = ThresholdFilter().filter(scores, 0)
		resolved, unresolved = TokenResolver().resolve(scores, corpus, tokenizer)
		self.assertTrue('to' in resolved)

		resolved, unresolved = TokenResolver().resolve(scores, corpus, Tokenizer(min_length=3, stem=False))
		self.assertTrue('to' in unresolved)

	def test_unknown_token(self):
		"""
		Test that when an unknown candidate is given, it is unresolved.
		"""

		"""
		Create the test data
		"""
		tokenizer = Tokenizer(min_length=1, stem=False)
		posts = [
			"Manchester United falter against Tottenham Hotspur",
			"Manchester United unable to avoid defeat to Tottenham",
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		candidates = TokenExtractor().extract(corpus)
		scores = TFScorer().score(candidates)
		scores = ThresholdFilter().filter(scores, 0)
		resolved, unresolved = TokenResolver().resolve({ 'unknown': 1 }, corpus, tokenizer)
		self.assertTrue('unknown' in unresolved)

	def test_empty_corpus(self):
		"""
		Test that when an empty corpus is given, all candidates are unresolved.
		"""

		"""
		Create the test data
		"""
		tokenizer = Tokenizer(min_length=1, stem=False)
		posts = [
			"Manchester United falter against Tottenham Hotspur",
			"Manchester United unable to avoid defeat to Tottenham",
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		candidates = TokenExtractor().extract(corpus)
		scores = TFScorer().score(candidates)
		scores = ThresholdFilter().filter(scores, 0)
		resolved, unresolved = TokenResolver().resolve(scores, [ ], tokenizer)
		self.assertEqual(len(scores), len(unresolved))
