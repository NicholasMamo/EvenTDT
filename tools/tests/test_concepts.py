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

    def test_create_extractor_returns_extractor(self):
        """
        Test that when creating an extractor, it actually returns an extractor.
        """

        path = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/ate/correlations.json')
        self.assertTrue(isinstance(concepts.create_extractor(GNClustering, correlations=path), TermClusteringAlgorithm))

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
