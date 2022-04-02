"""
Test the functionality of the :class:`~apd.extractors.local.annotation_extractor.AnnotationExtractor`.
"""

import json
import os
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from apd.extractors.local.annotation_extractor import AnnotationExtractor
from nlp.document import Document
from nlp.tokenizer import Tokenizer
import twitter

class TestAnnotationExtractor(unittest.TestCase):
    """
    Test the implementation and results of the :class:`~apd.extractors.local.annotation_extractor.AnnotationExtractor`.
    """

    def test_extract_returns_list_of_lists(self):
        """
        Test the annotation extractor returns a list of lists.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'LEIMUNv2.json')

        extractor = AnnotationExtractor()
        candidates = extractor.extract(path)
        self.assertEqual(list, type(candidates))
        self.assertTrue(all( list == type(candidate_list) for candidate_list in candidates ))
        self.assertTrue(all( str == type(candidate) for candidate_list in candidates for candidate in candidate_list ))

    def test_extract_from_empty_corpus(self):
        """
        Test that the annotation extractor returns an empty list from an empty corpus.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        extractor = AnnotationExtractor()
        candidates = extractor.extract(path)
        self.assertEqual([ ], candidates)

    def test_extract_from_all_tweets(self):
        """
        Test that the annotation extractor returns as many candidate sets as the number of documents given.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'LEIMUNv2.json')
        with open(path) as f:
            expected = len(f.readlines())

        extractor = AnnotationExtractor()
        candidates = extractor.extract(path)
        self.assertEqual(expected, len(candidates))

    def test_extract_entities_in_tweets(self):
        """
        Test that all extracted entities appear in the tweets.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'LEIMUNv2.json')
        extractor = AnnotationExtractor()
        candidates = extractor.extract(path)

        with open(path) as f:
            for i, line in enumerate(f):
                tweet = json.loads(line)
                self.assertTrue(all( candidate in twitter.full_text(tweet) for candidate in candidates[i] ))

    def test_extract_all_annotations(self):
        """
        Test that the annotation extractor returns all annotations.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'LEIMUNv2.json')
        extractor = AnnotationExtractor()
        candidates = extractor.extract(path)

        with open(path) as f:
            for i, line in enumerate(f):
                tweet = json.loads(line)
                self.assertEqual(twitter.annotations(tweet), candidates[i])
