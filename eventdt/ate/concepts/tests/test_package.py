"""
Test the functionality of the concepts package-level functions.
"""

import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate.concepts import DummyTermClusteringAlgorithm

class TestPackage(unittest.TestCase):
    """
    Test the functionality of the concepts package-level functions.
    """

    def test_read_correlations_all(self):
        """
        Test that the :class:`~ate.concepts.TermClusteringAlgorithm` reads all terms and correlations from the given file.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            # load the terms manually
            terms = json.loads(file.readline())['correlations']
            file.seek(0)

            # load the terms using the class
            algo = DummyTermClusteringAlgorithm(file)

            self.assertEqual(terms, algo.similarity)
