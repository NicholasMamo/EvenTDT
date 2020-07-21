"""
Test the functionality of the APD tool.
"""

import json
import os
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
 		  os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

from tools import participants as apd
from eventdt.apd.extractors.local import EntityExtractor
from eventdt.apd.scorers.local import TFScorer
from eventdt.apd.filters import Filter
from eventdt.apd.filters.local import RankFilter, ThresholdFilter

class TestAPD(unittest.TestCase):
	"""
	Test the functionality of the APD tool.
	"""

	def test_filter_subset(self):
		"""
		Test that when filtering, a subset of all participants are returned.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
		all_participants = apd.detect(file, EntityExtractor, TFScorer, Filter)
		top_participants = apd.detect(file, EntityExtractor, TFScorer, RankFilter, k=10)
		self.assertTrue(all( participant in all_participants for participant in top_participants ))

	def test_rank_filter_missing_k(self):
		"""
		Test that when using the rank filter without a _k_, a ValueError is raised.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
		self.assertRaises(ValueError, apd.detect, file, EntityExtractor, TFScorer, RankFilter)

	def test_rank_filter_length(self):
		"""
		Test that when using the rank filter, the correct number of participants are retained.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
		participants = apd.detect(file, EntityExtractor, TFScorer, RankFilter, k=10)
		self.assertEqual(10, len(participants))
