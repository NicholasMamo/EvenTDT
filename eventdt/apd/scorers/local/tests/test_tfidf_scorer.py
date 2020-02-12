"""
Test the functionality of the TF-IDF scorer.
"""

import math
import os
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from apd.extractors.local.token_extractor import TokenExtractor
from apd.scorers.local.tfidf_scorer import TFIDFScorer

from nlp.document import Document
from nlp.tokenizer import Tokenizer

def ignore_warnings(test):
	"""
	A decorator function used to ignore NLTK warnings
	From: http://www.neuraldump.net/2017/06/how-to-suppress-python-unittest-warnings/
	More about decorator functions: https://wiki.python.org/moin/PythonDecorators

	:param test: The test to perform.
	:type test: func

	:return: The function output.
	:rtype: obj
	"""
	def perform_test(self, *args, **kwargs):
		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			test(self, *args, **kwargs)
	return perform_test

class TestTFIDFScorer(unittest.TestCase):
	"""
	Test the implementation and results of the TF-IDF scorer.
	"""

	@ignore_warnings
	def test_tfidf_scorer(self):
		"""
		Test the basic functionality of the TF-IDF scorer.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"Erdogan with threats to attack regime forces 'everywhere' in Syria",
			"Damascus says Erdogan 'disconnected from reality' after threats",
		]

		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = TokenExtractor()
		scorer = TFIDFScorer({ 'erdogan': 1, 'threats': 2 }, 10)
		candidates = extractor.extract(corpus, tokenizer=tokenizer)
		scores = scorer.score(candidates)
		self.assertGreater(scores.get('erdogan'), scores.get('damascus'))
		self.assertEqual(scores.get('everywhere'), scores.get('disconnected')) # they appear the same number of times
		self.assertGreater(scores.get('erdogan'), scores.get('threats')) # 'threats' and 'erdogan' appear with the same frequency, but 'threats' has a higher DF

	@ignore_warnings
	def test_min_score(self):
		"""
		Test that the minimum score is greater than 0.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"Erdogan with threats to attack regime forces 'everywhere' in Syria",
			"Damascus says Erdogan 'disconnected from reality' after threats",
		]

		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = TokenExtractor()
		scorer = TFIDFScorer({ 'erdogan': 1, 'threats': 2 }, 10)
		candidates = extractor.extract(corpus)
		scores = scorer.score(candidates, normalize_scores=True)
		self.assertTrue(all( score > 0 for score in scores.values() ))

	@ignore_warnings
	def test_max_score(self):
		"""
		Test that the maximum score is 1 when normalization is enabled.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"Erdogan with threats to attack regime forces 'everywhere' in Syria",
			"Damascus says Erdogan 'disconnected from reality' after threats",
		]

		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = TokenExtractor()
		scorer = TFIDFScorer({ 'erdogan': 1, 'threats': 2 }, 10)
		candidates = extractor.extract(corpus)
		scores = scorer.score(candidates, normalize_scores=True)
		self.assertTrue(all( score <= 1 for score in scores.values() ))

	@ignore_warnings
	def test_score_of_unknown_token(self):
		"""
		Test that the score of an unknown token is 0.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"Erdogan with threats to attack regime forces 'everywhere' in Syria",
			"Damascus says Erdogan 'disconnected from reality' after threats",
		]

		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = TokenExtractor()
		scorer = TFIDFScorer({ 'erdogan': 1, 'threats': 2 }, 10)
		candidates = extractor.extract(corpus)
		scores = scorer.score(candidates)
		self.assertFalse(scores.get('unknown'))

	@ignore_warnings
	def test_score_across_multiple_documents(self):
		"""
		Test that the score is based on document frequency.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"Erdogan with threats to attack regime forces 'everywhere' in Syria",
			"Syria reacts to Erdogan's threats: Damascus says Erdogan 'disconnected from reality' after threats",
		]

		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = TokenExtractor()
		scorer = TFIDFScorer({ 'erdogan': 1, 'threats': 2 }, 10)
		candidates = extractor.extract(corpus, tokenizer=tokenizer)
		scores = scorer.score(candidates, normalize_scores=False)
		self.assertEqual(3 * math.log(10 / 1, 10), scores.get('erdogan'))
		self.assertEqual(3 * math.log(10 / 2, 10), scores.get('threats'))

	@ignore_warnings
	def test_normalization(self):
		"""
		Test that when normalization is enabled, the returned scores are integers.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"Erdogan with threats to attack regime forces 'everywhere' in Syria",
			"After Erdogan's statement, Damascus says Erdogan 'disconnected from reality' after threats",
		]

		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = TokenExtractor()
		scorer = TFIDFScorer({ 'erdogan': 1, 'threats': 2 }, 10)
		candidates = extractor.extract(corpus, tokenizer=tokenizer)
		scores = scorer.score(candidates, normalize_scores=True)
		self.assertEqual(1, scores.get('erdogan'))

	@ignore_warnings
	def test_repeated_tokens(self):
		"""
		Test that when tokens are repeated, the frequency that is returned is the document frequency.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"After Erdogan's statement, Damascus says Erdogan 'disconnected from reality' after threats",
		]

		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = TokenExtractor()
		scorer = TFIDFScorer({ 'erdogan': 3, 'threats': 2 }, 10)
		candidates = extractor.extract(corpus, tokenizer=tokenizer)
		scores = scorer.score(candidates, normalize_scores=False)
		self.assertEqual(2 * math.log(10 / 3, 10), scores.get('erdogan'))
