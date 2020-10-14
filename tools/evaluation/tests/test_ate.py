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

    def test_load_terms_default_keep(self):
        """
        Test that when loading terms without specifying the number of terms to keep, all of the terms are kept.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json')
        terms = ate.load_terms(file)
        with open(file) as f:
            original = json.loads(''.join(f.readlines()))['terms']
            self.assertEqual(len(original), len(terms))

    def test_load_terms_keep_inclusive(self):
        """
        Test that when loading terms and specifying the number of terms to keep, the number is inclusive.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json')
        terms = ate.load_terms(file, keep=10)
        self.assertEqual(10, len(terms))

    def test_load_terms_keep_order(self):
        """
        Test that when loading terms and specifying the number of terms to keep, the order of the terms is the same as in the original list.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json')
        terms = ate.load_terms(file, keep=10)
        with open(file) as f:
            original = json.loads(''.join(f.readlines()))['terms']
            original = [ term['term'] for term in original ]
            self.assertEqual(original[:10], terms)

    def test_load_terms_keep_all(self):
        """
        Test loading all terms from the file.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json')
        with open(file) as f:
            original = json.loads(''.join(f.readlines()))['terms']
            original = [ term['term'] for term in original ]
            all = len(original)

        terms = ate.load_terms(file, keep=all)
        self.assertEqual(len(original), len(terms))

    def test_load_terms_keep_extra(self):
        """
        Test that when trying to load extra terms, all terms are loaded.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json')
        with open(file) as f:
            original = json.loads(''.join(f.readlines()))['terms']
            original = [ term['term'] for term in original ]
            all = len(original)

        terms = ate.load_terms(file, keep=(all * 2))
        self.assertEqual(original, terms)

    def test_load_terms_keep_top(self):
        """
        Test that when loading a small number of terms, the ones towards the top of the ranking are retained.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json')

        terms = ate.load_terms(file, keep=10)
        with open(file) as f:
            original = json.loads(''.join(f.readlines()))['terms']
            original = { term['term']: term['rank'] for term in original}
            for i, term in enumerate(terms):
                self.assertEqual(i + 1, original[term])

    def test_load_terms_keep_bootstrap(self):
        """
        Test that when loading terms from a bootstrap file and specifying the number of terms to keep, the correct number of terms is loaded.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'bootstrapped.json')
        terms = ate.load_terms(file, keep=50)
        self.assertEqual(50, len(terms))

    def test_load_terms_keep_bootstrap_seed(self):
        """
        Test that when loading terms from a bootstrap file, the first terms are from the seed set.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'bootstrapped.json')
        with open(file) as f:
            data = json.loads(''.join(f.readlines()))
            seed, bootstrapped = data['meta']['seed'], data['bootstrapped']

        terms = ate.load_terms(file, keep=20)
        self.assertTrue(all( term in seed for term in terms))
        self.assertEqual(seed[:20], terms)

    def test_load_terms_keep_bootstrap_bootstrapped(self):
        """
        Test that when loading terms from a bootstrap file, when the function runs out of seed terms it loads bootstrapped terms.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'bootstrapped.json')
        with open(file) as f:
            data = json.loads(''.join(f.readlines()))
            seed, bootstrapped = data['meta']['seed'], data['bootstrapped']

        terms = ate.load_terms(file, keep=(len(seed)) + 10)
        self.assertEqual(terms[-10:], bootstrapped[:10])

    def test_load_gold_all_words(self):
        """
        Test that when loading the gold standard words, all words are returned.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files)

        """
        Assert that the correct number of gold words are loaded.
        """
        self.assertEqual(11, len(gold))

        """
        Load each gold set separately and ensure it has been loaded.
        """
        for file in files:
            with open(file, 'r') as f:
                for word in f:
                    self.assertTrue(word.strip() in gold.keys())
                    self.assertTrue(word.strip() in gold.values())

    def test_load_gold_multi_all_words(self):
        """
        Test that when loading the gold standard words from multiple files, all words are returned.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt'),
                  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold_other.txt') ]
        gold = ate.load_gold(files)

        """
        Assert that the correct number of gold words are loaded.
        """
        self.assertEqual(14, len(gold))

        """
        Load each gold set separately and ensure it has been loaded.
        """
        for file in files:
            with open(file, 'r') as f:
                for word in f:
                    self.assertTrue(word.strip() in gold.keys())
                    self.assertTrue(word.strip() in gold.values())

    def test_load_gold_dict(self):
        """
        Test that when loading the gold words, they are returned as a dictionary.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files)

        """
        Assert that the gold list is returned as a dictionary.
        """
        self.assertEqual(dict, type(gold))

    def test_load_gold_no_newlines(self):
        """
        Test that when loading the gold words, the newline symbol is removed.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files)

        """
        Assert that the gold list is returned as a list.
        """
        self.assertTrue(all( '\n' not in word for word in gold.keys() ))
        self.assertTrue(all( '\n' not in word for word in gold.values() ))

    def test_load_gold_default_same(self):
        """
        Test that when loading the gold words, by default the loaded and processed terms are the same.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files)

        """
        Assert that the gold list is returned as a list.
        """
        self.assertTrue(all( key == value for key, value in gold.items() ))

    def test_load_gold_multi_term_default(self):
        """
        Test that multi-word terms are retained as found by default.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files)

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

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'empty.txt') ]
        self.assertEqual({ }, ate.load_gold(files))

    def test_load_gold_none(self):
        """
        Test that when providing no gold standards, the function returns an empty gold standard.
        """

        self.assertEqual({ }, ate.load_gold([ ]))

    def test_load_gold_inverted_index(self):
        """
        Test that the gold standard is an inverted index.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files, stem=True)

        """
        Load each gold item separately and ensure its processed form is the key.
        """
        tokenizer = Tokenizer(remove_punctuation=False, stem=True, min_length=1)
        for file in files:
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

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files, stem=True)
        self.assertTrue('offsid' in gold)
        self.assertFalse('offside' in gold)

    def test_load_gold_stem_origin_not_stemmed(self):
        """
        Test that when stemming the gold standard terms, the original term is not stemmed.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files, stem=True, split=True)
        self.assertFalse('offside' in gold)
        self.assertTrue('offsid' in gold)
        self.assertEqual('offside', gold['offsid'])

    def test_load_gold_stem_multi_word(self):
        """
        Test that when loading and stemming the gold standard, multi-word terms are also stemmed.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files, stem=True)
        self.assertTrue('centr circl' in gold)
        self.assertEqual('centre circle', gold['centr circl'])

    def test_load_gold_split_unigrams(self):
        """
        Test that when loading the gold standard and splitting terms, unigrams are loaded normally.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files, stem=False, split=True)
        self.assertTrue('gol' in gold)
        self.assertTrue('keeper' in gold)

    def test_load_gold_split_multigrams(self):
        """
        Test that when loading the gold standard and splitting terms, multigrams are split.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files, stem=False, split=True)

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

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files, stem=False, split=True)

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

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files, stem=False, split=True)

        self.assertTrue('free-kick' in gold)
        self.assertFalse('free' in gold)
        self.assertFalse('kick' in gold)

    def test_load_gold_split_stem_unigrams(self):
        """
        Test that when loading the gold standard with splitting and stemming, all unigrams are stemmed.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files, stem=True, split=True)
        self.assertFalse('offside' in gold)
        self.assertTrue('offsid' in gold)

    def test_load_gold_split_stem_multigrams(self):
        """
        Test that when loading the gold standard with splitting and stemming, the components of the multi-grams are stemmed.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files, stem=True, split=True)

        self.assertTrue('centr' in gold)
        self.assertFalse('centre' in gold)
        self.assertTrue('circl' in gold)
        self.assertFalse('circle' in gold)

        self.assertTrue('yellow' in gold)
        self.assertTrue('card' in gold)

    def test_load_gold_unigrams(self):
        """
        Test that when loading only unigrams from the gold standard, none of the terms have any spaces in them.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files, unigrams=True)

        self.assertEqual(8, len(gold))
        self.assertTrue(all( ' ' not in term for term in gold.values() ))

    def test_load_gold_stemmed_unigrams(self):
        """
        Test that when stemming unigrams from the gold standard, they are all stemmed.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files, stem=True, unigrams=True)

        self.assertTrue('offsid' in gold)
        self.assertFalse('offside' in gold)

        tokenizer = Tokenizer(remove_punctuation=False, stem=True, min_length=1)
        for processed, actual in gold.items():
            self.assertEqual(tokenizer.tokenize(actual)[0], processed)

    def test_load_gold_unigrams_punctuation(self):
        """
        Test that when loading only unigrams from the gold standard, one-word terms with punctuation are accepted.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'gold.txt') ]
        gold = ate.load_gold(files, unigrams=True)

        self.assertTrue('free-kick' in gold)
