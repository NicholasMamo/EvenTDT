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

    def test_load_gold_all_words(self):
        """
        Test that when loading the gold standard words, all words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file)

        """
        Assert that the correct number of gold words are loaded.
        """
        self.assertEqual(10, len(gold))

        """
        Load each gold set separately and ensure it has been loaded.
        """
        with open(file, 'r') as f:
            for word in f:
                self.assertTrue(word.strip() in gold.keys())
                self.assertTrue(word.strip() in gold.values())

    def test_load_gold_dict(self):
        """
        Test that when loading the gold words, they are returned as a dictionary.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file)

        """
        Assert that the gold list is returned as a dictionary.
        """
        self.assertEqual(dict, type(gold))

    def test_load_gold_no_newlines(self):
        """
        Test that when loading the gold words, the newline symbol is removed.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file)

        """
        Assert that the gold list is returned as a list.
        """
        self.assertTrue(all( '\n' not in word for word in gold.keys() ))
        self.assertTrue(all( '\n' not in word for word in gold.values() ))

    def test_load_gold_default_same(self):
        """
        Test that when loading the gold words, by default the loaded and processed terms are the same.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file)

        """
        Assert that the gold list is returned as a list.
        """
        self.assertTrue(all( key == value for key, value in gold.items() ))

    def test_load_gold_empty(self):
        """
        Test that when the gold file is empty, the function returns an empty gold standard.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'empty.txt')
        self.assertEqual({ }, ate.load_gold(file))
