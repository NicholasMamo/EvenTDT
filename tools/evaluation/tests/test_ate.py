"""
Test the functionality of the ATE evaluation tool.
"""

import json
import os
import string
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..', '..'),
          os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from evaluation import ate

class TestATE(unittest.TestCase):
    """
    Test the functionality of the ATE evaluation tool.
    """

    def test_load_terms_extracted(self):
        """
        Test that when loading terms from the output of the :mod:`~tools.terms` tool, the terms themselves are loaded.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json')
        terms = ate.load_terms(file)
        self.assertTrue(all( type(term) is str for term in terms ))
        with open(file) as f:
            original = json.loads(''.join(f.readlines()))['terms']
            original = [ term['term'] for term in original ]
        self.assertEqual(len(original), len(terms))

    def test_load_terms_extracted_order(self):
        """
        Test that when loading terms from the output of the :mod:`~tools.terms` tool, they are loaded in order of rank.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json')
        terms = ate.load_terms(file)
        with open(file) as f:
            original = json.loads(''.join(f.readlines()))['terms']
            original = [ term['term'] for term in original ]
        self.assertEqual(original, terms)

    def test_load_terms_bootstrapped(self):
        """
        Test that when loading terms from the output of the :mod:`~tools.bootstrap` tool, the terms themselves are loaded.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'bootstrapped.json')
        terms = ate.load_terms(file)
        self.assertTrue(all( type(term) is str for term in terms ))
        with open(file) as f:
            data = json.loads(''.join(f.readlines()))
            original = data['meta']['seed'] + data['bootstrapped']
        self.assertEqual(len(original), len(terms))

    def test_load_terms_bootstrapped_order(self):
        """
        Test that when loading terms from the output of the :mod:`~tools.bootstrap` tool, the seed terms are first, followed by the bootstrapped terms.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'bootstrapped.json')
        terms = ate.load_terms(file)
        with open(file) as f:
            data = json.loads(''.join(f.readlines()))
            original = data['meta']['seed'] + data['bootstrapped']
        self.assertEqual(original, terms)
