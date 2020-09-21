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
from nlp import Tokenizer

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
        self.assertEqual(11, len(gold))

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

    def test_load_gold_multi_term_default(self):
        """
        Test that multi-word terms are retained as found by default.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file)

        """
        Assert that the gold list is returned as a list.
        """
        self.assertTrue(all( key == value for key, value in gold.items() ))
        self.assertTrue('free-kick' in gold)
        self.assertTrue('yellow card' in gold)
        self.assertTrue('centre circle' in gold)

    def test_load_gold_empty(self):
        """
        Test that when the gold file is empty, the function returns an empty gold standard.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'empty.txt')
        self.assertEqual({ }, ate.load_gold(file))

    def test_load_gold_inverted_index(self):
        """
        Test that the gold standard is an inverted index.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file, stem=True)

        """
        Load each gold item separately and ensure its processed form is the key.
        """
        tokenizer = Tokenizer(remove_punctuation=False, stem=True, min_length=1)
        with open(file, 'r') as f:
            for word in f:
                word = word.strip()
                processed = ' '.join(tokenizer.tokenize(word))
                self.assertTrue(processed in gold)
                self.assertEqual(word, gold[processed])

    def test_load_gold_stem(self):
        """
        Test that when stemming the gold standard terms, they are all stemmed.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file, stem=True)
        self.assertTrue('offsid' in gold)
        self.assertFalse('offside' in gold)

    def test_load_gold_stem_origin_not_stemmed(self):
        """
        Test that when stemming the gold standard terms, the original term is not stemmed.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file, stem=True, split=True)
        self.assertFalse('offside' in gold)
        self.assertTrue('offsid' in gold)
        self.assertEqual('offside', gold['offsid'])

    def test_load_gold_stem_multi_word(self):
        """
        Test that when loading and stemming the gold standard, multi-word terms are also stemmed.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file, stem=True)
        self.assertTrue('centr circl' in gold)
        self.assertEqual('centre circle', gold['centr circl'])

    def test_load_gold_split_unigrams(self):
        """
        Test that when loading the gold standard and splitting terms, unigrams are loaded normally.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file, stem=False, split=True)
        self.assertTrue('gol' in gold)
        self.assertTrue('keeper' in gold)

    def test_load_gold_split_multigrams(self):
        """
        Test that when loading the gold standard and splitting terms, multigrams are split.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file, stem=False, split=True)

        self.assertTrue('yellow' in gold)
        self.assertTrue('card' in gold)
        self.assertFalse('yellow card' in gold)

        self.assertTrue('centre' in gold)
        self.assertTrue('circle' in gold)
        self.assertFalse('centre circle' in gold)

    def test_load_gold_split_multigrams_same_origin(self):
        """
        Test that when loading the gold standard and splitting terms, multigrams' values are the original words.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file, stem=False, split=True)

        self.assertTrue('yellow' in gold)
        self.assertTrue('card' in gold)
        self.assertEqual('yellow card', gold['yellow'])
        self.assertEqual('yellow card', gold['card'])

        self.assertTrue('centre' in gold)
        self.assertTrue('circle' in gold)
        self.assertEqual('centre circle', gold['centre'])
        self.assertEqual('centre circle', gold['circle'])

    def test_load_gold_split_space(self):
        """
        Test that when loading the gold standard and splitting terms, the splits are based on spaces, not punctuation.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file, stem=False, split=True)

        self.assertTrue('free-kick' in gold)
        self.assertFalse('free' in gold)
        self.assertFalse('kick' in gold)

    def test_load_gold_split_stem_unigrams(self):
        """
        Test that when loading the gold standard with splitting and stemming, all unigrams are stemmed.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file, stem=True, split=True)
        self.assertFalse('offside' in gold)
        self.assertTrue('offsid' in gold)

    def test_load_gold_split_stem_multigrams(self):
        """
        Test that when loading the gold standard with splitting and stemming, the components of the multi-grams are stemmed.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt')
        gold = ate.load_gold(file, stem=True, split=True)

        self.assertTrue('centr' in gold)
        self.assertFalse('centre' in gold)
        self.assertTrue('circl' in gold)
        self.assertFalse('circle' in gold)

        self.assertTrue('yellow' in gold)
        self.assertTrue('card' in gold)
