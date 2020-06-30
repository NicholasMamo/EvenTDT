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

	def test_rank_empty_dict(self):
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
