"""
Test the functionality of the TF extractor.
"""

import json
import os
import string
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
 		  os.path.join(os.path.dirname(__file__), '..', '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

from ate import linguistic
from ate.stat import TFExtractor
from objects.exportable import Exportable

class TestTFExtractor(unittest.TestCase):
	"""
	Test the functionality of the TF extractor.
	"""

	def test_extract(self):
		"""
		Test that the extracted terms make sense.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')

		extractor = TFExtractor()
		terms = extractor.extract(corpora)
		terms = sorted(terms, key=terms.get, reverse=True)
		self.assertTrue('chelsea' in terms[:10])
		self.assertTrue('crystal' in terms[:10])
		self.assertTrue('palac' in terms[:10])
		self.assertTrue('crych' in terms[:10])
		self.assertTrue('kant' in terms[:10])

	def test_extract_positive(self):
		"""
		Test that the scores of all extracted terms are positive.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')

		extractor = TFExtractor()
		terms = extractor.extract(corpora)
		self.assertLess(0, min(terms.values()))

	def test_extract_integers(self):
		"""
		Test that the scores of all extracted terms are integers.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')

		extractor = TFExtractor()
		terms = extractor.extract(corpora)
		self.assertTrue(all( not score % 1 for score in terms.values() ))

	def test_extract_accumulates(self):
		"""
		Test that when multiple corpora are given, the scores accumulate.
		"""

		corpora = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json'),
		 			os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB.json') ]

		extractor = TFExtractor()
		terms_1 = extractor.extract(corpora[0])
		terms_2 = extractor.extract(corpora[1])
		terms_combined = extractor.extract(corpora)

		for term, score in terms_combined.items():
			self.assertEqual(round(score, 5), round(terms_1.get(term, 0) + terms_2.get(term, 0), 5))

	def test_extract_all_multiple_corpora(self):
		"""
		Test that the TF extractor extracts all terms from multiple corpora.
		"""

		corpora = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json'),
		 			os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB.json') ]

		extractor = TFExtractor()
		terms_1 = extractor.extract(corpora[0])
		terms_2 = extractor.extract(corpora[1])
		terms_combined = extractor.extract(corpora)
		self.assertTrue(all( term in terms_combined for term in terms_1 ))
		self.assertTrue(all( term in terms_combined for term in terms_2 ))

	def test_extract_all(self):
		"""
		Test that the TF extractor extracts all terms.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')

		vocabulary = linguistic.vocabulary(corpora)
		extractor = TFExtractor()
		terms = extractor.extract(corpora)
		self.assertTrue(all( term in terms for term in vocabulary ))

	def test_extract_candidates(self):
		"""
		Test that the TF extractor extracts scores for only select candidates if they are given.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')

		extractor = TFExtractor()
		terms = extractor.extract(corpora, candidates=[ 'chelsea', 'goal' ])
		self.assertEqual({ 'chelsea', 'goal' }, set(terms.keys()))

	def test_extract_candidates_same_scores(self):
		"""
		Test that the TF extractor's scores for known candidates are the same as when candidates are not given.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')

		extractor = TFExtractor()
		candidate_terms = extractor.extract(corpora, candidates=[ 'chelsea', 'goal' ])
		terms = extractor.extract(corpora)
		self.assertEqual(terms['chelsea'], candidate_terms['chelsea'])
		self.assertEqual(terms['goal'], candidate_terms['goal'])

	def test_extract_candidates_unknown_word(self):
		"""
		Test that the TF extractor's score for an unknown word is 0.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')

		extractor = TFExtractor()
		terms = extractor.extract(corpora, candidates=[ 'superlongword' ])
		self.assertEqual({ 'superlongword': 0 }, terms)
