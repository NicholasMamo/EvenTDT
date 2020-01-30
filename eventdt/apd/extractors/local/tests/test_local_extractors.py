"""
Test the functionality of local extractors.
"""

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
from libraries.apd.extractors.local.token_extractor import TokenExtractor

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

class TestExtractors(unittest.TestCase):
	"""
	Test the implementation and results of the different extractors.
	"""

	@ignore_warnings
	def test_entity_extractor(self):
		"""
		Test the entity extractor.
		"""

		extractor = EntityExtractor()
		tokenizer = Tokenizer(case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)

		posts = [
			"Manchester United falter against Tottenham Hotspur",
			"Mourinho under pressure as Manchester United follow with a loss",
		]

		corpus = [] # the corpus of documents
		for post in posts:
			tokens = tokenizer.tokenize(post)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)

		candidates = extractor.extract(corpus)
		self.assertEqual(candidates[0], ["united", "tottenham hotspur"])
		self.assertEqual(candidates[1], ["mourinho", "manchester united"])

	@ignore_warnings
	def test_token_extractor(self):
		"""
		Test the token extractor.
		"""

		extractor = TokenExtractor()
		tokenizer = Tokenizer(stopwords=stopwords.words("english"))

		posts = [
			"Manchester United falter against Tottenham Hotspur",
			"Mourinho under pressure as Manchester United follow with a loss",
		]

		corpus = [] # the corpus of documents
		for post in posts:
			tokens = tokenizer.tokenize(post)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)

		candidates = extractor.extract(corpus)
		self.assertEqual(candidates[0], ["manchest", "unit", "falter", "tottenham", "hotspur"])
		self.assertEqual(candidates[1], ["mourinho", "pressur", "manchest", "unit", "follow", "loss"])
