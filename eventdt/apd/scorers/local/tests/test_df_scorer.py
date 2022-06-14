"""
Test the functionality of the DF scorer.
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

from apd.extractors.local.token_extractor import TokenExtractor
from apd.scorers.local.df_scorer import DFScorer

from nlp.document import Document
from nlp.tokenizer import Tokenizer

class TestDFScorer(unittest.TestCase):
    """
    Test the implementation and results of the DF scorer.
    """

    def test_init_normalize_scores_default(self):
        """
        Test that by default, the DF scorer does not normalize scores.
        """

        scorer = DFScorer()
        self.assertFalse(scorer.normalize_scores)

        scorer = DFScorer(normalize_scores=True)
        self.assertTrue(scorer.normalize_scores)

    def test_df_scorer(self):
        """
        Test the basic functionality of the DF scorer.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = DFScorer()
        candidates = extractor.extract(path)
        scores = scorer.score(candidates, normalize_scores=False)
        candidates = scorer._fold(candidates)
        chelsea = sum([ True if 'chelsea' in candidate_set else False for candidate_set in candidates ])
        self.assertGreater(chelsea, 0)
        self.assertEqual(chelsea, scores.get('chelsea', 0))

    def test_score_candidates_unchanged(self):
        """
        Test that the original list of candidates do not change after undergoing case-folding.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = DFScorer()
        candidates = extractor.extract(path)
        original = copy.deepcopy(candidates)
        scorer.score(candidates)
        self.assertEqual(original, candidates)

    def test_score_candidates_folded(self):
        """
        Test that the candidates are case-folded when scoring.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = DFScorer()
        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        self.assertTrue(all( candidate.lower() == candidate for candidate in scores ))

    def test_score_candidates_all_retained(self):
        """
        Test that when scoring candidates, all of them are retained, if folded.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = DFScorer()
        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        self.assertTrue(all( candidate.lower() in scores for candidate_set in candidates for candidate in candidate_set ))

    def test_min_score(self):
        """
        Test that the minimum score is greater than 0.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = DFScorer()
        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        self.assertTrue(all( score > 0 for score in scores.values() ))

    def test_max_score(self):
        """
        Test that the maximum score is 1 when normalization is enabled.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = DFScorer(normalize_scores=True)
        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        self.assertTrue(all( score <= 1 for score in scores.values() ))

    def test_score_of_unknown_token(self):
        """
        Test that the score of an unknown token is 0.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = DFScorer()
        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        self.assertFalse(scores.get('unknown'))

    def test_normalization(self):
        """
        Test that when normalization is disabled, the returned scores are integers.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = DFScorer(normalize_scores=False)
        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        self.assertTrue(all( score >= 1 for score in scores.values() ))
        self.assertTrue(all( score % 1 == 0 for score in scores.values() ))

    def test_repeated_tokens(self):
        """
        Test that when tokens are repeated, the frequency that is returned is the document frequency.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = DFScorer(normalize_scores=False)
        candidates = extractor.extract(path)
        self.assertTrue(all( score == 1 for candidate_set in candidates for score in scorer.score([ candidate_set ]).values() ))
