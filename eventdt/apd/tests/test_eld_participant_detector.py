"""
Test the functionality of the ELD participant detector.
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

from eld_participant_detector import ELDParticipantDetector
from extractors.local import EntityExtractor
from scorers.local import TFScorer, LogTFScorer
from filters.local import RankFilter, ThresholdFilter
from resolvers import Resolver
from resolvers.external import WikipediaSearchResolver
from extrapolators import Extrapolator
from extrapolators.external import WikipediaExtrapolator
from postprocessors import Postprocessor
from postprocessors.external import WikipediaPostprocessor

from nlp.tokenizer import Tokenizer

class TestELDParticipantDetector(unittest.TestCase):
    """
    Test the implementation and results of the ELD participant detector.
    """

    def test_init_custom_extractor(self):
        """
        Test that when a custom extractor is given, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = ELDParticipantDetector(extractor=EntityExtractor(), corpus=path)
        self.assertEqual(EntityExtractor, type(apd.extractor))

    def test_init_custom_scorer(self):
        """
        Test that when a custom scorer is given, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = ELDParticipantDetector(scorer=LogTFScorer(), corpus=path)
        self.assertEqual(LogTFScorer, type(apd.scorer))

    def test_init_custom_filter(self):
        """
        Test that when a custom filter is given, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = ELDParticipantDetector(filter=ThresholdFilter(0.5), corpus=path)
        self.assertEqual(ThresholdFilter, type(apd.filter))

    def test_init_custom_resolver(self):
        """
        Test that when a custom resolver is given, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = ELDParticipantDetector(resolver=Resolver(), corpus=path)
        self.assertEqual(Resolver, type(apd.resolver))

    def test_init_custom_extrapolator(self):
        """
        Test that when a custom extrapolator is given, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = ELDParticipantDetector(extrapolator=Extrapolator(), corpus=path)
        self.assertEqual(Extrapolator, type(apd.extrapolator))

    def test_init_custom_postprocessor(self):
        """
        Test that when a custom postprocessor is given, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = ELDParticipantDetector(postprocessor=Postprocessor(), corpus=path)
        self.assertEqual(Postprocessor, type(apd.postprocessor))

    def test_init_custom_tokenizer(self):
        """
        Test that when a custom tokenizer is given, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = ELDParticipantDetector(tokenizer=Tokenizer(stem=False), corpus=path)
        self.assertFalse(apd.resolver.tokenizer.stem)
        self.assertFalse(apd.extrapolator.tokenizer.stem)

    def test_init_default_configuration(self):
        """
        Test the default configuration of the ELD participant detector.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = ELDParticipantDetector(corpus=path)
        from extractors.local.twitterner_entity_extractor import TwitterNEREntityExtractor
        self.assertEqual(TwitterNEREntityExtractor, type(apd.extractor))
        self.assertEqual(TFScorer, type(apd.scorer))
        self.assertEqual(RankFilter, type(apd.filter))
        self.assertEqual(WikipediaSearchResolver, type(apd.resolver))
        self.assertEqual(WikipediaExtrapolator, type(apd.extrapolator))
        self.assertEqual(WikipediaPostprocessor, type(apd.postprocessor))

    def test_init_default_configuration_with_overload(self):
        """
        Test the default configuration of the ELD participant detector when overloading certain components.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  'tests', 'corpora', 'empty.json')
        apd = ELDParticipantDetector(scorer=LogTFScorer(), filter=ThresholdFilter(1), corpus=path)
        from extractors.local.twitterner_entity_extractor import TwitterNEREntityExtractor
        self.assertEqual(TwitterNEREntityExtractor, type(apd.extractor))
        self.assertEqual(LogTFScorer, type(apd.scorer))
        self.assertEqual(ThresholdFilter, type(apd.filter))
        self.assertEqual(WikipediaSearchResolver, type(apd.resolver))
        self.assertEqual(WikipediaExtrapolator, type(apd.extrapolator))
        self.assertEqual(WikipediaPostprocessor, type(apd.postprocessor))
