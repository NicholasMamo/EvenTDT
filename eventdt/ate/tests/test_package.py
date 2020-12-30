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
from objects.exportable import Exportable
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

    def test_total_documents_timeline_empty_corpus(self):
        """
        Test that the number of documents in an empty timeline corpus is 0.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'timelines', 'empty.json')
        documents = ate.total_documents(path)
        self.assertEqual(0, documents)

    def test_total_documents_timeline_int(self):
        """
        Test that the number of documents in timeline corpus is always an integer.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')
        documents = ate.total_documents(path)
        self.assertEqual(int, type(documents))

    def test_total_documents_timeline_token(self):
        """
        Test that when computing the number of documents in which one token appears, the frequency considers only the topical keywords.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')

        token = 'via'
        with open(path) as f:
            timeline = Exportable.decode(json.loads(f.readline()))['timeline']
            nodes = len([ node for node in timeline.nodes
                          if token in [ keyword for topic in node.topics for keyword in topic.dimensions ] ])
            self.assertTrue(nodes) # check that the result isn't 0: a trivial test
            documents = ate.total_documents(path, focus=token)
            self.assertEqual(nodes, documents)

    def test_total_documents_timeline_tuple(self):
        """
        Test that when computing the number of documents in which a tuple of tokens appears, the frequency considers only the topical keywords.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')

        tuple = ('via', 'direct')
        with open(path) as f:
            timeline = Exportable.decode(json.loads(f.readline()))['timeline']
            nodes = 0
            for node in timeline.nodes:
                keywords = [ keyword for topic in node.topics
                                     for keyword in topic.dimensions ]
                if all( token in keywords for token in tuple ):
                    nodes += 1
            self.assertTrue(nodes) # check that the result isn't 0: a trivial test
            documents = ate.total_documents(path, focus=tuple)
            self.assertEqual(nodes, documents)

    def test_total_documents_timeline_multiple_tokens(self):
        """
        Test that when computing the number of documents in which multiple tokens appear, the frequency considers only the topical keywords.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')

        tokens = [ 'crystal', 'bissaka', 'underway' ]
        with open(path) as f:
            timeline = Exportable.decode(json.loads(f.readline()))['timeline']
            documents = ate.total_documents(path, focus=tokens)
            for token in tokens:
                nodes = len([ node for node in timeline.nodes
                              if token in [ keyword for topic in node.topics for keyword in topic.dimensions ] ])
                self.assertTrue(nodes) # check that the result isn't 0: a trivial test
                self.assertEqual(nodes, documents[token])

    def test_total_documents_timeline_multiple_tuples(self):
        """
        Test that when computing the number of documents in which multiple tuples of tokens appears, the frequency considers only the topical keywords.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')

        tuples = [ ('via', 'direct'), ('golo', 'shoot'), ('minut', 'underway') ]
        with open(path) as f:
            timeline = Exportable.decode(json.loads(f.readline()))['timeline']
            documents = ate.total_documents(path, focus=tuples)
            for tuple in tuples:
                nodes = 0
                for node in timeline.nodes:
                    keywords = [ keyword for topic in node.topics
                                         for keyword in topic.dimensions ]
                    if all( token in keywords for token in tuple ):
                        nodes += 1
                self.assertTrue(nodes) # check that the result isn't 0: a trivial test
                self.assertEqual(nodes, documents[tuple])

    def test_total_documents_timeline_mix(self):
        """
        Test that when computing the number of nodes in which a mix of tokens and tuples appear, the frequencies are correct.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')

        mix = [ 'minut', ('underway', 'minut') ]
        with open(path) as f:
            timeline = Exportable.decode(json.loads(f.readline()))['timeline']
            documents = ate.total_documents(path, focus=mix)
            for focus in mix:
                nodes = 0
                for node in timeline.nodes:
                    keywords = [ keyword for topic in node.topics
                                         for keyword in topic.dimensions ]
                    if type(focus) is str:
                        if focus in keywords:
                            nodes += 1
                    else:
                        if all( token in keywords for token in focus ):
                            nodes += 1
                self.assertTrue(nodes) # check that the result isn't 0: a trivial test
                self.assertEqual(nodes, documents[focus])

    def test_total_documents_timeline_tuple_in_different_topics(self):
        """
        Test that when computing the number of documents in which a tuple of tokens appears, the frequency considers all topics in a node, so tokens may be scattered in different topics.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')

        tuple = ('via', 'watch')
        with open(path) as f:
            timeline = Exportable.decode(json.loads(f.readline()))['timeline']
            nodes = 0
            for node in timeline.nodes:
                keywords = [ keyword for topic in node.topics
                                     for keyword in topic.dimensions ]
                if all( token in keywords for token in tuple ):
                    nodes += 1
            self.assertTrue(nodes) # check that the result isn't 0: a trivial test
            documents = ate.total_documents(path, focus=tuple)
            self.assertEqual(nodes, documents)

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

    def test_datatype_empty_timeline(self):
        """
        Test that the datatype of an empty timeline is `None`.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'timelines', 'empty.json')
        self.assertEqual(timeline.Timeline, ate.datatype(path))

    def test_datatype_empty(self):
        """
        Test that the datatype of an empty corpus is `None`.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'tokenized', 'empty.json')
        self.assertEqual(None, ate.datatype(path))
