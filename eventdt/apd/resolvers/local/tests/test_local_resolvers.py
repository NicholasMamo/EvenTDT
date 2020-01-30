"""
Test the functionality of local resolvers.
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

from libraries.apd.participant_detector import ParticipantDetector
from libraries.apd.extractors.local.entity_extractor import EntityExtractor
from libraries.apd.extractors.local.token_extractor import TokenExtractor
from libraries.apd.scorers.local.sum_scorer import SumScorer
from libraries.apd.resolvers.local.token_resolver import TokenResolver
from libraries.apd.resolvers.local.entity_resolver import EntityResolver

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

class TestResolvers(unittest.TestCase):
	"""
	Test the implementation and results of the different resolvers.
	"""

	@ignore_warnings
	def test_token_resolver(self):
		"""
		Test the token resolver.
		"""

		tokenizer = Tokenizer(min_length=1, stem=False)
		posts = [
			"Manchester United falter against Tottenham Hotspur",
			"Manchester United unable to avoid defeat to Tottenham",
			"Manchester United lost to Tottenham Hotspur",
			"Mourinho under pressure as Manchester United follow with a loss",
			"Manchester United powerless in loss to Tottenham",
			"Lucas Moura punishes United",
			"Manchester United manager Jose Mourinho sacked tomorrow?",
			"Luke Shaw was the only bright spot in dim Manchester United",
			"Selfie this: Tottenham Hotspur star Lucas Moura pictured with Manchester United fans",
			"Beginning of a crisis for Jose Mourinho's Manchester United?",
			"Pochettino hails Lucas Moura and Harry Kane"
		]

		corpus = [] # the corpus of documents
		for post in posts:
			tokens = tokenizer.tokenize(post)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)

		tokens = list(set([ token for document in corpus for token in document.get_attribute("tokens") ]))

		participant_detector = ParticipantDetector(corpus, TokenExtractor, SumScorer, TokenResolver)
		resolved, unresolved, extrapolated = participant_detector.detect()

		self.assertTrue(len(resolved) <= len(tokens))

	@ignore_warnings
	def test_entity_resolver(self):
		"""
		Test the entity resolver.
		"""

		tokenizer = Tokenizer(stopwords=stopwords.words("english"))
		posts = [
			"Manchester United falter against Tottenham Hotspur",
			"Manchester United unable to avoid defeat to Tottenham",
			"Manchester United lost to Tottenham Hotspur",
			"Mourinho under pressure as Manchester United follow with a loss",
			"Manchester United powerless in loss to Tottenham",
			"Lucas Moura punishes United",
			"Manchester United manager Jose Mourinho sacked tomorrow?",
			"Luke Shaw was the only bright spot in dim Manchester United",
			"Selfie this: Tottenham Hotspur star Lucas Moura pictured with Manchester United fans",
			"Beginning of a crisis for Jose Mourinho's Manchester United?",
			"Pochettino hails Lucas Moura and Harry Kane"
		]

		named_entities, corpus = [], [] # the corpus of documents
		for post in posts:
			tokens = tokenizer.tokenize(post)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)
		entities = list(set([ entity for entity_set in EntityExtractor().extract(corpus) for entity in entity_set ]))
		tokens = list(set([ token for document in corpus for token in document.get_attribute("tokens") ]))

		participant_detector = ParticipantDetector(corpus, EntityExtractor, SumScorer, EntityResolver)
		resolved, unresolved, extrapolated = participant_detector.detect()

		self.assertEqual(len(resolved) + len(unresolved), 8)

		"""
		Repeat the test, but this time using a token extractor.
		"""

		named_entities, corpus = [], [] # the corpus of documents
		for post in posts:
			tokens = tokenizer.tokenize(post)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)

		tokens = list(set([ token for document in corpus for token in document.get_attribute("tokens") ]))

		participant_detector = ParticipantDetector(corpus, TokenExtractor, SumScorer, EntityResolver)
		resolved, unresolved, extrapolated = participant_detector.detect()

		self.assertTrue(all([ entity in entities for entity in resolved ]))
