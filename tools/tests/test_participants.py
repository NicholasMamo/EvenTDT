"""
Test the functionality of the APD tool.
"""

import copy
import json
import os
import re
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
           os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

import tools
from tools import participants as apd
from eventdt.apd import ELDParticipantDetector, ParticipantDetector
from eventdt.apd.extractors import *
from eventdt.apd.scorers import *
from eventdt.apd.filters import *
from eventdt.apd.resolvers import *
from eventdt.objects.exportable import Exportable
from logger import logger
logger.set_logging_level(logger.LogLevel.WARNING)

class TestAPD(unittest.TestCase):
    """
    Test the functionality of the APD tool.
    """

    def test_detect_rank_filter_subset(self):
        """
        Test that when using the rank filter, a subset of all participants are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, Filter, Resolver, file=file)
        _, _, resolved, _, _ = apd.detect(detector, corpus=file)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, resolved_k, _, _ = apd.detect(detector, corpus=file)
        self.assertTrue(all( participant in resolved for participant in resolved_k ))

    def test_detect_rank_filter_subset_k(self):
        """
        Test that when using the rank filter with different _k_ values, a subset is returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=20, file=file)
        _, _, lenient, _, _ = apd.detect(detector, corpus=file)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, strict, _, _ = apd.detect(detector, corpus=file)
        self.assertEqual(20, len(lenient))
        self.assertEqual(10, len(strict))
        self.assertTrue(all( participant in lenient for participant in strict ))

    def test_detect_rank_filter_length(self):
        """
        Test that when using the rank filter, the correct number of participants are retained.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, resolved, _, _ = apd.detect(detector, corpus=file)
        self.assertEqual(10, len(resolved))

    def test_detect_threshold_filter_subset(self):
        """
        Test that when using the threshold filter, a subset of all participants are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, Filter, Resolver, file=file)
        _, _, resolved, _, _ = apd.detect(detector, corpus=file)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, ThresholdFilter, Resolver, filter_threshold=0.5)
        _, _, resolved_k, _, _ = apd.detect(detector, corpus=file)
        self.assertTrue(all( participant in resolved for participant in resolved_k ))

    def test_detect_rank_filter_float_threshold(self):
        """
        Test that when using the threshold filter, the threshold is used as a float.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, LogTFScorer, ThresholdFilter, Resolver, filter_threshold=0.2, file=file)
        _, _, lenient, _, _ = apd.detect(detector, corpus=file)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, LogTFScorer, ThresholdFilter, Resolver, filter_threshold=0.8, file=file)
        _, _, strict, _, _ = apd.detect(detector, corpus=file)
        self.assertTrue(all( participant in lenient for participant in strict ))
        self.assertLess(len(strict), len(lenient))

    def test_detect_threshold_filter_behaviour(self):
        """
        Test that when creating a threshold filter, the actual threshold is used to filter tokens.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.detect(ParticipantDetector, EntityExtractor, TFScorer, ThresholdFilter, Resolver, file=file, filter_threshold=0.2)
        _, filtered, _, _, _ = apd.detect(detector, corpus=file)
        self.assertTrue(all( participant['score'] >= 0.2 for participant in filtered ))

    def test_detect_threshold_filter_all(self):
        """
        Test that when using the minimum threshold filter, all participants are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, Filter, Resolver, file=file)
        _, _, resolved, _, _ = apd.detect(detector, corpus=file)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, ThresholdFilter, Resolver, filter_threshold=0)
        _, _, resolved_k, _, _ = apd.detect(detector, corpus=file)
        self.assertEqual(resolved, resolved_k)

    def test_detect_scored_ranked(self):
        """
        Test that all scored participants are returned ranked.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        scored, _, _, _, _ = apd.detect(detector, corpus=file)
        self.assertTrue(all( 'rank' in participant for participant in scored ))
        self.assertTrue(all( scored[i]['rank'] == scored[i + 1]['rank'] - 1 for i in range(len(scored) - 1) ))

    def test_detect_filtered_ranked(self):
        """
        Test that all filtered participants are returned ranked.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, filtered, _, _, _ = apd.detect(detector, corpus=file)
        self.assertTrue(all( 'rank' in participant for participant in filtered ))
        self.assertTrue(all( filtered[i]['rank'] == filtered[i + 1]['rank'] - 1 for i in range(len(filtered) - 1) ))

    def test_detect_resolved_ranked(self):
        """
        Test that all resolved participants are returned ranked.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, resolved, _, _ = apd.detect(detector, corpus=file)
        self.assertTrue(all( 'rank' in participant for participant in resolved ))
        self.assertTrue(all( resolved[i]['rank'] == resolved[i + 1]['rank'] - 1 for i in range(len(resolved) - 1) ))

    def test_detect_extrapolated_ranked(self):
        """
        Test that all extrapolated participants are returned ranked.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, _, extrapolated, _ = apd.detect(detector, corpus=file)
        self.assertTrue(all( 'rank' in participant for participant in extrapolated ))
        self.assertTrue(all( extrapolated[i]['rank'] == extrapolated[i + 1]['rank'] - 1 for i in range(len(extrapolated) - 1) ))

    def test_detect_postprocessed_ranked(self):
        """
        Test that all postprocessed participants are returned ranked.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, _, _, postprocessed = apd.detect(detector, corpus=file)
        self.assertTrue(all( 'rank' in participant for participant in postprocessed ))
        self.assertTrue(all( postprocessed[i]['rank'] == postprocessed[i + 1]['rank'] - 1 for i in range(len(postprocessed) - 1) ))

    def test_detect_token_behaviour(self):
        """
        Test that when creating a detector with a TokenExtractor and a TokenResolver, all candidates are resolved.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, TokenExtractor, TFScorer, Filter, TokenResolver, file=file)
        _, filtered, resolved, _, _ = apd.detect(detector, corpus=file)
        filtered_tokens = [ participant['participant'] for participant in filtered ]
        resolved_tokens = [ participant['participant'] for participant in resolved ]
        self.assertEqual(len(filtered_tokens), len(resolved_tokens))
        self.assertEqual(filtered_tokens, resolved_tokens)

    def test_create_detector_eld_participant_detector_missing_tfidf(self):
        """
        Test that when using the ELDParticipantDetector without a TF-IDF scheme, a ValueError is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        self.assertRaises(ValueError, apd.create_detector, ParticipantDetector, EntityExtractor, TFScorer, ThresholdFilter, Resolver, file=file)

    def test_create_extractor_none(self):
        """
        Test that when no extractor is provided, the default extractor is returned.
        """

        extractor = apd.create_extractor(None)
        self.assertEqual(None, extractor)

    def test_create_extractor_entity_extractor(self):
        """
        Test that when the EntityExtractor is provided, the default EntityExtractor is returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        extractor = apd.create_extractor(EntityExtractor)
        self.assertEqual(EntityExtractor, type(extractor))
        self.assertTrue(extractor.binary)

    def test_create_extractor_token_extractor(self):
        """
        Test that when the TokenExtractor is provided, the module-wide tokenizer is used.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        extractor = apd.create_extractor(TokenExtractor)
        self.assertEqual(TokenExtractor, type(extractor))
        self.assertEqual(apd.tokenizer, extractor.tokenizer)

    def test_create_filter_threshold_filter(self):
        """
        Test that when creating a threshold filter, the actual threshold is used.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        filter = apd.create_filter(ThresholdFilter, filter_threshold=0.5)
        self.assertEqual(ThresholdFilter, type(filter))
        self.assertEqual(0.5, filter.threshold)

    def test_create_filter_threshold_filter_missing_threshold(self):
        """
        Test that when using the threshold filter without a threshold, a ValueError is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        self.assertRaises(ValueError, apd.create_detector, ParticipantDetector, EntityExtractor, TFScorer, ThresholdFilter, Resolver, file=file)

    def test_create_filter_threshold_filter_zero(self):
        """
        Test that when creating a threshold filter with a threshold of zero, it is accepted.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        filter = apd.create_filter(ThresholdFilter, filter_threshold=0)
        self.assertEqual(ThresholdFilter, type(filter))
        self.assertEqual(0, filter.threshold)

    def test_create_filter_threshold_filter_ignores_other_thresholds(self):
        """
        Test that when creating a threshold filter, it only considers the `filter_threshold` parameter.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        filter = apd.create_filter(ThresholdFilter, filter_threshold=0.2, resolver_threshold=0.5, extrapolator_threshold=0.8)
        self.assertEqual(ThresholdFilter, type(filter))
        self.assertEqual(0.2, filter.threshold)

    def test_create_filter_rank_filter_missing_k(self):
        """
        Test that when using the rank filter without a _k_, a ValueError is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        self.assertRaises(ValueError, apd.create_detector, ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, file=file)

    def test_create_resolver_none(self):
        """
        Test that when no resolver is provided, the default resolver is returned.
        """

        resolver = apd.create_resolver(None)
        self.assertEqual(None, resolver)

    def test_create_resolver_token_resolver_none(self):
        """
        Test that when no resolver is provided, the default resolver is returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        resolver = apd.create_resolver(TokenResolver, file=file)
        self.assertEqual(TokenResolver, type(resolver))

    def test_create_resolver_token_resolver(self):
        """
        Test creating the `TokenResolver`.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        resolver = apd.create_resolver(TokenResolver, file=file)
        self.assertEqual(TokenResolver, type(resolver))

    def test_create_resolver_token_resolver_tokenizer(self):
        """
        Test that the module-wide tokenizer is used.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        resolver = apd.create_resolver(TokenResolver, file=file)
        self.assertEqual(apd.tokenizer, resolver.tokenizer)

    def test_create_resolver_wikipedia_name_resolver(self):
        """
        Test creating the `WikipediaNameResolver`.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        resolver = apd.create_resolver(WikipediaNameResolver, file=file, scheme=scheme, threshold=0)
        self.assertEqual(WikipediaNameResolver, type(resolver))

    def test_create_resolver_wikipedia_name_resolver_threshold(self):
        """
        Test that when creating a `WikipediaNameResolver`, it sets the threshold correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        resolver = apd.create_resolver(WikipediaNameResolver, file=file, scheme=scheme, resolver_threshold=0.5)
        self.assertEqual(0.5, resolver.threshold)

    def test_create_resolver_wikipedia_name_resolver_scheme(self):
        """
        Test that when creating a `WikipediaNameResolver`, it loads the scheme correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        resolver = apd.create_resolver(WikipediaNameResolver, file=file, scheme=scheme, resolver_threshold=0.5)
        _scheme = tools.load(scheme)['tfidf']
        self.assertEqual(Exportable.encode(_scheme), Exportable.encode(resolver.scheme))

    def test_create_resolver_wikipedia_name_resolver_ignores_other_thresholds(self):
        """
        Test that when creating a `WikipediaNameResolver`, it only considers the `resolver_threshold` parameter.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        resolver = apd.create_resolver(WikipediaNameResolver, file=file, scheme=scheme, filter_threshold=0.2, resolver_threshold=0.5, extrapolator_threshold=0.8)
        self.assertEqual(WikipediaNameResolver, type(resolver))
        self.assertEqual(0.5, resolver.threshold)

    def test_create_resolver_wikipedia_name_resolver_ignores_other_thresholds(self):
        """
        Test that when creating a `WikipediaNameResolver`, it only considers the `resolver_threshold` parameter.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        resolver = apd.create_resolver(WikipediaNameResolver, file=file, scheme=scheme, filter_threshold=0.2, resolver_threshold=0.5, extrapolator_threshold=0.8)
        self.assertEqual(WikipediaNameResolver, type(resolver))
        self.assertEqual(0.5, resolver.threshold)

    def test_create_resolver_wikipedia_name_resolver_without_scheme(self):
        """
        Test that creating the `WikipediaNameResolver` without a scheme raises a `ValueError`.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        self.assertRaises(ValueError, apd.create_resolver, WikipediaNameResolver, file=file, threshold=0)

    def test_create_resolver_wikipedia_name_resolver_without_threshold(self):
        """
        Test that creating the `WikipediaNameResolver` without a threshold raises a `ValueError`.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        self.assertRaises(ValueError, apd.create_resolver, WikipediaNameResolver, file=file, scheme=scheme)

    def test_create_resolver_wikipedia_name_resolver_tokenizer(self):
        """
        Test that the module-wide tokenizer is used when creating the WikipediaNameResolver.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        resolver = apd.create_resolver(WikipediaNameResolver, file=file, scheme=scheme, threshold=0)
        self.assertEqual(WikipediaNameResolver, type(resolver))
        self.assertEqual(apd.tokenizer, resolver.tokenizer)

    def test_create_resolver_wikipedia_search_resolver(self):
        """
        Test creating the `WikipediaSearchResolver`.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        resolver = apd.create_resolver(WikipediaSearchResolver, file=file, scheme=scheme, threshold=0)
        self.assertEqual(WikipediaSearchResolver, type(resolver))

    def test_create_resolver_wikipedia_search_resolver_threshold(self):
        """
        Test that when creating a `WikipediaSearchResolver`, it sets the threshold correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        resolver = apd.create_resolver(WikipediaSearchResolver, file=file, scheme=scheme, resolver_threshold=0.5)
        self.assertEqual(0.5, resolver.threshold)

    def test_create_resolver_wikipedia_search_resolver_scheme(self):
        """
        Test that when creating a `WikipediaSearchResolver`, it loads the scheme correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        resolver = apd.create_resolver(WikipediaSearchResolver, file=file, scheme=scheme, resolver_threshold=0.5)
        _scheme = tools.load(scheme)['tfidf']
        self.assertEqual(Exportable.encode(_scheme), Exportable.encode(resolver.scheme))

    def test_create_resolver_wikipedia_search_resolver_ignores_other_thresholds(self):
        """
        Test that when creating a `WikipediaSearchResolver`, it only considers the `resolver_threshold` parameter.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        resolver = apd.create_resolver(WikipediaSearchResolver, file=file, scheme=scheme, filter_threshold=0.2, resolver_threshold=0.5, extrapolator_threshold=0.8)
        self.assertEqual(WikipediaSearchResolver, type(resolver))
        self.assertEqual(0.5, resolver.threshold)

    def test_create_resolver_wikipedia_search_resolver_without_scheme(self):
        """
        Test that creating the `WikipediaSearchResolver` without a scheme raises a `ValueError`.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        self.assertRaises(ValueError, apd.create_resolver, WikipediaSearchResolver, file=file, threshold=0)

    def test_create_resolver_wikipedia_search_resolver_without_threshold(self):
        """
        Test that creating the `WikipediaSearchResolver` without a threshold raises a `ValueError`.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        self.assertRaises(ValueError, apd.create_resolver, WikipediaSearchResolver, file=file, scheme=scheme)

    def test_create_resolver_wikipedia_search_resolver_tokenizer(self):
        """
        Test that the module-wide tokenizer is used when creating the `WikipediaSearchResolver`.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        scheme = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        resolver = apd.create_resolver(WikipediaSearchResolver, file=file, scheme=scheme, threshold=0)
        self.assertEqual(apd.tokenizer, resolver.tokenizer)

    def test_rank_copy(self):
        """
        Test that when ranking participants, the original term dictionary is not changed.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, _, resolved, _, _ = detector.detect(corpus=file)
        original = copy.deepcopy(resolved)
        ranked = apd.rank(resolved)
        self.assertEqual(original, resolved)

    def test_rank_all_participants(self):
        """
        Test that when ranking participants, all participants are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, _, resolved, _, _ = detector.detect(corpus=file)
        ranked = apd.rank(resolved)
        self.assertEqual(len(resolved), len(ranked))
        self.assertEqual({ participant['participant']: participant['participant'] for participant in ranked }, resolved)

    def test_rank_no_duplicates(self):
        """
        Test that when ranking participants, there are no duplicates.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, _, resolved, _, _ = detector.detect(corpus=file)
        ranked = apd.rank(resolved)
        ranked = [ participant['participant'] for participant in ranked ]
        self.assertEqual(len(ranked), len(set(ranked)))

    def test_rank_start_from_one(self):
        """
        Test that when ranking participants, the ranks start from 1.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, _, resolved, _, _ = detector.detect(corpus=file)
        ranked = apd.rank(resolved)
        ranks = [ participant['rank'] for participant in ranked ]
        self.assertEqual(1, min(ranks))

    def test_rank_ascending_rank(self):
        """
        Test that when ranking participants, the ranks are in ascending order.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, _, resolved, _, _ = detector.detect(corpus=file)
        ranked = apd.rank(resolved)
        self.assertTrue(all( ranked[i]['rank'] == ranked[i + 1]['rank'] - 1 for i in range(len(ranked) - 1) ))

    def test_rank_scored_descending(self):
        """
        Test that when ranking scored participants, the rank is calculated by sorting them in descending order of score.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, scored, _, _, _, _ = detector.detect(corpus=file)
        ranked = apd.rank(scored)
        self.assertTrue(all( ranked[i]['score'] >= ranked[i + 1]['score'] - 1 for i in range(len(ranked) - 1) ))
        self.assertTrue(all( ranked[i]['rank'] >= ranked[i + 1]['rank'] - 1 for i in range(len(ranked) - 1) ))

    def test_rank_filtered_descending(self):
        """
        Test that when ranking filtered participants, the rank is calculated by sorting them in descending order of score.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, filtered, _, _, _ = detector.detect(corpus=file)
        ranked = apd.rank(filtered)
        self.assertTrue(all( ranked[i]['score'] >= ranked[i + 1]['score'] - 1 for i in range(len(ranked) - 1) ))
        self.assertTrue(all( ranked[i]['rank'] >= ranked[i + 1]['rank'] - 1 for i in range(len(ranked) - 1) ))

    def test_rank_resolved_order_unchanged(self):
        """
        Test that the order of resolved participants does not change when ranking.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, _, resolved, _, _ = detector.detect(corpus=file)
        ranked = apd.rank(resolved)
        self.assertTrue(all( _ranked['participant'] == _resolved for _ranked, _resolved in zip(ranked, resolved) ))

    def test_rank_resolved_order_unchanged(self):
        """
        Test that when ranking resolved participants, the value associated with each key is kept.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, _, resolved, _, _ = detector.detect(corpus=file)
        ranked = apd.rank(resolved)
        self.assertTrue(all( _ranked['participant'] == _resolved for _ranked, _resolved in zip(ranked, resolved) ))
        self.assertTrue(all( _ranked['details'] == _resolved for _ranked, _resolved in zip(ranked, resolved) ))

    def test_rank_extrapolated_order_unchanged(self):
        """
        Test that the order of extrapolated participants does not change when ranking.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, _, _, extrapolated, _ = detector.detect(corpus=file)
        ranked = apd.rank(extrapolated)
        self.assertTrue(all( _ranked['participant'] == _extrapolated for _ranked, _extrapolated in zip(ranked, extrapolated) ))

    def test_rank_postprocessed_order_unchanged(self):
        """
        Test that the order of postprocessed participants does not change when ranking.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, Resolver, keep=10, file=file)
        _, _, _, _, _, postprocessed = detector.detect(corpus=file)
        ranked = apd.rank(postprocessed)
        self.assertTrue(all( _ranked['participant'] == _postprocessed for _ranked, _postprocessed in zip(ranked, postprocessed) ))
