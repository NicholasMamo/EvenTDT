"""
Test the functionality of the ATE package-level functions.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

import ate
from summarization import timeline

class TestPackage(unittest.TestCase):
    """
    Test the functionality of the ATE package-level functions.
    """

    def test_total_documents_empty_corpus(self):
        """
        Test that the number of documents in an empty corpus is 0.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'empty.json')
        documents = ate.total_documents(path)
        self.assertEqual(0, documents)

    def test_total_documents_one_corpus(self):
        """
        Test getting the number of documents from one corpus.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
        documents = ate.total_documents(path)

        """
        Count the documents by reading all lines.
        """
        with open(path, 'r') as f:
            self.assertEqual(documents, len(f.readlines()))

    def test_total_documents_multiple_corpora(self):
        """
        Test getting the number of documents from multiple corpora.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
        documents = ate.total_documents(paths)

        """
        Count the documents by reading all lines.
        """
        total = 0
        for path in paths:
            with open(path, 'r') as f:
                total += len(f.readlines())

        self.assertEqual(documents, total)

    def test_total_documents_int(self):
        """
        Test that when no focus tokens or tuples are given, an integer is returned.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
        documents = ate.total_documents(paths)
        self.assertEqual(int, type(documents))

    def test_total_documents_token(self):
        """
        Test that when computing the number of documents in which one token appears, the frequency is correct.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]

        """
        Compute the probability for all tokens in the corpora first.
        """
        token = 'yellow'
        freq = ate.total_documents(paths, focus=token)
        self.assertEqual(int, type(freq))

        """
        Count the documents in which the token appears by reading all lines.
        """
        total = 0
        for path in paths:
            with open(path, 'r') as f:
                for line in f:
                    document = json.loads(line)
                    if token in document['tokens']:
                        total += 1

        self.assertEqual(freq, total)

    def test_total_documents_tuple(self):
        """
        Test that when computing the number of documents in which one tuple appears, the frequency is correct.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]

        """
        Compute the probability for all tokens in the corpora first.
        """
        tuple = ('yellow', 'foul')
        freq = ate.total_documents(paths, focus=tuple)
        self.assertEqual(int, type(freq))

        """
        Count the documents in which the tuple appears by reading all lines.
        """
        total = 0
        for path in paths:
            with open(path, 'r') as f:
                for line in f:
                    document = json.loads(line)
                    if all(token in document['tokens'] for token in tuple):
                        total += 1

        self.assertEqual(freq, total)

    def test_total_documents_multiple_tokens(self):
        """
        Test that when computing the number of documents in which tokens appear, the frequencies are correct.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]

        """
        Compute the probability for all tokens in the corpora first.
        """
        tokens = [ 'yellow', 'foul' ]
        freq = ate.total_documents(paths, focus=tokens)
        self.assertEqual(dict, type(freq))
        self.assertEqual(set(tokens), set(freq.keys()))

        """
        Count the documents in which the tokens appears by reading all lines.
        """
        counts = dict.fromkeys(tokens, 0)
        for path in paths:
            with open(path, 'r') as f:
                for line in f:
                    document = json.loads(line)
                    for token in tokens:
                        if token in document['tokens']:
                            counts[token] += 1

        self.assertEqual(counts, freq)

    def test_total_documents_multiple_tuples(self):
        """
        Test that when computing the number of documents in which tuples appear, the frequencies are correct.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]

        """
        Compute the probability for all tokens in the corpora first.
        """
        tuples = [ ('yellow', 'foul'), ('yellow', 'tackl') ]
        freq = ate.total_documents(paths, focus=tuples)
        self.assertEqual(dict, type(freq))
        self.assertEqual(set(tuples), set(freq.keys()))

        """
        Count the documents in which the tuples appears by reading all lines.
        """
        counts = dict.fromkeys(tuples, 0)
        for path in paths:
            with open(path, 'r') as f:
                for line in f:
                    document = json.loads(line)
                    for tuple in tuples:
                        if all(token in document['tokens'] for token in tuple):
                            counts[tuple] += 1

        self.assertEqual(counts, freq)

    def test_total_documents_mix(self):
        """
        Test that when computing the number of documents in which a mix of tokens and tuples appear, the frequencies are correct.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]

        """
        Compute the probability for all tokens in the corpora first.
        """
        focus = [ 'yellow', ('yellow', 'tackl') ]
        freq = ate.total_documents(paths, focus=focus)
        self.assertEqual(dict, type(freq))
        self.assertEqual(set(focus), set(freq.keys()))

        """
        Count the documents in which the tokens and tuples appears by reading all lines.
        """
        counts = dict.fromkeys(focus, 0)
        for path in paths:
            with open(path, 'r') as f:
                for line in f:
                    document = json.loads(line)
                    for itemset in focus:
                        if type(itemset) is str:
                            if itemset in document['tokens']:
                                counts[itemset] += 1
                        else:
                            if all(token in document['tokens'] for token in itemset):
                                counts[itemset] += 1

        self.assertEqual(counts, freq)

    def test_datatype_tokenized(self):
        """
        Test that the datatype of a tokenized corpus is a normal dictionary.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
        self.assertEqual(dict, ate.datatype(path))

    def test_datatype_timeline(self):
        """
        Test that the datatype of a timeline corpus is a timeline.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')
        self.assertEqual(timeline.Timeline, ate.datatype(path))
