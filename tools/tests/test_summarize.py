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
from queues.consumers.algorithms import ReportingLevel
from summarization.algorithms import MMR, DGS
from summarization import Summary
from summarization.timeline import Timeline
from summarization.timeline.nodes import Node, TopicalClusterNode
from tools import bootstrap, summarize
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

        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30, with_query=False)
        self.assertEqual(1, len(summaries[0][0].documents))
        self.assertEqual(str(documents[2]), str(summaries[0][0]))

        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30, with_query=True)
        self.assertEqual(1, len(summaries[0][0].documents))
        self.assertEqual(str(documents[2]), str(summaries[0][0]))

        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        timeline.add(cluster=cluster, topic=Vector({ 'this': 1 }))
        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30, with_query=True)
        self.assertEqual(1, len(summaries[0][0].documents))
        self.assertEqual(str(documents[1]), str(summaries[0][0]))

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

        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30, with_query=False)
        self.assertEqual(1, len(summaries[0][0].documents))
        self.assertEqual(str(documents[1]), str(summaries[0][0]))

        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30, with_query=True)
        self.assertEqual(1, len(summaries[0][0].documents))
        self.assertEqual(str(documents[2]), str(summaries[0][0]))

        timeline = Timeline(TopicalClusterNode, 60, 0.5)
        timeline.add(cluster=cluster, topic=Vector({ 'this': 1, 'pipe': 1 }))
        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30, with_query=True)
        self.assertEqual(1, len(summaries[0][0].documents))
        self.assertEqual(str(documents[0]), str(summaries[0][0]))

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

        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30, with_query=True)
        self.assertEqual(1, len(summaries[0][0].documents))
        self.assertEqual(query.dimensions, summaries[0][0].attributes['query'])

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

        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30, with_query=False)
        self.assertEqual(1, len(summaries[0][0].documents))
        self.assertFalse('query' in summaries[0][0].attributes)

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
        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30, with_query=True, max_documents=1, terms=terms)
        self.assertTrue(summaries[0][0].documents[0] in documents[1:])

        terms = [ 'pipe' ]
        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30, with_query=True, max_documents=1, terms=terms)
        self.assertEqual(documents[0], summaries[0][0].documents[0])

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

        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30)
        self.assertEqual(timestamp, summaries[0][0].attributes['timestamp'])

    def test_summarize_with_split(self):
        """
        Test that when summarizing a split timeline, each summary has a split attribute.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/#ParmaMilan-streams.json')
        timelines, splits = summarize.load_timeline(file), summarize.load_splits(file)
        summarizer = summarize.create_summarizer(MMR)
        combined = summarize.summarize(summarizer, timelines, splits)
        self.assertTrue(all( summary.attributes['split'] for summaries in combined for summary in summaries ))

    def test_tabulate_empty(self):
        """
        Test that when tabulating an empty list of summaries, another empty list is created.
        """

        self.assertEqual([ ], summarize.tabulate([ ], [ ]))

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

        summaries = summarize.summarize(summarizer, timeline, splits=[ ], length=30)
        headers = [ 'timestamp', 'query', 'summary' ]
        self.assertEqual(len(summaries), len(summarize.tabulate(summaries, headers)))

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

        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30)
        headers = [ 'timestamp', 'query', 'summary' ]
        tabulated = summarize.tabulate(summaries, headers)
        self.assertEqual(str(timestamp), tabulated[0][0])

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

        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30)
        headers = [ 'timestamp', 'query', 'summary' ]
        tabulated = summarize.tabulate(summaries, headers)
        self.assertTrue(all( round(query.dimensions[topic], 7) == round(dict(json.loads(tabulated[0][1]))[topic], 7)
                        for topic in query.dimensions ))

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

        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30)
        headers = [ 'timestamp', 'query', 'summary' ]
        tabulated = summarize.tabulate(summaries, headers)
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

        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30)
        headers = [ 'timestamp', 'query', 'summary' ]
        tabulated = summarize.tabulate(summaries, headers)
        decoded = json.loads(tabulated[0][1])
        self.assertEqual(max(query.dimensions, key=query.dimensions.get), decoded[0][0])
        self.assertEqual(min(query.dimensions, key=query.dimensions.get), decoded[-1][0])
        self.assertTrue(all( decoded[i][1] > decoded[i + 1][1]
                             for i in range(len(decoded) - 1) ))

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

        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30, with_query=False)
        headers = [ 'timestamp', 'query', 'summary' ]
        tabulated = summarize.tabulate(summaries, headers)
        self.assertEqual(json.dumps([ ]), tabulated[0][1])

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

        summaries = summarize.summarize(summarizer, timeline, splits=[], length=30)
        headers = [ 'timestamp', 'query', 'summary' ]
        tabulated = summarize.tabulate(summaries, headers)
        self.assertEqual(str, type(tabulated[0][-1]))
        self.assertTrue(any( tabulated[0][-1] == str(document) for document in documents ))

    def test_tabulate_with_splits(self):
        """
        Test that when tabulating a split timeline, the summary's splits are stored.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/#ParmaMilan-streams.json')
        timelines, splits = summarize.load_timeline(file), summarize.load_splits(file)
        summarizer = summarize.create_summarizer(MMR)
        summaries = summarize.summarize(summarizer, timelines, splits=splits, length=30)
        headers = [ 'timestamp', 'query', 'summary', 'split' ]
        tabulated = summarize.tabulate(summaries, headers)
        self.assertTrue(all( len(headers) == len(row) for row in tabulated ))

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

    def test_load_terms_from_bootstrapped(self):
        """
        Test that when loading the terms from the `bootstrap` tool's output, they are returned as a list.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'bootstrapped-new.json')
        terms = summarize.load_terms(file)
        self.assertEqual(bootstrap.load(file), summarize.load_terms(file))

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

    def test_construct_query_single_node_single_cluster(self):
        """
        Test that when computing the query with a single node that has only one cluster, the same query is returned.
        """

        query = Vector({ 'where': 1 })
        node = TopicalClusterNode(0, clusters=[ Cluster() ], topics=[ query ])
        self.assertEqual(query.dimensions, summarize.construct_query(node).dimensions)

    def test_construct_query_single_node_multiple_clusters(self):
        """
        Test that when computing the query with a single node that has more than one cluster, the centroid of topics is returned.
        """

        queries = [ Vector({ 'where': 1 }), Vector({ 'pipe': 1, 'cigar': 0.5 }) ]
        node = TopicalClusterNode(0, clusters=[ Cluster() ] * 2, topics=queries)
        self.assertEqual(Cluster(vectors=queries).centroid.dimensions,
                         summarize.construct_query(node).dimensions)

    def test_construct_query_list_nodes_multiple_clusters(self):
        """
        Test that when computing the query with a list of nodes, the centroid of their pooled topics is returned.
        """

        q1 = [ Vector({ 'where': 1 }), Vector({ 'pipe': 1, 'cigar': 0.5 }) ]
        n1 = TopicalClusterNode(0, clusters=[ Cluster() ] * 2, topics=q1)

        q2 = [ Vector({ 'pipe': 1, 'cigar': 0.5 }) ]
        n2 = TopicalClusterNode(0, clusters=[ Cluster() ], topics=q2)

        self.assertEqual(Cluster(vectors=q1+q2).centroid.dimensions,
                         summarize.construct_query([ n1, n2 ]).dimensions)

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

    def test_filter_documents_reporting_all(self):
        """
        Test that when filtering documents with the 'ALL' reporting strategy, all documents are returned.
        """

        documents = [ Document('a'), Document('b'), Document('c') ]
        self.assertEqual(documents, summarize.filter_documents(documents, reporting=ReportingLevel.ALL))

    def test_filter_documents_reporting_original_no_retweets(self):
        """
        Test that when filtering documents with the 'ORIGINAL' reporting strategy, if no documents are retweets, they are all returned.
        """

        documents = [ Document('a', attributes={ 'is_retweet': False }),
                      Document('b', attributes={ 'is_retweet': False }),
                      Document('c', attributes={ 'is_retweet': False }) ]
        self.assertEqual(documents, summarize.filter_documents(documents, reporting=ReportingLevel.ORIGINAL))

    def test_filter_documents_reporting_original_no_retweets_from_tweet(self):
        """
        Test that when filtering documents with the 'ORIGINAL' reporting strategy, if no documents are retweets, they are all returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', "CRYCHE-100.json")
        with open(file) as f:
            tweets = [ json.loads(line) for line in f ]
            documents = [ Document.from_dict(tweet) for tweet in tweets ]
            documents = [ document for document in documents if not document.is_retweet ]
            for document in documents:
                del document.attributes['is_retweet']

        self.assertTrue(not any( document.is_retweet for document in documents ))
        self.assertTrue(documents)
        self.assertEqual(documents, summarize.filter_documents(documents, reporting=ReportingLevel.ORIGINAL))

    def test_filter_documents_reporting_original_only(self):
        """
        Test that when filtering documents with the 'ORIGINAL' reporting strategy, original tweets are returned.
        """

        documents = [ Document('a', attributes={ 'is_retweet': True }),
                      Document('b', attributes={ 'is_retweet': False }),
                      Document('c', attributes={ 'is_retweet': True }) ]
        filtered = summarize.filter_documents(documents, reporting=ReportingLevel.ORIGINAL)
        self.assertFalse(documents[0] in filtered)
        self.assertTrue(documents[1] in filtered)
        self.assertFalse(documents[0] in filtered)
        self.assertTrue(all( not document.is_retweet for document in filtered ))

    def test_filter_documents_reporting_original_original_only_from_tweet(self):
        """
        Test that when filtering documents with the 'ORIGINAL' reporting strategy, original tweets are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', "CRYCHE-100.json")
        with open(file) as f:
            tweets = [ json.loads(line) for line in f ]
            documents = [ Document.from_dict(tweet) for tweet in tweets ]
            for document in documents:
                del document.attributes['is_retweet']

        self.assertTrue(documents)
        filtered = summarize.filter_documents(documents, reporting=ReportingLevel.ORIGINAL)
        self.assertTrue(all( not document.is_retweet for document in filtered ))

    def test_filter_documents_reporting_original_all_retweets(self):
        """
        Test that when filtering documents with the 'ORIGINAL' reporting strategy, all tweets are returned if they are all retweets.
        """

        documents = [ Document('a', attributes={ 'is_retweet': True }),
                      Document('b', attributes={ 'is_retweet': True }),
                      Document('c', attributes={ 'is_retweet': True }) ]
        self.assertEqual(documents, summarize.filter_documents(documents, reporting=ReportingLevel.ORIGINAL))

    def test_filter_documents_reporting_original_all_retweets_from_tweet(self):
        """
        Test that when filtering documents with the 'ORIGINAL' reporting strategy, all tweets are returned if they are all retweets.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', "CRYCHE-100.json")
        with open(file) as f:
            tweets = [ json.loads(line) for line in f ]
            documents = [ Document.from_dict(tweet) for tweet in tweets ]
            documents = [ document for document in documents if document.is_retweet ]
            for document in documents:
                del document.attributes['is_retweet']

            # remove duplicates
            filtered = { document.text.lower(): document for document in documents }
            documents = [ document for document in documents
                                   if document in filtered.values() ]

        self.assertTrue(documents)
        self.assertEqual(documents, summarize.filter_documents(documents, reporting=ReportingLevel.ORIGINAL))

    def test_filter_documents_reporting_verified_no_verified(self):
        """
        Test that when filtering documents with the 'VERIFIED' reporting strategy, if no documents are verified, they are all returned.
        """

        documents = [ Document('a', attributes={ 'is_verified': False }),
                      Document('b', attributes={ 'is_verified': False }),
                      Document('c', attributes={ 'is_verified': False }) ]
        self.assertEqual(documents, summarize.filter_documents(documents, reporting=ReportingLevel.VERIFIED))

    def test_filter_documents_reporting_verified_no_verified_from_tweet(self):
        """
        Test that when filtering documents with the 'VERIFIED' reporting strategy, if no documents are verified, they are all returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', "CRYCHE-100.json")
        with open(file) as f:
            tweets = [ json.loads(line) for line in f ]
            documents = [ Document.from_dict(tweet) for tweet in tweets ]
            documents = [ document for document in documents if not document.is_verified ]
            for document in documents:
                del document.attributes['is_verified']

            # remove duplicates
            filtered = { document.text.lower(): document for document in documents }
            documents = [ document for document in documents
                                   if document in filtered.values() ]

        self.assertTrue(not any( document.is_verified for document in documents ))
        self.assertTrue(documents)
        self.assertEqual(documents, summarize.filter_documents(documents, reporting=ReportingLevel.VERIFIED))

    def test_filter_documents_reporting_verified_only(self):
        """
        Test that when filtering documents with the 'VERIFIED' reporting strategy, verified tweets are returned.
        """

        documents = [ Document('a', attributes={ 'is_verified': True }),
                      Document('b', attributes={ 'is_verified': False }),
                      Document('c', attributes={ 'is_verified': True }) ]
        filtered = summarize.filter_documents(documents, reporting=ReportingLevel.VERIFIED)
        self.assertTrue(documents[0] in filtered)
        self.assertFalse(documents[1] in filtered)
        self.assertTrue(documents[0] in filtered)
        self.assertTrue(all( document.is_verified for document in filtered ))

    def test_filter_documents_reporting_verified_only_from_tweet(self):
        """
        Test that when filtering documents with the 'VERIFIED' reporting strategy, verified tweets are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', "CRYCHE-500.json")
        with open(file) as f:
            tweets = [ json.loads(line) for line in f ]
            documents = [ Document.from_dict(tweet) for tweet in tweets ]
            for document in documents:
                del document.attributes['is_verified']

        self.assertTrue(not any( document.is_verified for document in documents ))
        self.assertTrue(all( document.is_verified for document in summarize.filter_documents(documents, reporting=ReportingLevel.VERIFIED) ))

    def test_filter_documents_reporting_verified_all_verified(self):
        """
        Test that when filtering documents with the 'VERIFIED' reporting strategy, all tweets are returned if they are all verified.
        """

        documents = [ Document('a', attributes={ 'is_verified': True }),
                      Document('b', attributes={ 'is_verified': True }),
                      Document('c', attributes={ 'is_verified': True }) ]
        self.assertEqual(documents, summarize.filter_documents(documents, reporting=ReportingLevel.VERIFIED))

    def test_filter_documents_reporting_verified_all_verified_from_tweet(self):
        """
        Test that when filtering documents with the 'VERIFIED' reporting strategy, all tweets are returned if they are all verified.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', "CRYCHE-100.json")
        with open(file) as f:
            tweets = [ json.loads(line) for line in f ]
            documents = [ Document.from_dict(tweet) for tweet in tweets ]
            documents = [ document for document in documents if document.is_verified ]
            for document in documents:
                del document.attributes['is_verified']

            # remove duplicates
            filtered = { document.text.lower(): document for document in documents }
            documents = [ document for document in documents
                                   if document in filtered.values() ]

        self.assertTrue(not any( document.is_verified for document in documents ))
        self.assertTrue(documents)
        self.assertEqual(documents, summarize.filter_documents(documents, reporting=ReportingLevel.VERIFIED))

    def test_load_splits_old_file(self):
        """
        Test loading the splits from an old file that uses no splits.
        The function should return an empty list.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/CRYCHE.json')
        splits = summarize.load_splits(file)
        self.assertEqual([ ], splits)

    def test_load_splits_streamed_timeline(self):
        """
        Test loading the splits from a timeline that has splits.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/#ParmaMilan-streams.json')
        splits = summarize.load_splits(file)
        with open(file) as f:
            streams = json.loads(f.readline())['pcmd']['splits']
            self.assertEqual(streams, splits)

    def test_combine_list_of_lists(self):
        """
        Test that when combining a simple timeline, the nodes are returned as a list of list of nodes.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/CRYCHE.json')
        timeline = summarize.load_timeline(file)
        combined = summarize.combine(timeline)
        self.assertTrue(list, type(combined))
        self.assertTrue(all( list == type(nodes) for nodes in combined ))
        self.assertTrue(all( isinstance(node, Node) for nodes in combined for node in nodes ))

    def test_combine_simple_node_per_list(self):
        """
        Test that when combining a simple timeline, each list has only one node.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/CRYCHE.json')
        timeline = summarize.load_timeline(file)
        combined = summarize.combine(timeline)
        self.assertTrue(all( 1 == len(nodes) for nodes in combined ))

    def test_combine_simple_all_nodes(self):
        """
        Test that when combining a simple timeline, all nodes are present.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/CRYCHE.json')
        timeline = summarize.load_timeline(file)
        combined = summarize.combine(timeline)
        self.assertEqual(len(timeline.nodes), len(combined))
        self.assertTrue(all( _og == nodes[0] for _og, nodes in zip(timeline.nodes, combined) ))

    def test_combine_split_list_of_lists(self):
        """
        Test that when combining a split timeline, the nodes are returned as a list of list of nodes.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/#ParmaMilan-streams.json')
        timelines, splits = summarize.load_timeline(file), summarize.load_splits(file)
        combined = summarize.combine(timelines, splits)
        self.assertTrue(list, type(combined))
        self.assertTrue(all( list == type(nodes) for nodes in combined ))
        self.assertTrue(all( isinstance(node, Node) for nodes in combined for node in nodes ))

    def test_combine_split_all_nodes(self):
        """
        Test that when combining a split timeline, all nodes are present.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/#ParmaMilan-streams.json')
        timelines, splits = summarize.load_timeline(file), summarize.load_splits(file)
        combined = summarize.combine(timelines, splits)
        self.assertEqual(len([ node for timeline in timelines for node in timeline.nodes ]),
                             len([ node for nodes in combined for node in nodes ]))
        self.assertTrue(all( any( node in nodes for nodes in combined ) for timeline in timelines for node in timeline.nodes))

    def test_combine_split_all_nodes_similar_time(self):
        """
        Test that all nodes in the same list have a similar time.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/#ParmaMilan-streams.json')
        timelines, splits = summarize.load_timeline(file), summarize.load_splits(file)
        combined = summarize.combine(timelines, splits)

        # check the expiry of each list of nodes
        expiry = timelines[0].expiry
        for nodes in combined:
            self.assertTrue(nodes[-1].created_at - nodes[0].created_at <= expiry)

    def test_combine_split_chronological_lists(self):
        """
        Test that the node lists are ordered chronologically.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/#ParmaMilan-streams.json')
        timelines, splits = summarize.load_timeline(file), summarize.load_splits(file)
        combined = summarize.combine(timelines, splits)

        self.assertTrue(all( combined[i][0].created_at < combined[i + 1][0].created_at
                             for i in range(len(combined) - 1) ))

    def test_combine_split_chronological_nodes(self):
        """
        Test that the nodes in the lists are ordered chronologically.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/#ParmaMilan-streams.json')
        timelines, splits = summarize.load_timeline(file), summarize.load_splits(file)
        combined = summarize.combine(timelines, splits)

        for nodes in combined:
            self.assertTrue(all( nodes[i].created_at < nodes[i + 1].created_at for i in range(len(nodes) - 1) ))

    def test_combine_split_saves_split_attribute(self):
        """
        Test that when combining timelines, the split is saved as an attribute.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/#ParmaMilan-streams.json')
        timelines, splits = summarize.load_timeline(file), summarize.load_splits(file)
        combined = summarize.combine(timelines, splits)
        self.assertTrue(all( 'split' in node.attributes for nodes in combined for node in nodes ))

    def test_combine_split_correct_split(self):
        """
        Test that when combining timelines, the correct split is saved as an attribute.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/timelines/#ParmaMilan-streams.json')
        timelines, splits = summarize.load_timeline(file), summarize.load_splits(file)
        combined = summarize.combine(timelines, splits)
        for timeline, split in zip(timelines, splits):
            self.assertTrue(all( split == node.attributes['split'] for node in timeline.nodes ))
