"""
Test the functionality of the summarization tool.
"""

from datetime import datetime
import json
import math
import os
import re
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
           os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from nlp import Document
from summarization.algorithms import MMR, DGS
from summarization import Summary
from summarization.timeline import Timeline
from summarization.timeline.nodes import TopicalClusterNode
from tools import summarize
from vsm import Vector
from vsm.clustering import Cluster

class TestSummarize(unittest.TestCase):
    """
    Test the functionality of the summarization tool.
    """

    def test_create_mmr_custom_lambda(self):
        """
        Test that when creating MMR with a custom lambda, it is saved
        """

        summarizer = summarize.create_summarizer(MMR, l=0.7)
        self.assertEqual(0.7, summarizer.l)

    def test_summarize_dgs_with_query(self):
        """
        Test that when summarizing using the DGS algorithm with a query, the summaries are more topical.
        """

        summarizer = summarize.create_summarizer(DGS)
        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                       Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
                      Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
        cluster = Cluster(documents)
        timeline.add(cluster=cluster, topic=Vector({ 'where': 1 }))

        summaries = summarize.summarize(summarizer, timeline, length=30, with_query=False)
        self.assertEqual(1, len(summaries[0].documents))
        self.assertEqual(str(documents[2]), str(summaries[0]))

        summaries = summarize.summarize(summarizer, timeline, length=30, with_query=True)
        self.assertEqual(1, len(summaries[0].documents))
        self.assertEqual(str(documents[2]), str(summaries[0]))

        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        timeline.add(cluster=cluster, topic=Vector({ 'this': 1 }))
        summaries = summarize.summarize(summarizer, timeline, length=30, with_query=True)
        self.assertEqual(1, len(summaries[0].documents))
        self.assertEqual(str(documents[1]), str(summaries[0]))

    def test_summarize_mmr_with_query(self):
        """
        Test that when summarizing using the MMR algorithm with a query, the summaries are more topical.
        """

        summarizer = summarize.create_summarizer(MMR)
        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                       Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
                      Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
        cluster = Cluster(documents)
        timeline.add(cluster=cluster, topic=Vector({ 'where': 1 }))

        summaries = summarize.summarize(summarizer, timeline, length=30, with_query=False)
        self.assertEqual(1, len(summaries[0].documents))
        self.assertEqual(str(documents[1]), str(summaries[0]))

        summaries = summarize.summarize(summarizer, timeline, length=30, with_query=True)
        self.assertEqual(1, len(summaries[0].documents))
        self.assertEqual(str(documents[2]), str(summaries[0]))

        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        timeline.add(cluster=cluster, topic=Vector({ 'this': 1, 'pipe': 1 }))
        summaries = summarize.summarize(summarizer, timeline, length=30, with_query=True)
        self.assertEqual(1, len(summaries[0].documents))
        self.assertEqual(str(documents[0]), str(summaries[0]))

    def test_summarize_with_query(self):
        """
        Test that when summarizing with a query, the queries are stored alongside the summary.
        """

        query = Vector({ 'where': 1 })

        summarizer = summarize.create_summarizer(MMR)
        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                       Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
                      Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
        cluster = Cluster(documents)
        timeline.add(cluster=cluster, topic=query)

        summaries = summarize.summarize(summarizer, timeline, length=30, with_query=True)
        self.assertEqual(1, len(summaries[0].documents))
        self.assertEqual(query.dimensions, summaries[0].attributes['query'])

    def test_summarize_without_query(self):
        """
        Test that when summarizing without a query, no queries are generated or stored alongside the summary.
        """

        query = Vector({ 'where': 1 })

        summarizer = summarize.create_summarizer(MMR)
        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                       Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
                      Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
        cluster = Cluster(documents)
        timeline.add(cluster=cluster, topic=query)

        summaries = summarize.summarize(summarizer, timeline, length=30, with_query=False)
        self.assertEqual(1, len(summaries[0].documents))
        self.assertFalse('query' in summaries[0].attributes)

    def test_summarize_with_domain_terms(self):
        """
        Test that when summarizing with domain terms, they are used to rank documents instead of quality indicators.
        """

        summarizer = summarize.create_summarizer(MMR)
        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                       Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
                      Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
        cluster = Cluster(documents)
        timeline.add(cluster=cluster, topic=Vector({ 'cigar': 1, 'pipe': 1 })) # no discrimination here

        terms = [ 'cigar' ]
        summaries = summarize.summarize(summarizer, timeline, length=30, with_query=True, max_documents=1, terms=terms)
        self.assertTrue(summaries[0].documents[0] in documents[1:])

        terms = [ 'pipe' ]
        summaries = summarize.summarize(summarizer, timeline, length=30, with_query=True, max_documents=1, terms=terms)
        self.assertEqual(documents[0], summaries[0].documents[0])

    def test_summarize_stores_created_at(self):
        """
        Test that when summarizing, the function stores the summary's time as an attribute.
        """

        timestamp = datetime.now().timestamp()

        summarizer = summarize.create_summarizer(MMR)
        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                       Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
                      Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
        cluster = Cluster(documents)
        timeline.add(timestamp=timestamp, cluster=cluster, topic=Vector({ 'cigar': 1, 'pipe': 1 })) # no discrimination here

        summaries = summarize.summarize(summarizer, timeline, length=30)
        self.assertEqual(timestamp, summaries[0].attributes['timestamp'])

    def test_tabulate_empty(self):
        """
        Test that when tabulating an empty list of summaries, another empty list is created.
        """

        self.assertEqual([ ], summarize.tabulate([ ]))

    def test_tabulate_equal_to_summaries(self):
        """
        Test that when tabulating summaries, the outer list contains as many lists as the number of summaries.
        """

        timestamp = datetime.now().timestamp()
        summarizer = summarize.create_summarizer(MMR)
        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                       Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
                      Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
        cluster = Cluster(documents)
        timeline.add(timestamp=timestamp, cluster=cluster, topic=Vector({ 'cigar': 1, 'pipe': 1 })) # no discrimination here

        summaries = summarize.summarize(summarizer, timeline, length=30)
        self.assertEqual(len(summaries), len(summarize.tabulate(summaries)))

    def test_tabulate_includes_timestamp(self):
        """
        Test that when tabulating summaries, the first column is the timestamp.
        """

        timestamp = datetime.now().timestamp()
        summarizer = summarize.create_summarizer(MMR)
        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                       Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
                      Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
        cluster = Cluster(documents)
        timeline.add(timestamp=timestamp, cluster=cluster, topic=Vector({ 'cigar': 1, 'pipe': 1 })) # no discrimination here

        summaries = summarize.summarize(summarizer, timeline, length=30)
        tabulated = summarize.tabulate(summaries)
        self.assertEqual(timestamp, tabulated[0][0])

    def test_tabulate_includes_query(self):
        """
        Test that when tabulating summaries, the second column is the query.
        """

        query = Vector({ 'cigar': 1, 'pipe': 1 })
        query.normalize()
        timestamp = datetime.now().timestamp()
        summarizer = summarize.create_summarizer(MMR)
        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                       Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
                      Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
        cluster = Cluster(documents)
        timeline.add(timestamp=timestamp, cluster=cluster, topic=query) # no discrimination here

        summaries = summarize.summarize(summarizer, timeline, length=30)
        tabulated = summarize.tabulate(summaries)
        self.assertTrue(all( round(query.dimensions[topic], 7) == round(json.loads(tabulated[0][1])[topic], 7) for topic in query.dimensions ))

    def test_tabulate_query_string(self):
        """
        Test that when tabulating summaries, the query is stored as a string.
        """

        query = Vector({ 'cigar': 1, 'pipe': 1 })
        query.normalize()
        timestamp = datetime.now().timestamp()
        summarizer = summarize.create_summarizer(MMR)
        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                       Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
                      Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
        cluster = Cluster(documents)
        timeline.add(timestamp=timestamp, cluster=cluster, topic=query) # no discrimination here

        summaries = summarize.summarize(summarizer, timeline, length=30)
        tabulated = summarize.tabulate(summaries)
        self.assertEqual(str, type(tabulated[0][1]))

    def test_tabulate_query_ordered(self):
        """
        Test that when tabulating summaries, the query is sorted in descending order of weight.
        """

        query = Vector({ 'cigar': 0.8, 'pipe': 1 })
        timestamp = datetime.now().timestamp()
        summarizer = summarize.create_summarizer(MMR)
        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                       Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
                      Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
        cluster = Cluster(documents)
        timeline.add(timestamp=timestamp, cluster=cluster, topic=query) # no discrimination here

        summaries = summarize.summarize(summarizer, timeline, length=30)
        tabulated = summarize.tabulate(summaries)
        decoded = json.loads(tabulated[0][1])
        self.assertEqual(max(query.dimensions, key=query.dimensions.get), list(decoded.keys())[0])
        self.assertEqual(min(query.dimensions, key=query.dimensions.get), list(decoded.keys())[-1])
        self.assertTrue(all( decoded[list(decoded.keys())[i]] > decoded[list(decoded.keys())[i + 1]]
                             for i in range(len(decoded.keys()) - 1) ))

    def test_tabulate_no_query(self):
        """
        Test that if the summary is created without a query, the tabulated summaries have an empty query.
        """

        query = Vector({ 'cigar': 1, 'pipe': 1 })
        query.normalize()
        timestamp = datetime.now().timestamp()
        summarizer = summarize.create_summarizer(MMR)
        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                       Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
                      Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
        cluster = Cluster(documents)
        timeline.add(timestamp=timestamp, cluster=cluster, topic=query) # no discrimination here

        summaries = summarize.summarize(summarizer, timeline, length=30, with_query=False)
        tabulated = summarize.tabulate(summaries)
        self.assertEqual(json.dumps({ }), tabulated[0][1])

    def test_tabulate_includes_summary(self):
        """
        Test that when tabulating summaries, the last column is the actual summary.
        """

        timestamp = datetime.now().timestamp()
        summarizer = summarize.create_summarizer(MMR)
        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                       Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
                      Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
        cluster = Cluster(documents)
        timeline.add(timestamp=timestamp, cluster=cluster, topic=Vector({ 'cigar': 1, 'pipe': 1 })) # no discrimination here

        summaries = summarize.summarize(summarizer, timeline, length=30)
        tabulated = summarize.tabulate(summaries)
        self.assertEqual(str, type(tabulated[0][-1]))
        self.assertTrue(any( tabulated[0][-1] == str(document) for document in documents ))

    def test_load_terms_all_words(self):
        """
        Test that when loading the terms, all words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        terms = summarize.load_terms(file)

        """
        Assert that the correct number of terms are loaded.
        """
        self.assertEqual(30, len(terms))

        """
        Load each term set separately and ensure it has been loaded.
        """
        with open(file, 'r') as f:
            for word in f:
                self.assertTrue(word.strip() in terms)

    def test_load_terms_list(self):
        """
        Test that when loading the terms, they are returned as a list.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        terms = summarize.load_terms(file)

        """
        Assert that the terms list is returned as a list.
        """
        self.assertEqual(list, type(terms))

    def test_load_terms_from_terms(self):
        """
        Test that when loading the terms from the `terms` tool's output, they are returned as a list.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json')
        terms = summarize.load_terms(file)

        """
        Assert that the terms list is returned as a list.
        """
        self.assertEqual(list, type(terms))
        self.assertTrue(len(terms))

    def test_load_terms_no_newlines(self):
        """
        Test that when loading the terms, the newline symbol is removed.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        terms = summarize.load_terms(file)

        """
        Assert that the terms list is returned as a list.
        """
        self.assertTrue(all( '\n' not in word for word in terms ))

    def test_load_terms_max_terms_zero(self):
        """
        Test that when loading the terms and keeping zero words, a ``ValueError`` is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        self.assertRaises(ValueError, summarize.load_terms, file, 0)

    def test_load_terms_max_terms_negative(self):
        """
        Test that when loading the terms and keeping negative words, a ``ValueError`` is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        self.assertRaises(ValueError, summarize.load_terms, file, -1)

    def test_load_terms_max_terms_respected(self):
        """
        Test that when loading the terms, the specified number of words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        terms = summarize.load_terms(file, 10)
        self.assertEqual(10, len(terms))

    def test_load_terms_max_terms_top_words(self):
        """
        Test that when loading the terms with a cutoff, the top words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        all = summarize.load_terms(file)
        terms = summarize.load_terms(file, 10)
        self.assertEqual(all[:10], terms)

    def test_load_terms_max_terms_very_large(self):
        """
        Test that when loading the terms with a large cutoff, all words are retained.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        terms = summarize.load_terms(file, 50)
        self.assertEqual(30, len(terms))

    def test_load_terms_max_terms_none(self):
        """
        Test that when loading the terms with no specified cutoff, all words are retained.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        terms = summarize.load_terms(file, None)
        self.assertEqual(30, len(terms))

    def test_load_terms_empty(self):
        """
        Test that when the terms file is empty, a ``ValueError`` is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'empty.txt')
        self.assertRaises(ValueError, summarize.load_terms, file)

    def test_filter_documents_order(self):
        """
        Test that when filtering documents, the documents are returned in the same order.
        """

        documents = [ Document('a'), Document('b'), Document('c') ]
        self.assertEqual(documents, summarize.filter_documents(documents))

    def test_filter_documents_with_duplicates(self):
        """
        Test that when filtering documents, duplicates are removed automatically.
        """

        documents = [ Document('a'), Document('b'), Document('c'), Document('a') ]
        self.assertEqual(documents[-3:], summarize.filter_documents(documents))

    def test_filter_documents_with_duplicates_case_insensitive(self):
        """
        Test that when filtering documents, duplicates are removed automatically even if they have different capitalization.
        """

        documents = [ Document('a'), Document('b'), Document('c'), Document('A') ]
        self.assertEqual(documents[-3:], summarize.filter_documents(documents))

    def test_filter_documents_empty(self):
        """
        Test that when filtering an empty list of documents, another empty list is returned.
        """

        documents = [ ]
        self.assertEqual([ ], summarize.filter_documents(documents))

    def test_filter_documents_None(self):
        """
        Test that when filtering a list of documents, if no maximum number of documents is given, all documents are retained.
        """

        documents = [ Document('a'), Document('b'), Document('c') ]
        self.assertEqual(documents, summarize.filter_documents(documents, max_documents=None))

    def test_filter_documents_too_few(self):
        """
        Test that when filtering a list of documents, if the maximum number of documents exceed the number of documents, all documents are returned.
        """

        documents = [ Document('a'), Document('b'), Document('c') ]
        self.assertEqual(documents, summarize.filter_documents(documents, max_documents=len(documents)+1))

    def test_filter_documents_longest(self):
        """
        Test that when filtering a list of documents, the longest documents are returned.
        """

        documents = [ Document('aaa'), Document('bb'), Document('c') ]
        self.assertEqual(documents[:2], summarize.filter_documents(documents, max_documents=2))

    def test_filter_documents_with_domain_terms(self):
        """
        Test that when filtering documents and providing the domain terms, they are used to rank documents.
        """

        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                      Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]

        terms = [ 'pipe' ]
        self.assertEqual(documents[0], summarize.filter_documents(documents, max_documents=1, terms=terms)[0])

        terms = [ 'cigar' ]
        self.assertEqual(documents[1], summarize.filter_documents(documents, max_documents=1, terms=terms)[0])

    def test_filter_documents_break_ties(self):
        """
        Test that when filtering documents and providing the domain terms, ties are broken using quality indicators.
        """

        documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                      Document('this is not a pipe ... or is it?', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
                      Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]

        terms = [ 'pipe' ]
        self.assertEqual(documents[1], summarize.filter_documents(documents, max_documents=1, terms=terms)[0])

        terms = [ 'cigar' ]
        self.assertEqual(documents[2], summarize.filter_documents(documents, max_documents=1, terms=terms)[0])
