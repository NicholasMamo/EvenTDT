"""
Test the functionality of the concepts tool.
"""

import argparse
import json
import os
import sys
import unittest

from datetime import datetime

paths = [ os.path.join(os.path.dirname(__file__), '..'),
           os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from ate.concepts import *
import concepts
from logger import logger
logger.set_logging_level(logger.LogLevel.ERROR)

class TestConcepts(unittest.TestCase):
    """
    Test the functionality of the concepts tool.
    """

    def test_is_own_correlations(self):
        """
        Test that checking whether an output was produced by this tool returns true when given its own output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "concepts.json")
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            self.assertTrue(concepts.isOwn(output))

    def test_is_own_other(self):
        """
        Test that checking whether an output was produced by this tool returns false when given another tool's output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', "bootstrapped.json")
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            self.assertFalse(concepts.isOwn(output))

    def test_create_extractor_returns_extractor(self):
        """
        Test that when creating an extractor, it actually returns an extractor.
        """

        path = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/ate/correlations.json')
        self.assertTrue(isinstance(concepts.create_extractor(GNClustering, correlations=path), TermClusteringAlgorithm))

    def test_extract_list_of_lists(self):
        """
        Test that when extracting, the function returns a list of lists.
        """

        path = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/ate/correlations.json')
        extractor = concepts.create_extractor(GNClustering, correlations=path)
        _concepts = concepts.extract(extractor, 10)
        self.assertEqual(list, type(_concepts))
        self.assertTrue(all( list == type(concept) for concept in _concepts ))

    def test_extract_1_concept(self):
        """
        Test that when extracting one concept, there is a list of list with all terms.
        """

        path = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/ate/correlations.json')
        with open(path) as f:
            terms = set(json.loads(f.readline())['correlations'])

        extractor = concepts.create_extractor(GNClustering, correlations=path)
        _concepts = concepts.extract(extractor, 1)
        self.assertEqual(1, len(_concepts))
        self.assertEqual(terms, set(_concepts[0]))

    def test_extract_n_concepts(self):
        """
        Test that when extracting concepts, the correct number of concepts are returned.
        This test ignores the fact that sometimes the term graph may be too fragmented, returning too many concepts.
        """

        path = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/ate/correlations.json')
        extractor = concepts.create_extractor(GNClustering, correlations=path)
        _concepts = concepts.extract(extractor, 15)
        self.assertEqual(15, len(_concepts))

    def test_extract_sorted(self):
        """
        Test that the extracted concepts are sorted with the largest clusters first.
        """

        path = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/ate/correlations.json')
        extractor = concepts.create_extractor(GNClustering, correlations=path)
        _concepts = concepts.extract(extractor, 15)
        self.assertTrue(all( len(_concepts[i]) >= len(_concepts[i + 1]) for i in range(len(_concepts) - 1) ))

    def test_method_lowercase(self):
        """
        Test that the method parsing converts the string to lowercase.
        """

        self.assertEqual(GNClustering, concepts.method('gnclustering'))
        self.assertEqual(GNClustering, concepts.method('GNClustering'))

    def test_method_unknown(self):
        """
        Test that if the method is unknown, the concepts tool raises an ArgumentTypeError.
        """

        self.assertRaises(argparse.ArgumentTypeError, concepts.method, 'unknown')

    def test_nn_string(self):
        """
        Test that passing a string as a natural number raises an ArgumentTypeError.
        """

        self.assertRaises(argparse.ArgumentTypeError, concepts.nn, 'abc')

    def test_nn_float(self):
        """
        Test that passing a float as a natural number raises an ArgumentTypeError.
        """

        self.assertRaises(argparse.ArgumentTypeError, concepts.nn, '1.2')

    def test_nn_0(self):
        """
        Test that passing 0 raises an ArgumentTypeError.
        """

        self.assertRaises(argparse.ArgumentTypeError, concepts.nn, '0')

    def test_nn_int(self):
        """
        Test that passing an integer as a natural number does not raise an ArgumentTypeError.
        """

        self.assertTrue(concepts.nn('1'))

    def test_nn_return_int(self):
        """
        Test that parsing a natural number returns an integer.
        """

        self.assertEqual(int, type(concepts.nn('2')))
        self.assertEqual(2, concepts.nn('2'))
