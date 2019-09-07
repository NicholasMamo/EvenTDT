"""
Test the functionality of external postprocessors.
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
from libraries.apd.extrapolators.extrapolator import Extrapolator
from libraries.apd.extrapolators.external.wikipedia_extrapolator import LinkExtrapolator, WikipediaExtrapolator
from libraries.apd.postprocessors.external.wikipedia_postprocessor import WikipediaPostprocessor
from libraries.apd.resolvers.external.wikipedia_resolver import WikipediaResolver
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

class TestPostprocessors(unittest.TestCase):
	"""
	Test the implementation and results of the different postprocessors.
	"""

	@ignore_warnings
	def test_wikipedia_postprocessor(self):
		"""
		Test the wikipedia postprocessor.
		"""

		tokenizer = Tokenizer(case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)

		posts = [
			"Olympique Lyonnais' Moussa Dembélé on target twice in Dijon",
			"OL's Martin Terrier strike sinks Dijon"
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

		"""
		Default settings.
		"""
		participant_detector = ParticipantDetector(corpus, EntityExtractor, SumScorer, WikipediaResolver, Extrapolator, WikipediaPostprocessor)
		resolved, unresolved, extrapolated = participant_detector.detect(threshold=0.1,
			resolver_scheme=TFIDF(idf), resolver_threshold=0.1,
			extrapolator_scheme=TFIDF(idf), extrapolator_participants=30, extrapolator_threshold=0)

		self.assertTrue("Martin Terrier" in resolved)
		self.assertTrue("Dembele" in resolved)
		self.assertTrue("Dijon" in resolved)
		self.assertTrue("Olympique Lyonnais" in resolved)

		"""
		Retain full names.
		"""
		resolved, unresolved, extrapolated = participant_detector.detect(threshold=0.1,
			resolver_scheme=TFIDF(idf), resolver_threshold=0.1,
			extrapolator_scheme=TFIDF(idf), extrapolator_participants=30, extrapolator_threshold=0,
			postprocessor_surname_only=False)

		self.assertTrue("Martin Terrier" in resolved)
		self.assertTrue("Moussa Dembele" in resolved)
		self.assertTrue("Dijon" in resolved)
		self.assertTrue("Olympique Lyonnais" in resolved)

		"""
		Retain surnames only, but with disambiguation text.
		"""
		resolved, unresolved, extrapolated = participant_detector.detect(threshold=0.1,
			resolver_scheme=TFIDF(idf), resolver_threshold=0.1,
			extrapolator_scheme=TFIDF(idf), extrapolator_participants=30, extrapolator_threshold=0,
			postprocessor_surname_only=True, postprocessor_remove_disambiguation=False)

		self.assertTrue("Martin Terrier" in resolved)
		self.assertTrue("Dembele" in resolved)
		self.assertTrue("Dijon" in resolved)
		self.assertTrue("Olympique Lyonnais" in resolved)

		"""
		Retain surnames only, and do not remove the accents.
		"""
		resolved, unresolved, extrapolated = participant_detector.detect(threshold=0.1,
			resolver_scheme=TFIDF(idf), resolver_threshold=0.1,
			extrapolator_scheme=TFIDF(idf), extrapolator_participants=30, extrapolator_threshold=0,
			postprocessor_surname_only=True, postprocessor_remove_accents=False, postprocessor_remove_disambiguation=False)

		self.assertTrue("Martin Terrier" in resolved)
		self.assertTrue("Dembélé" in resolved)
		self.assertTrue("Dijon" in resolved)
		self.assertTrue("Olympique Lyonnais" in resolved)
