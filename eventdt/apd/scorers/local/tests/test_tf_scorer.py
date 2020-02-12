"""
Test the functionality of the TF scorer.
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
from apd.scorers.local.tf_scorer import TFScorer

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

class TestTFScorer(unittest.TestCase):
	"""
	Test the implementation and results of the TF scorer.
	"""

	@ignore_warnings
	def test_tf_scorer(self):
		"""
		Test the basic functionality of the TF scorer.
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
		scorer = TFScorer()
		candidates = extractor.extract(corpus)
		scores = scorer.score(candidates)
		self.assertEqual(1, scores.get('erdogan', 0))
		self.assertEqual(0.5, scores.get('damascus', 0))
		self.assertEqual(1, scores.get('threats', 0))

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
		scorer = TFScorer()
		candidates = extractor.extract(corpus)
		scores = scorer.score(candidates)
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
		scorer = TFScorer()
		candidates = extractor.extract(corpus)
		scores = scorer.score(candidates)
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
		scorer = TFScorer()
		candidates = extractor.extract(corpus)
		scores = scorer.score(candidates)
		self.assertFalse(scores.get('unknown'))

	@ignore_warnings
	def test_score_across_multiple_documents(self):
		"""
		Test that the score is based on term frequency.
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
		scorer = TFScorer()
		candidates = extractor.extract(corpus, tokenizer=tokenizer)
		scores = scorer.score(candidates, normalize_scores=False)
		self.assertEqual(3, scores.get('erdogan'))

	@ignore_warnings
	def test_normalization(self):
		"""
		Test that when normalization is disabled, the returned scores are integers.
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
		scorer = TFScorer()
		candidates = extractor.extract(corpus)
		scores = scorer.score(candidates, normalize_scores=False)
		self.assertEqual(2, scores.get('erdogan'))

	@ignore_warnings
	def test_repeated_tokens(self):
		"""
		Test that when tokens are repeated, the frequency that is returned is the term frequency.
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
		scorer = TFScorer()
		candidates = extractor.extract(corpus, tokenizer=tokenizer)
		scores = scorer.score(candidates, normalize_scores=False)
		self.assertEqual(2, scores.get('erdogan'))
