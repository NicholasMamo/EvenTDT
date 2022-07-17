"""
Test the functionality of the DEPICT participant detector.
"""

from nltk.corpus import stopwords
import json
import os
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
           os.path.join(os.path.dirname(__file__), '..', '..'),
          os.path.join(os.path.dirname(__file__), '..', '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from depict_participant_detector import DEPICTParticipantDetector
from extractors.local import AnnotationExtractor, EntityExtractor
from scorers.local import TFScorer, LogTFScorer
from filters.local import RankFilter, ThresholdFilter
from resolvers import Resolver
from resolvers.external import WikipediaSearchResolver
from extrapolators import Extrapolator
from extrapolators.external import WikipediaAttributeExtrapolator, WikipediaExtrapolator
from postprocessors import Postprocessor
from postprocessors.external import WikipediaAttributePostprocessor

class TestDEPICTParticipantDetector(unittest.TestCase):
    """
    Test the implementation and results of the DEPICT participant detector.
    """

    def test_custom_extractor(self):
        """
        Test that when a custom extractor is given, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = DEPICTParticipantDetector(extractor=EntityExtractor(), corpus=path)
        self.assertEqual(EntityExtractor, type(apd.extractor))

    def test_custom_scorer(self):
        """
        Test that when a custom scorer is given, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = DEPICTParticipantDetector(scorer=LogTFScorer(), corpus=path)
        self.assertEqual(LogTFScorer, type(apd.scorer))

    def test_custom_filter(self):
        """
        Test that when a custom filter is given, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = DEPICTParticipantDetector(filter=ThresholdFilter(0.5), corpus=path)
        self.assertEqual(ThresholdFilter, type(apd.filter))

    def test_custom_resolver(self):
        """
        Test that when a custom resolver is given, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = DEPICTParticipantDetector(resolver=Resolver(), corpus=path)
        self.assertEqual(Resolver, type(apd.resolver))

    def test_custom_extrapolator(self):
        """
        Test that when a custom extrapolator is given, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = DEPICTParticipantDetector(extrapolator=Extrapolator(), corpus=path)
        self.assertEqual(Extrapolator, type(apd.extrapolator))

    def test_custom_postprocessor(self):
        """
        Test that when a custom postprocessor is given, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = DEPICTParticipantDetector(postprocessor=Postprocessor(), corpus=path)
        self.assertEqual(Postprocessor, type(apd.postprocessor))

    def test_default_configuration(self):
        """
        Test the default configuration of the DEPICT participant detector.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = DEPICTParticipantDetector(corpus=path)
        self.assertEqual(AnnotationExtractor, type(apd.extractor))
        self.assertEqual(TFScorer, type(apd.scorer))
        self.assertEqual(RankFilter, type(apd.filter))
        self.assertEqual(50, apd.filter.keep)
        self.assertEqual(WikipediaSearchResolver, type(apd.resolver))
        self.assertEqual(0.1, apd.resolver.threshold)
        self.assertEqual(WikipediaAttributeExtrapolator, type(apd.extrapolator))
        self.assertEqual(1, apd.extrapolator.prune)
        self.assertEqual(200, apd.extrapolator.fetch)
        self.assertEqual(WikipediaAttributePostprocessor, type(apd.postprocessor))

    def test_default_configuration_with_overload(self):
        """
        Test the default configuration of the DEPICT participant detector when overloading certain components.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = DEPICTParticipantDetector(scorer=LogTFScorer(), filter=ThresholdFilter(1), corpus=path)
        self.assertEqual(AnnotationExtractor, type(apd.extractor))
        self.assertEqual(LogTFScorer, type(apd.scorer))
        self.assertEqual(ThresholdFilter, type(apd.filter))
        self.assertEqual(WikipediaSearchResolver, type(apd.resolver))
        self.assertEqual(WikipediaAttributeExtrapolator, type(apd.extrapolator))
        self.assertEqual(WikipediaAttributePostprocessor, type(apd.postprocessor))
