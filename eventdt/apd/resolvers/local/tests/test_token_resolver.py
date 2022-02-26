"""
Test the functionality of the token resolver.
"""

import os
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nltk.corpus import stopwords

from apd.extractors.local.entity_extractor import EntityExtractor
from apd.extractors.local.token_extractor import TokenExtractor
from apd.scorers.local.tf_scorer import TFScorer
from apd.filters.local.threshold_filter import ThresholdFilter
from apd.resolvers.local.token_resolver import TokenResolver

from nlp.document import Document
from nlp.tokenizer import Tokenizer

class TestTokenResolver(unittest.TestCase):
    """
    Test the implementation and results of the token resolver.
    """

    def test_token_resolver(self):
        """
        Test the token resolver.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')

        tokenizer = Tokenizer(min_length=1, stem=False)
        candidates = TokenExtractor().extract(path)
        scores = TFScorer().score(candidates)
        scores = ThresholdFilter(0).filter(scores)
        resolved, unresolved = TokenResolver(tokenizer, path).resolve(scores)

        self.assertTrue('chelsea' in resolved)
        self.assertTrue('callum' in resolved)
        self.assertTrue('bayern' in resolved)
        self.assertTrue('munich' in resolved)

    def test_reuse_tokenizer(self):
        """
        Test that when the tokenizer is re-used, no candidates should be unresolved.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')

        tokenizer = Tokenizer(min_length=1, stem=False, split_hashtags=False)
        candidates = TokenExtractor(tokenizer).extract(path)
        scores = TFScorer().score(candidates)
        scores = ThresholdFilter(0).filter(scores)
        resolved, unresolved = TokenResolver(tokenizer, path).resolve(scores)

        self.assertFalse(unresolved)
        self.assertEqual(len(scores), len(resolved))

    def test_different_tokenizer(self):
        """
        Test that when a different tokenizer is used than the one used in extraction, it is used.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False)

        candidates = TokenExtractor().extract(path)
        scores = TFScorer().score(candidates)
        scores = ThresholdFilter(0).filter(scores)
        resolved, unresolved = TokenResolver(tokenizer, path).resolve(scores)
        self.assertTrue('to' in resolved)

        resolved, unresolved = TokenResolver(Tokenizer(min_length=3, stem=False), path).resolve(scores)
        self.assertTrue('to' in unresolved)

    def test_unknown_token(self):
        """
        Test that when an unknown candidate is given, it is unresolved.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False)
        candidates = TokenExtractor().extract(path)
        scores = TFScorer().score(candidates)
        scores = ThresholdFilter(0).filter(scores)
        resolved, unresolved = TokenResolver(tokenizer, path).resolve({ 'unknown': 1 })
        self.assertTrue('unknown' in unresolved)

    def test_empty_corpus(self):
        """
        Test that when an empty path is given, all candidates are unresolved.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False)
        candidates = TokenExtractor().extract(path)
        scores = TFScorer().score(candidates)
        scores = ThresholdFilter(0).filter(scores)

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        resolved, unresolved = TokenResolver(tokenizer, path).resolve(scores)
        self.assertEqual(len(scores), len(unresolved))

    def test_case_folding(self):
        """
        Test that when case-folding is set, the case does not matter.
        In this test, the stem 'report' can be formed by:

            #. Reporters - appears twice
            #. reporters - appears twice
            #. reports - appears three times

        Without case-folding, 'reports' would be chosen to represent the token 'report'.
        'reports' appears three times, and 'Reporters' and 'reporters' appear twice.
        With case-folding, 'reports' still appears three times, but 'reporters' appears four times.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False)
        candidates = TokenExtractor().extract(path)
        scores = TFScorer().score(candidates)
        scores = ThresholdFilter(0).filter(scores)
        resolved, unresolved = TokenResolver(tokenizer, path, case_fold=False).resolve(scores)
        self.assertTrue('Chelsea' in resolved)

        resolved, unresolved = TokenResolver(tokenizer, path, case_fold=True).resolve(scores)
        self.assertTrue('chelsea' in resolved)

    def test_case_folding_all_lower(self):
        """
        Test that when case-folding is set, all returned tokens are in lower case.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False)
        candidates = TokenExtractor().extract(path)
        scores = TFScorer().score(candidates)
        scores = ThresholdFilter(0).filter(scores)
        resolved, unresolved = TokenResolver(tokenizer, path, case_fold=True).resolve(scores)
        self.assertTrue(all( token == token.lower() for token in resolved ))

    def test_sorting(self):
        """
        Test that the resolver sorts the tokens in descending order of score.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=3, stem=False, case_fold=True)
        candidates = TokenExtractor(tokenizer).extract(path)
        scores = TFScorer().score(candidates)
        scores = ThresholdFilter(0).filter(scores)
        resolved, unresolved = TokenResolver(tokenizer, path).resolve(scores)

        self.assertLess(resolved.index('chelsea'), resolved.index('sarri'))
