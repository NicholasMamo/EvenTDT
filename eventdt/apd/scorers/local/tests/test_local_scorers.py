"""
Test the functionality of local scorers.
The strategy is to simulate the participant detection process to test the intermediate scoring step.
"""

import math
import os
import sys
import unittest
import warnings

path = os.path.dirname(__file__)
path = os.path.join(path, '../../')
if path not in sys.path:
	sys.path.append(path)

from nltk.corpus import stopwords

from libraries.apd.extractors.local.entity_extractor import EntityExtractor
from libraries.apd.scorers.local.idf_scorer import IDFScorer
from libraries.apd.scorers.local.sum_scorer import LogSumScorer, SumScorer

from libraries.vector.nlp.document import Document
from libraries.vector.nlp.tokenizer import Tokenizer
from libraries.vector.nlp.term_weighting import TF, TFIDF

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

class TestScorers(unittest.TestCase):
	"""
	Test the implementation and results of the different scorers.
	"""

	@ignore_warnings
	def test_idf_scorer(self):
		"""
		Test the IDF scorer.
		"""

		extractor = EntityExtractor()
		scorer = IDFScorer()
		tokenizer = Tokenizer(case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)

		posts = [
			"Manchester United falter against Tottenham Hotspur",
			"Mourinho under pressure as Manchester United follow with a loss",
		]

		idf = {
			"DOCUMENTS": 100,
			"crisis": 12,
			"bright": 10,
			"selfie": 5,
			"power": 8,
			"pressure": 5,
			"defeat": 8,
			"fall": 7,
			"falter": 2,
			"spot": 3,
			"dim": 7,
			"spur": 1,
			"against": 10,
			"tomorrow": 3,
			"sack": 2,
			"follow": 8,
			"mourinho": 10,
		}

		idf = { ("a" + key if not key == "DOCUMENTS" else key): value
			for key, value in idf.items() }

		corpus = [] # the corpus of documents
		for post in posts:
			tokens = tokenizer.tokenize(post)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)

		candidates = extractor.extract(corpus)
		self.assertEqual(candidates[0], ["united", "tottenham hotspur"])
		self.assertEqual(candidates[1], ["mourinho", "manchester united"])

		scores = scorer.score(candidates, idf)
		self.assertEqual(scores["united"], 1)
		self.assertEqual(scores["tottenham hotspur"], 1)
		self.assertEqual(scores["mourinho"], 1)
		self.assertEqual(scores["manchester united"], 1)

	@ignore_warnings
	def test_sum_scorer(self):
		"""
		Test the sum scorer.
		"""

		extractor = EntityExtractor()
		scorer = SumScorer()
		tokenizer = Tokenizer(case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)

		posts = [
			"Manchester United falter against Tottenham Hotspur",
			"Manchester United powerless in loss to Tottenham",
			"Mourinho under pressure as Manchester United follow with a loss",
		]

		corpus = [] # the corpus of documents
		for post in posts:
			tokens = tokenizer.tokenize(post)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)

		candidates = extractor.extract(corpus)
		self.assertEqual(candidates[0], ["united", "tottenham hotspur"])
		self.assertEqual(candidates[1], ["united"])
		self.assertEqual(candidates[2], ["mourinho", "manchester united"])

		scores = scorer.score(candidates)
		self.assertEqual(scores["united"], 1)
		self.assertEqual(scores["tottenham hotspur"], 0.5)
		self.assertEqual(scores["mourinho"], 0.5)
		self.assertEqual(scores["manchester united"], 0.5)

	@ignore_warnings
	def test_log_sum_scorer(self):
		"""
		Test the log sum scorer.
		"""

		extractor = EntityExtractor()
		scorer = LogSumScorer()
		tokenizer = Tokenizer(case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)

		posts = [
			"Manchester United falter against Tottenham Hotspur",
			"Manchester United powerless in loss to Tottenham",
			"Mourinho under pressure as Manchester United follow with a loss",
		]

		corpus = [] # the corpus of documents
		for post in posts:
			tokens = tokenizer.tokenize(post)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)

		candidates = extractor.extract(corpus)
		self.assertEqual(candidates[0], ["united", "tottenham hotspur"])
		self.assertEqual(candidates[1], ["united"])
		self.assertEqual(candidates[2], ["mourinho", "manchester united"])

		scores = scorer.score(candidates)
		self.assertEqual(scores["united"], 1)
		self.assertEqual(scores["tottenham hotspur"], math.log(2, 10)/math.log(3, 10))
		self.assertEqual(scores["mourinho"], math.log(2, 10)/math.log(3, 10))
		self.assertEqual(scores["manchester united"], math.log(2, 10)/math.log(3, 10))
