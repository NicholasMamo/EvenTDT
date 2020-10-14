"""
Test the functionality of the linguistic package functions.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from linguistic import *

class TestPackage(unittest.TestCase):
    """
    Test the functionality of the linguistic package functions.
    """

    def test_vocabulary_empty_corpus(self):
        """
        Test that the vocabulary of an empty corpus is an empty list.
        """

        path = os.path.join(os.path.dirname(__file__), 'empty.json')
        self.assertEqual([ ], vocabulary(path))

    def test_vocabulary_example(self):
        """
        Test getting the vocabulary.
        """

        path = os.path.join(os.path.dirname(__file__), 'e.json')
        self.assertEqual({ 'x', '!x', 'y', '!y' }, set(vocabulary(path)))

    def test_vocabulary_one_corpus(self):
        """
        Test getting the vocabulary from one corpus.
        """

        path = os.path.join(os.path.dirname(__file__), 'c1.json')

        """
        Manually get the vocabulary.
        """
        vocab = [ ]
        with open(path, 'r') as f:
            for line in f:
                vocab.extend(json.loads(line)['tokens'])

        """
        Get the vocabulary using the function.
        """
        self.assertEqual(set(vocab), set(vocabulary(path)))

    def test_vocabulary_corpora(self):
        """
        Test getting the vocabulary from multiple corpora.
        """

        paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
                   os.path.join(os.path.dirname(__file__), 'c2.json') ]

        """
        Manually get the vocabulary.
        """
        vocab = { }
        for path in paths:
            vocab[path] = [ ]
            with open(path, 'r') as f:
                for line in f:
                    vocab[path].extend(json.loads(line)['tokens'])

        """
        Check that all the words in each corpus are in the vocabulary.
        """
        all_tokens = vocabulary(paths)
        self.assertTrue(all(token in all_tokens for token in set(vocab[paths[0]])))
        self.assertTrue(all(token in all_tokens for token in set(vocab[paths[1]])))
        self.assertEqual(set(all_tokens), set(vocab[paths[0]]).union(set(vocab[paths[1]])))

    def test_vocabulary_set(self):
        """
        Test that the vocabulary returned is a set with no duplicates.
        """

        paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
                   os.path.join(os.path.dirname(__file__), 'c2.json') ]

        all_tokens = vocabulary(paths)
        self.assertEqual(len(set(all_tokens)), len(all_tokens))

    def test_nouns_empty_corpus(self):
        """
        Test that the nouns of an empty corpus is an empty list.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'empty.json')
        self.assertEqual([ ], nouns(path))

    def test_nouns_single_corpus(self):
        """
        Test extracting nouns from a corpus.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
        tokens = nouns(path)
        self.assertTrue('corner' in tokens)
        self.assertFalse('give' in tokens)
        self.assertFalse('lost' in tokens)

    def test_nouns_multiple_corpora(self):
        """
        Test extracting nouns from multiple corpora.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json') ]
        tokens = nouns(paths)
        self.assertTrue('corner' in tokens)
        self.assertFalse('give' in tokens)
        self.assertFalse('lost' in tokens)

    def test_nouns_set(self):
        """
        Test that the returned nouns are a set with no duplicates.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json') ]

        tokens = nouns(paths)
        self.assertEqual(len(set(tokens)), len(tokens))

    def test_nouns_no_stem(self):
        """
        Test that when no stemming is specified, the words are not stemmed.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json') ]

        tokens = nouns(paths, stem=False)
        self.assertTrue('feeling' in tokens)
        self.assertFalse('feel' in tokens)
