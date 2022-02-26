"""
Test the functionality of the Wikipedia name resolver.
"""

import os
import random
import string
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nltk.corpus import stopwords

from apd.extractors.local.entity_extractor import EntityExtractor
from apd.scorers.local.tf_scorer import TFScorer
from apd.filters.local.threshold_filter import ThresholdFilter
from apd.resolvers.external.wikipedia_name_resolver import WikipediaNameResolver

from nlp.document import Document
from nlp.tokenizer import Tokenizer
from nlp.weighting.tf import TF

class TestWikipediaNameResolver(unittest.TestCase):
    """
    Test the implementation and results of the Wikipedia name resolver.
    """

    def test_wikipedia_name_resolver(self):
        """
        Test the Wikipedia name resolver.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False)
        resolver = WikipediaNameResolver(TF(), tokenizer, 0, path)
        resolved, unresolved = resolver.resolve({ 'Chelsea F.C.': 1, 'Maurizio Sarri': 0.5 })

        self.assertTrue('Chelsea F.C.' in resolved)
        self.assertTrue('Maurizio Sarri' in resolved)

    def test_all_resolved_or_unresolved(self):
        """
        Test that the resolver either resolves or does not resolve named entities.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False)
        resolver = WikipediaNameResolver(TF(), tokenizer, 0, path)
        scores = { 'Chelsea F.C.': 1, 'Maurizio Sarri': 0.5, 'Callum': 0.25, 'EvenTDT': 0.1 }
        resolved, unresolved = resolver.resolve(scores)
        self.assertTrue(all( candidate in resolved or candidate in unresolved for candidate in scores ))

    def test_random_string_unresolved(self):
        """
        Test that a random string is unresolved.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False)
        resolver = WikipediaNameResolver(TF(), tokenizer, 0, path)
        random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(32))
        scores = { random_string: 1 }
        resolved, unresolved = resolver.resolve(scores)
        self.assertTrue(random_string in unresolved)

    def test_zero_threshold(self):
        """
        Test that when the threshold is zero, it includes all ambiguous candidates.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False, stopwords=list(stopwords.words("english")))
        resolver = WikipediaNameResolver(TF(), tokenizer, 0, path)
        scores = { 'Chelsea F.C.': 1, 'Maurizio Sarri': 0.5, 'Callum': 0.25, 'Eden': 0.1 }
        resolved, unresolved = resolver.resolve(scores)
        self.assertTrue('Eden' in resolved)
        self.assertEqual('Eden Hazard', resolved['Eden'])

    def test_low_threshold(self):
        """
        Test that when the threshold is not zero, it excludes some ambiguous candidates.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False, stopwords=list(stopwords.words("english")))
        resolver = WikipediaNameResolver(TF(), tokenizer, 0.5, path)
        scores = { 'Chelsea F.C.': 1, 'Maurizio Sarri': 0.5, 'Callum': 0.25, 'Eden': 0.1 }
        resolved, unresolved = resolver.resolve(scores)
        self.assertFalse('Eden Hazard' in resolved)
        self.assertTrue('Eden' in unresolved)

    def test_resolve_empty(self):
        """
        Test that when resolving an empty set of candidates, the resolver returns empty lists.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        resolver = WikipediaNameResolver(TF(), Tokenizer(), 0, path)
        resolved, unresolved = resolver.resolve({ })
        self.assertFalse(len(resolved))
        self.assertFalse(len(unresolved))

    def test_sorting(self):
        """
        Test that the resolver sorts the named entities in descending order of score.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False, stopwords=list(stopwords.words("english")))
        resolver = WikipediaNameResolver(TF(), tokenizer, 0, path)
        scores = { 'Chelsea F.C.': 1, 'Maurizio Sarri': 0.5, 'Callum': 0.1, 'Eden Hazard': 0.25 }
        resolved, unresolved = resolver.resolve(scores)

        order = sorted(scores, key=scores.get, reverse=True)
        self.assertEqual(order, list(resolved.keys()))

    def test_sorting_ambiguous(self):
        """
        Test that the resolver sorts the named entities in descending order of score, but ambiguous candidates are at the end.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False, stopwords=list(stopwords.words("english")))
        resolver = WikipediaNameResolver(TF(), tokenizer, 0, path)
        scores = { 'Chelsea F.C.': 1, 'Maurizio Sarri': 0.5, 'Callum': 0.1, 'Eden': 0.25 }
        resolved, unresolved = resolver.resolve(scores)

        order = sorted(scores, key=scores.get, reverse=True)
        order.remove('Eden')
        self.assertEqual(order + [ 'Eden Hazard' ], list(resolved.values()))
