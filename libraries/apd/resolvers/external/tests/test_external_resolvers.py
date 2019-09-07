"""
Test the functionality of external resolvers.
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
from libraries.apd.resolvers.external.wikipedia_resolver import SearchResolver, WikipediaResolver
from libraries.apd.scorers.local.sum_scorer import SumScorer

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
	def test_search_resolve(self):
		"""
		Test the Search resolver.
		"""

		tokenizer = Tokenizer(case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)

		posts = [
			"Manchester United falter against Tottenham Hotspur",
			"Manchester United unable to avoid defeat to Tottenham Hotspur",
			"Manchester United lost to Tottenham Hotspur",
			"Mourinho under pressure as Manchester United follow with a loss",
			"Manchester United powerless in loss to Tottenham Hotspur",
			"Lucas Moura punishes United",
			"Manchester United manager Jose Mourinho sacked tomorrow?",
			"Luke Shaw was the only bright spot in dim Manchester United",
			"Selfie this: Tottenham star Lucas Moura pictured with Manchester United fans",
			"Beginning of a crisis for Jose Mourinho's Manchester United?",
			"Pochettino hails Lucas Moura and Harry Kane"
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
		}

		corpus = [] # the corpus of documents
		for post in posts:
			tokens = tokenizer.tokenize(post)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)

		participant_detector = ParticipantDetector(corpus, EntityExtractor, SumScorer, SearchResolver)
		resolved, unresolved, _ = participant_detector.detect(resolver_scheme=TFIDF(idf))

		self.assertEqual(unresolved, [])
		self.assertTrue('Harry Kane' in resolved)
		self.assertTrue('Mauricio Pochettino' in resolved)
		self.assertTrue('José Mourinho' in resolved)
		self.assertTrue('Lucas Moura' in resolved)
		self.assertTrue('Luke Shaw' in resolved)
		self.assertTrue('Tottenham Hotspur F.C.' in resolved)

	@ignore_warnings
	def test_wikipedia_resolve(self):
		"""
		Test the Wikipedia resolver.
		"""

		tokenizer = Tokenizer(case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)

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
		}

		corpus = [] # the corpus of documents
		for post in posts:
			tokens = tokenizer.tokenize(post)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)

		participant_detector = ParticipantDetector(corpus, EntityExtractor, SumScorer, WikipediaResolver)
		resolved, unresolved, _ = participant_detector.detect(resolver_scheme=TFIDF(idf))

		self.assertEqual(unresolved, [])
		self.assertEqual(set(resolved), set(['Harry Kane', 'Mauricio Pochettino', 'Selfie', 'Lucas Moura', 'José Mourinho', 'Tottenham Hotspur', 'Manchester United', 'Pochettino', 'Jose Mourinho', 'Tottenham Hotspur F.C.', 'Manchester United F.C.', 'Luke Shaw']))
