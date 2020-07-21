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
from eventdt.apd import ELDParticipantDetector, ParticipantDetector
from eventdt.apd.extractors.local import EntityExtractor
from eventdt.apd.scorers.local import LogTFScorer, TFScorer
from eventdt.apd.filters import Filter
from eventdt.apd.filters.local import RankFilter, ThresholdFilter

class TestAPD(unittest.TestCase):
	"""
	Test the functionality of the APD tool.
	"""

	def test_rank_filter_subset(self):
		"""
		Test that when using the rank filter, a subset of all participants are returned.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
		all_participants = apd.detect(file, ParticipantDetector, EntityExtractor, TFScorer, Filter)
		top_participants = apd.detect(file, ParticipantDetector, EntityExtractor, TFScorer, RankFilter, k=10)
		self.assertTrue(all( participant in all_participants for participant in top_participants ))

	def test_rank_filter_subset_k(self):
		"""
		Test that when using the rank filter with different _k_ values, a subset is returned.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
		lenient = apd.detect(file, ParticipantDetector, EntityExtractor, TFScorer, RankFilter, k=20)
		strict = apd.detect(file, ParticipantDetector, EntityExtractor, TFScorer, RankFilter, k=10)
		self.assertEqual(20, len(lenient))
		self.assertEqual(10, len(strict))
		self.assertTrue(all( participant in lenient for participant in strict ))

	def test_rank_filter_missing_k(self):
		"""
		Test that when using the rank filter without a _k_, a ValueError is raised.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
		self.assertRaises(ValueError, apd.detect, file, ParticipantDetector, EntityExtractor, TFScorer, RankFilter)

	def test_rank_filter_length(self):
		"""
		Test that when using the rank filter, the correct number of participants are retained.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
		participants = apd.detect(file, ParticipantDetector, EntityExtractor, TFScorer, RankFilter, k=10)
		self.assertEqual(10, len(participants))

	def test_threshold_filter_subset(self):
		"""
		Test that when using the threshold filter, a subset of all participants are returned.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
		all_participants = apd.detect(file, ParticipantDetector, EntityExtractor, TFScorer, Filter)
		top_participants = apd.detect(file, ParticipantDetector, EntityExtractor, TFScorer, ThresholdFilter, threshold=1)
		self.assertTrue(all( participant in all_participants for participant in top_participants ))

	def test_rank_filter_float_threshold(self):
		"""
		Test that when using the threshold filter, the threshold is used as a float.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
		lenient = apd.detect(file, ParticipantDetector, EntityExtractor, LogTFScorer, ThresholdFilter, threshold=0.2)
		strict = apd.detect(file, ParticipantDetector, EntityExtractor, LogTFScorer, ThresholdFilter, threshold=0.8)
		self.assertTrue(all( participant in lenient for participant in strict ))
		self.assertLess(len(strict), len(lenient))

	def test_threshold_filter_missing_threshold(self):
		"""
		Test that when using the threshold filter without a threshold, a ValueError is raised.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
		self.assertRaises(ValueError, apd.detect, file, ParticipantDetector, EntityExtractor, TFScorer, ThresholdFilter)

	def test_eld_participant_detector_missing_tfidf(self):
		"""
		Test that when using the ELDParticipantDetector without a TF-IDF scheme, a ValueError is raised.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
		self.assertRaises(ValueError, apd.detect, file, ParticipantDetector, EntityExtractor, TFScorer, ThresholdFilter)
