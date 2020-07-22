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
from extractors.local.twitterner_entity_extractor import TwitterNEREntityExtractor
from scorers.local import TFScorer, LogTFScorer
from filters.local import RankFilter, ThresholdFilter
from resolvers import Resolver
from resolvers.external import WikipediaSearchResolver
from extrapolators import Extrapolator
from extrapolators.external import WikipediaExtrapolator
from postprocessors import Postprocessor
from postprocessors.external import WikipediaPostprocessor

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

	def test_default_configuration(self):
		"""
		Test the default configuration of the ELD participant detector.
		"""

		apd = ELDParticipantDetector()
		self.assertEqual(TwitterNEREntityExtractor, type(apd.extractor))
		self.assertEqual(TFScorer, type(apd.scorer))
		self.assertEqual(RankFilter, type(apd.filter))
		self.assertEqual(WikipediaSearchResolver, type(apd.resolver))
		self.assertEqual(WikipediaExtrapolator, type(apd.extrapolator))
		self.assertEqual(WikipediaPostprocessor, type(apd.postprocessor))

	def test_default_configuration_with_overload(self):
		"""
		Test the default configuration of the ELD participant detector when overloading certain components.
		"""

		apd = ELDParticipantDetector(scorer=LogTFScorer(), filter=ThresholdFilter(1))
		self.assertEqual(TwitterNEREntityExtractor, type(apd.extractor))
		self.assertEqual(LogTFScorer, type(apd.scorer))
		self.assertEqual(ThresholdFilter, type(apd.filter))
		self.assertEqual(WikipediaSearchResolver, type(apd.resolver))
		self.assertEqual(WikipediaExtrapolator, type(apd.extrapolator))
		self.assertEqual(WikipediaPostprocessor, type(apd.postprocessor))
