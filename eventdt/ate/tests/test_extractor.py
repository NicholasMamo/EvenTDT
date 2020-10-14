"""
Test the functionality of the abstract extractor class.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from extractor import DummyExtractor

class TestExtractor(unittest.TestCase):
    """
    Test the functionality of the abstract extractor class.
    """

    def test_to_list_one_corpus(self):
        """
        Test that when converting a single corpus to a list, a list with that corpus is returned.
        """

        extractor = DummyExtractor()
        self.assertEqual([ 'a' ], extractor.to_list('a'))

    def test_to_list_multiple_corpora(self):
        """
        Test that when converting multiple corpora to a list, the same list is returned.
        """

        extractor = DummyExtractor()
        self.assertEqual([ 'a', 'b' ], extractor.to_list([ 'a', 'b' ]))
