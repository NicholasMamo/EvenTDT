"""
Test the functionality of the rank difference extractor functions.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate.stat import probability, TFExtractor
from ate.stat.corpus import RankExtractor
from ate import linguistic

class TestRankExtractor(unittest.TestCase):
	"""
	Test the functionality of the rank difference extractor functions.
	"""

	def test_extract(self):
	def test_cutoff_str(self):
		"""
		Test that the rank extractor does not accept a string cutoff value.
		"""

		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')
		self.assertRaises(ValueError, RankExtractor, general, "1")

	def test_cutoff_float(self):
		"""
		Test that the rank extractor does not accept a float cutoff value.
		"""

		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')
		self.assertRaises(ValueError, RankExtractor, general, 1.0)

	def test_cutoff_zero(self):
		"""
		Test that the rank extractor does not accept a cutoff value of zero.
		"""

		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')
		self.assertRaises(ValueError, RankExtractor, general, 0)

	def test_cutoff_negative(self):
		"""
		Test that the rank extractor does not accept a negative cutoff value.
		"""

		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')
		self.assertRaises(ValueError, RankExtractor, general, -1)

	def test_cutoff_positive(self):
		"""
		Test that the rank extractor accepts a positive cutoff value.
		"""

		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')
		self.assertTrue(RankExtractor(general, 1))

		"""
		Test that the extracted terms make sense.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json'),
					os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-2.json') ]

		extractor = RankExtractor(general)
		terms = extractor.extract(corpora)
		terms = sorted(terms, key=terms.get, reverse=True)
		self.assertTrue('chelsea' in terms[:10])
		self.assertTrue('hazard' in terms[:10])
		self.assertTrue('willian' in terms[:10])

	def test_extract_upper_bound(self):
		"""
		Test that no score is greater than 1.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json')
		general = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json'),
					os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-2.json') ]

		"""
		Ensure that the top domain term is not in the general corpora.
		"""
		extractor = TFExtractor()
		terms = extractor.extract(corpora)
		self.assertTrue(max(terms, key=terms.get) not in extractor.extract(general))

		extractor = RankExtractor(general)
		terms = extractor.extract(corpora)
		self.assertEqual(1, max(terms.values()))
		self.assertTrue(all( score <= 1 for score in terms.values() ))

	def test_extract_lower_bound(self):
		"""
		Test that no score is less than or equal to -1.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json')
		general = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json'),
					os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-2.json') ]

		extractor = RankExtractor(general)
		terms = extractor.extract(corpora)
		self.assertTrue(all( score > -1 for score in terms.values() ))

	def test_extract_negative(self):
		"""
		Test that scores may be negative.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json')
		general = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json'),
					os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-2.json') ]

		extractor = RankExtractor(general)
		terms = extractor.extract(corpora)
		self.assertTrue(any( score < 0 for score in terms.values() ))

	def test_extract_all(self):
		"""
		Test that the rank difference extractor extracts all terms from the vocabulary.
		"""

		corpora = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
		 			os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = RankExtractor(general)
		terms = extractor.extract(corpora)
		vocabulary = linguistic.vocabulary(corpora)
		self.assertTrue(all( term in terms for term in vocabulary ))

	def test_extract_all_multiple_corpora(self):
		"""
		Test that the rank difference extractor extracts all terms from multiple corpora.
		"""

		corpora = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
		 			os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = RankExtractor(general)
		terms_1 = extractor.extract(corpora[0])
		terms_2 = extractor.extract(corpora[1])
		terms_combined = extractor.extract(corpora)
		self.assertTrue(all( term in terms_combined for term in terms_1 ))
		self.assertTrue(all( term in terms_combined for term in terms_2 ))

	def test_extract_candidates(self):
		"""
		Test that the rank difference extractor extracts scores for only select candidates if they are given.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = RankExtractor(general)
		terms = extractor.extract(corpora, candidates=[ 'chelsea', 'goal' ])
		self.assertEqual({ 'chelsea', 'goal' }, set(terms.keys()))

	def test_extract_candidate_unknown(self):
		"""
		Test that when extracting a candidate that does not appear in the domain or background, its score is zero.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = RankExtractor(general)
		terms = extractor.extract(corpora, candidates=[ 'chelsea', 'goal', 'superlongword' ])
		self.assertEqual(0, terms['superlongword'])

	def test_extract_empty_general(self):
		"""
		Test that when extracting terms with an empty general corpus, all scores are positive.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'empty.json')

		extractor = RankExtractor(general)
		terms = extractor.extract(corpora)
		self.assertTrue(all( score > 0 for score in terms.values() ))

	def test_rank_empty_dict(self):
	def test_filter_cutoff_1(self):
		"""
		Test that when the cutoff is 1, the same input dictionary is returned after filtering.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json')
		general = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json'),
					os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-2.json') ]

		extractor = TFExtractor()
		terms = extractor.extract(corpora)
		extractor = RankExtractor(general, cutoff=1)
		self.assertEqual(terms, extractor._filter_terms(terms))

	def test_filter_cutoff_inclusive(self):
		"""
		Test that the cutoff value is inclusive when filtering terms.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json')
		general = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json'),
					os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-2.json') ]

		extractor = TFExtractor()
		terms = extractor.extract(corpora)
		extractor = RankExtractor(general, cutoff=2)
		self.assertEqual(2, min(extractor._filter_terms(terms).values()))

	def test_filter_cutoff_all_equal_greater(self):
		"""
		Test that when filtering, all terms with a value greater than or equal to the cutoff value are retained.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json')
		general = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json'),
					os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-2.json') ]

		extractor = TFExtractor()
		terms = extractor.extract(corpora)
		extractor = RankExtractor(general, cutoff=2)
		filtered = extractor._filter_terms(terms)
		for term, score in terms.items():
			if score >= 2:
				self.assertTrue(term in filtered)
				self.assertTrue(filtered[term] == score)

	def test_filter_input_unchanged(self):
		"""
		Test that when filtering, the input dictionary is not changed.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json')
		general = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json'),
					os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-2.json') ]

		extractor = TFExtractor()
		terms = extractor.extract(corpora)
		copy = dict(terms)
		extractor = RankExtractor(general, cutoff=2)
		filtered = extractor._filter_terms(terms)
		self.assertEqual(copy, terms)

		"""
		Test that when ranking an empty dictionary, an empty dictionary is returned.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'empty.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = RankExtractor(general)
		p = probability.p(corpora)
		rank = extractor._rank(p)
		self.assertEqual([ ], rank)

	def test_rank_order(self):
		"""
		Test that the rank order corresponds to the probability order.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = RankExtractor(general)
		p = probability.p(corpora)
		rank = extractor._rank(p)
		for i, term in enumerate(rank[:-1]):
			self.assertLessEqual(p[term], p[rank[i + 1]])

	def test_rank_max(self):
		"""
		Test that the last term in the ranking is the term with the highest probability.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = RankExtractor(general)
		p = probability.p(corpora)
		rank = extractor._rank(p)
		self.assertEqual(max(p, key=p.get), rank[-1])

	def test_rank_max(self):
		"""
		Test that the first term in the ranking is the term with the lowest probability.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = RankExtractor(general)
		p = probability.p(corpora)
		rank = extractor._rank(p)
		self.assertEqual(min(p, key=p.get), rank[0])

	def test_rank_all(self):
		"""
		Test that the ranking function returns all terms.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = RankExtractor(general)
		p = probability.p(corpora)
		rank = extractor._rank(p)
		self.assertEqual(len(p), len(rank))
