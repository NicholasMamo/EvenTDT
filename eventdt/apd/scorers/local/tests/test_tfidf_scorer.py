"""
Test the functionality of the TF-IDF scorer.
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
from apd.scorers.local.tfidf_scorer import TFIDFScorer

from nlp.document import Document
from nlp.tokenizer import Tokenizer

class TestTFIDFScorer(unittest.TestCase):
    """
    Test the implementation and results of the TF-IDF scorer.
    """

    def test_init_high_value(self):
        """
        Test that the IDF raises an error when the highest IDF value is higher than the number of documents.
        """

        idf = { 'a': 3, 'b': 1 }
        self.assertRaises(ValueError, TFIDFScorer, idf, 2)

    def test_init_negative_value(self):
        """
        Test that the IDF raises an error when any IDF value is negative.
        """

        idf = { 'a': 3, 'b': -1 }
        self.assertRaises(ValueError, TFIDFScorer, idf, 3)

    def test_init_negative_documents(self):
        """
        Test that the IDF raises an error when the number of documents is negative.
        """

        idf = { 'a': 3, 'b': 1 }
        self.assertRaises(ValueError, TFIDFScorer, idf, -1)

    def test_init_normalize_scores_default(self):
        """
        Test that by default, the TF scorer does not normalize scores.
        """

        idf = { 'a': 3, 'b': 1 }

        scorer = TFIDFScorer(idf, 3)
        self.assertFalse(scorer.normalize_scores)

        scorer = TFIDFScorer(idf, 3, normalize_scores=True)
        self.assertTrue(scorer.normalize_scores)

    def test_tfidf_scorer(self):
        """
        Test the basic functionality of the TF-IDF scorer.
        """

        """
        Create the test data.
        """
        tokenizer = Tokenizer(stem=False)
        posts = [
            "Erdogan with threats to attack regime forces 'everywhere' in Syria",
            "Damascus says Erdogan 'disconnected from reality' after threats",
        ]

        scorer = TFIDFScorer({ 'erdogan': 1, 'threats': 2 }, 10)
        scores = scorer.score([ tokenizer.tokenize(post) for post in posts ])
        self.assertGreater(scores.get('erdogan'), scores.get('damascus'))
        self.assertEqual(scores.get('everywhere'), scores.get('disconnected')) # they appear the same number of times
        self.assertGreater(scores.get('erdogan'), scores.get('threats')) # 'threats' and 'erdogan' appear with the same frequency, but 'threats' has a higher DF

    def test_score_candidates_unchanged(self):
        """
        Test that the original list of candidates do not change after undergoing case-folding.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = TFIDFScorer({ 'erdogan': 1, 'threats': 2 }, 10)
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
        scorer = TFIDFScorer({ 'erdogan': 1, 'threats': 2 }, 10)
        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        self.assertTrue(all( candidate.lower() == candidate for candidate in scores ))

    def test_score_candidates_all_retained(self):
        """
        Test that when scoring candidates, all of them are retained, if folded.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = TFIDFScorer({ 'erdogan': 1, 'threats': 2 }, 10)
        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        self.assertTrue(all( candidate.lower() in scores for candidate_set in candidates for candidate in candidate_set ))

    def test_min_score(self):
        """
        Test that the minimum score is greater than 0.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = TFIDFScorer({ 'chelsea': 10 }, 100)
        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        self.assertTrue(all( score > 0 for score in scores.values() ))

    def test_max_score(self):
        """
        Test that the maximum score is 1 when normalization is enabled.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = TFIDFScorer({ 'chelsea': 10 }, 100, normalize_scores=True)
        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        self.assertTrue(all( score <= 1 for score in scores.values() ))

    def test_score_of_unknown_token(self):
        """
        Test that the score of an unknown token is 0.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = TFIDFScorer({ 'chelsea': 10 }, 100)
        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        self.assertFalse(scores.get('unknown'))

    def test_normalization(self):
        """
        Test that when normalization is disabled, the returned scores are integers.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TokenExtractor()
        scorer = TFIDFScorer({ 'chelsea': 10 }, 100, normalize_scores=False)
        candidates = extractor.extract(path)
        scores = scorer.score(candidates)
        self.assertTrue(all( score >= 1 for score in scores.values() ))
        self.assertTrue(all( score % 1 == 0 for score in scores.values() ))

    def test_repeated_tokens(self):
        """
        Test that when tokens are repeated, the frequency that is returned is the document frequency.
        """

        """
        Create the test data.
        """
        tokenizer = Tokenizer(stem=False)
        posts = [
            "After Erdogan's statement, Damascus says Erdogan 'disconnected from reality' after threats",
        ]

        corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

        extractor = TokenExtractor(tokenizer=tokenizer)
        scorer = TFIDFScorer({ 'erdogan': 3, 'threats': 2 }, 10, normalize_scores=False)
        scores = scorer.score([ tokenizer.tokenize(post) for post in posts ])
        self.assertEqual(2 * math.log(10 / 3, 10), scores.get('erdogan'))
