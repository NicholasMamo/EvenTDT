"""
Test the functionality of the ELD participant detector.
"""

import os
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
 		  os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

from eld_participant_detector import ELDParticipantDetector
from extractors.local import EntityExtractor
from scorers.local import LogTFScorer
from filters.local import ThresholdFilter
from resolvers import Resolver
from extrapolators import Extrapolator
from postprocessors import Postprocessor

class TestELDParticipantDetector(unittest.TestCase):
	"""
	Test the implementation and results of the ELD participant detector.
	"""

	def test_custom_extractor(self):
		"""
		Test that when a custom extractor is given, it is used.
		"""

		apd = ELDParticipantDetector(extractor=EntityExtractor())
		self.assertEqual(EntityExtractor, type(apd.extractor))

	def test_custom_scorer(self):
		"""
		Test that when a custom scorer is given, it is used.
		"""

		apd = ELDParticipantDetector(scorer=LogTFScorer())
		self.assertEqual(LogTFScorer, type(apd.scorer))

	def test_custom_filter(self):
		"""
		Test that when a custom filter is given, it is used.
		"""

		apd = ELDParticipantDetector(filter=ThresholdFilter(0.5))
		self.assertEqual(ThresholdFilter, type(apd.filter))

	def test_custom_resolver(self):
		"""
		Test that when a custom resolver is given, it is used.
		"""

		apd = ELDParticipantDetector(resolver=Resolver())
		self.assertEqual(Resolver, type(apd.resolver))

	def test_custom_extrapolator(self):
		"""
		Test that when a custom extrapolator is given, it is used.
		"""

		apd = ELDParticipantDetector(extrapolator=Extrapolator())
		self.assertEqual(Extrapolator, type(apd.extrapolator))

	def test_custom_postprocessor(self):
		"""
		Test that when a custom postprocessor is given, it is used.
		"""

		apd = ELDParticipantDetector(postprocessor=Postprocessor())
		self.assertEqual(Postprocessor, type(apd.postprocessor))
