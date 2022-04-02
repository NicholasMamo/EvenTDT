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

    def test_entity_extractor_returns_list_of_lists(self):
        """
        Test the annotation extractor returns a list of lists.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'LEIMUNv2.json')

        extractor = AnnotationExtractor()
        candidates = extractor.extract(path)
        self.assertEqual(list, type(candidates))
        self.assertTrue(all( list == type(candidate_list) for candidate_list in candidates ))
        self.assertTrue(all( str == type(candidate) for candidate_list in candidates for candidate in candidate_list ))

    def test_empty_corpus(self):
        """
        Test that the annotation extractor returns an empty list from an empty corpus.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        extractor = AnnotationExtractor()
        candidates = extractor.extract(path)
        self.assertEqual([ ], candidates)

    def test_return_length(self):
        """
        Test that the annotation extractor returns as many candidate sets as the number of documents given.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'LEIMUNv2.json')
        with open(path) as f:
            expected = len(f.readlines())

        extractor = AnnotationExtractor()
        candidates = extractor.extract(path)
        self.assertEqual(expected, len(candidates))
