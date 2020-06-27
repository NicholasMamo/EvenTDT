"""
Test the functionality of the TF-DCF extractor functions.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate.stat import TFExtractor
from ate.stat.corpus.tfdcf import TFDCFExtractor
from ate import linguistic

class TestTFDCFExtractor(unittest.TestCase):
	"""
	Test the functionality of the TF-DCF extractor functions.
	"""

	def test_extract(self):
		"""
		Test that the extracted terms make sense.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = TFDCFExtractor(general)
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

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = TFDCFExtractor(general)
		terms = extractor.extract(corpora)
		self.assertLess(0, min(terms.values()))

	def test_extract_accumulates(self):
		"""
		Test that when multiple corpora are given, the scores accumulate.
		"""

		corpora = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json'),
		 			os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB.json') ]
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = TFDCFExtractor(general)
		terms_1 = extractor.extract(corpora[0])
		terms_2 = extractor.extract(corpora[1])
		terms_combined = extractor.extract(corpora)

		for term, score in terms_combined.items():
			self.assertEqual(round(score, 5), round(terms_1.get(term, 0) + terms_2.get(term, 0), 5))

	def test_extract_all_multiple_corpora(self):
		"""
		Test that the TF-DCF extractor extracts all terms from multiple corpora.
		"""

		corpora = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json'),
		 			os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB.json') ]
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = TFDCFExtractor(general)
		terms_1 = extractor.extract(corpora[0])
		terms_2 = extractor.extract(corpora[1])
		terms_combined = extractor.extract(corpora)
		self.assertTrue(all( term in terms_combined for term in terms_1 ))

	def test_extract_all(self):
		"""
		Test that the TF-DCF extractor extracts all terms.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		vocabulary = linguistic.vocabulary(corpora)
		extractor = TFDCFExtractor(general)
		terms = extractor.extract(corpora)
		self.assertTrue(all( term in terms for term in vocabulary ))

	def test_extract_candidates(self):
		"""
		Test that the TF-DCF extractor extracts scores for only select candidates if they are given.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = TFDCFExtractor(general)
		terms = extractor.extract(corpora, candidates=[ 'chelsea', 'goal' ])
		self.assertEqual({ 'chelsea', 'goal' }, set(terms.keys()))

	def test_extract_candidates_same_scores(self):
		"""
		Test that the TF-DCF extractor's scores for known candidates are the same as when candidates are not given.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = TFDCFExtractor(general)
		candidate_terms = extractor.extract(corpora, candidates=[ 'chelsea', 'goal' ])
		terms = extractor.extract(corpora)
		self.assertEqual(terms['chelsea'], candidate_terms['chelsea'])
		self.assertEqual(terms['goal'], candidate_terms['goal'])

	def test_extract_candidates_unknown_word(self):
		"""
		Test that the TF-DCF extractor's score for an unknown word is 0.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = TFDCFExtractor(general)
		terms = extractor.extract(corpora, candidates=[ 'superlongword' ])
		self.assertEqual({ 'superlongword': 0 }, terms)

	def test_extract_general_product(self):
		"""
		Test that the general corpora's scores are multiplied together.
		"""

		corpora = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json'),
		 			os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB.json') ]
		general = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json'),
					os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-2.json') ]

		extractor = TFDCFExtractor(general)
		combined = extractor.extract(corpora)

		"""
		Extract the term scores separately with each general dataset.
		Then, extract the TF separately.
		Later, they will be combined.
		"""
		extractor = TFDCFExtractor(general[0])
		terms_1 = extractor.extract(corpora)
		extractor = TFDCFExtractor(general[1])
		terms_2 = extractor.extract(corpora)
		extractor = TFExtractor()
		tf = extractor.extract(corpora)

		"""
		Divide by the TF because the multiplication applies for the numerator and denominator.
		The TF in the numerator should not be multiplied, however.
		"""
		self.assertTrue(all( round(combined[term], 5) == round(terms_1[term] * terms_2[term] / tf[term], 5)
							 for term in combined ))
