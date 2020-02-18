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

class TestTokenResolver(unittest.TestCase):
	"""
	Test the implementation and results of the token resolver.
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
		scores = ThresholdFilter(0).filter(scores)
		resolved, unresolved = TokenResolver().resolve(scores, corpus, tokenizer)

		self.assertTrue('manchester' in resolved)
		self.assertTrue('united' in resolved)
		self.assertTrue('tottenham' in resolved)
		self.assertTrue('hotspur' in resolved)

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
		scores = ThresholdFilter(0).filter(scores)
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
		scores = ThresholdFilter(0).filter(scores)
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
		scores = ThresholdFilter(0).filter(scores)
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
		scores = ThresholdFilter(0).filter(scores)
		resolved, unresolved = TokenResolver().resolve(scores, [ ], tokenizer)
		self.assertEqual(len(scores), len(unresolved))

	def test_case_folding(self):
		"""
		Test that when case-folding is set, the case does not matter.
		In this test, the stem 'report' can be formed by:

		    #. Reporters - appears twice
			#. reporters - appears twice
			#. reports - appears three times

		Without case-folding, 'reports' would be chosen to represent the token 'report'.
		'reports' appears three times, and 'Reporters' and 'reporters' appear twice.
		With case-folding, 'reports' still appears three times, but 'reporters' appears four times.
		"""

		"""
		Create the test data
		"""
		tokenizer = Tokenizer(min_length=1, stem=True)
		posts = [
			"Reporters Without Borders issue statement after reporters are harrassed",
			"Reporters left waiting all night long: reports",
			"Two reporters injured before gala: reports",
			"Queen reacts: reports of her falling ill exaggerated"
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		candidates = TokenExtractor().extract(corpus)
		scores = TFScorer().score(candidates)
		scores = ThresholdFilter(0).filter(scores)
		resolved, unresolved = TokenResolver().resolve(scores, corpus, tokenizer, case_fold=False)
		self.assertTrue('reports' in resolved)

		resolved, unresolved = TokenResolver().resolve(scores, corpus, tokenizer, case_fold=True)
		self.assertTrue('reporters' in resolved)
