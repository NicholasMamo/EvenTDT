"""
Test the functionality of the threshold filter.
"""

import copy
import math
import os
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from apd.extractors.local.entity_extractor import EntityExtractor
from apd.scorers.local.tf_scorer import TFScorer
from apd.filters.local.threshold_filter import ThresholdFilter

from nlp.document import Document
from nlp.tokenizer import Tokenizer

class TestThresholdFilter(unittest.TestCase):
    """
    Test the implementation and results of the threshold filter.
    """

    def test_threshold_filter_does_not_change_scores(self):
        """
        Test that the threshold filter does not change the scores.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = EntityExtractor()
        scorer = TFScorer()
        filter = ThresholdFilter(5)

        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        filtered = filter.filter(scores)
        self.assertTrue(all( score == scores[candidate]
                             for candidate, score in filtered.items() ))

    def test_scores_not_changed(self):
        """
        Test that the original scores are not changed when filtering.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = EntityExtractor()
        scorer = TFScorer()
        filter = ThresholdFilter(5)

        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        original = copy.deepcopy(scores)
        filtered = filter.filter(scores)
        self.assertEqual(original, scores)

    def test_negative_threshold(self):
        """
        Test that when a negative threshold is given, all candidate participants are retained.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = EntityExtractor()
        scorer = TFScorer()
        filter = ThresholdFilter(-1)

        candidates = extractor.extract(path)
        scores = scorer.score(candidates)

        filtered = filter.filter(scores)
        self.assertEqual(scores, filtered)

    def test_zero_threshold(self):
        """
        Test that when a threshold of zero is given, all candidate participants are retained.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = EntityExtractor()
        scorer = TFScorer()
        filter = ThresholdFilter(0)

        candidates = extractor.extract(path)
        scores = scorer.score(candidates)

        filtered = filter.filter(scores)
        self.assertEqual(scores, filtered)

    def test_equal_threshold(self):
        """
        Test that when a named entity has a score that is equal to the threshold, it is retained.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = EntityExtractor()
        scorer = TFScorer()
        threshold = 5
        filter = ThresholdFilter(threshold)

        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        filtered = filter.filter(scores)
        self.assertTrue(all( candidate in filtered
                             for candidate, score in scores.items()
                             if score >= threshold ))

    def test_marginal_threshold(self):
        """
        Test that when a threshold exceeds a candidate score, the filter excludes them.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = EntityExtractor()
        scorer = TFScorer()
        threshold = 5
        filter = ThresholdFilter(threshold)

        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        filtered = filter.filter(scores)
        self.assertTrue(all( candidate not in filtered
                             for candidate, score in scores.items()
                             if score < threshold ))

    def test_high_threshold(self):
        """
        Test that when a high threshold is given, no candidate participants are retained.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = EntityExtractor()
        scorer = TFScorer()
        filter = ThresholdFilter(1.01)

        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        filtered = filter.filter(scores)
        self.assertFalse(filtered)
