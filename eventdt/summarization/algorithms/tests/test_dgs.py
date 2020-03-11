"""
Run unit tests on the Document Graph Summarizer by Mamo et al. (2019)'s algorithm.
"""

import math
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from nlp.term_weighting.tf import TF
from summarization import Summary
from summarization.algorithms import DGS
from vsm import vector_math

class TestDGS(unittest.TestCase):
	"""
	Test Document Graph Summarizer by Mamo et al. (2019)'s algorithm.
	"""

	def test_negative_length(self):
		"""
		Test that when providing a negative length, the function raises a ValueError.
		"""

		c = [ ]
		algo = DGS()
		self.assertRaises(ValueError, algo.summarize, c, -1)

	def test_zero_length(self):
		"""
		Test that when providing a length of zero, the function raises a ValueError.
		"""

		c = [ ]
		algo = DGS()
		self.assertRaises(ValueError, algo.summarize, c, 0)

	def test_compute_query_empty(self):
		"""
		Test that the query is empty when no documents are given.
		"""

		algo = DGS()
		self.assertEqual({ }, algo._compute_query([ ]).dimensions)

	def test_compute_query_one_document(self):
		"""
		Test that the query construction is identical to the given document when there is just one document.
		"""

		d = Document('this is not a pipe', { 'pipe': 1 })
		algo = DGS()
		self.assertEqual(d.dimensions, algo._compute_query([ d ]).dimensions)

	def test_compute_query_normalized(self):
		"""
		Test that the query is normallized.
		"""

		d = Document('this is not a pipe', { 'this': 1, 'pipe': 1 })
		d.normalize()
		algo = DGS()
		self.assertEqual(1, round(vector_math.magnitude(algo._compute_query([ d ])), 10))

	def test_compute_query(self):
		"""
		Test the query construction with multiple documents.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a pipe', { 'this': 1 }),
		 		   Document('this is not a pipe', { 'pipe': 1 }) ]

		algo = DGS()
		self.assertEqual(round(math.sqrt(2)/2., 10), round(algo._compute_query(corpus).dimensions['this'], 10))
		self.assertEqual(round(math.sqrt(2)/2., 10), round(algo._compute_query(corpus).dimensions['pipe'], 10))
		self.assertEqual(1, round(vector_math.magnitude(algo._compute_query(corpus)), 10))

	def test_create_empty_graph(self):
		"""
		Test that when creating a graph with no documents, an empty graph is created instead.
		"""

		algo = DGS()
		graph = algo._to_graph([ ])
		self.assertEqual([ ], list(graph.nodes))
		self.assertEqual([ ], list(graph.edges))

	def test_create_graph_one_document(self):
		"""
		Test that when creating a graph with one document, a graph with one node and no edges is created.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a pipe', { 'this': 1 }) ]

		algo = DGS()
		graph = algo._to_graph(corpus)
		self.assertEqual(corpus, list(graph.nodes))
		self.assertEqual([ ], list(graph.edges))

	def test_create_graph_different_documents(self):
		"""
		Test that when creating a graph with different documents, no edge is created between them.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a pipe', { 'pipe': 1 }),
		 		   Document('this is not a cigar', { 'cigar': 1 }), ]

		algo = DGS()
		graph = algo._to_graph(corpus)
		self.assertEqual(corpus, list(graph.nodes))
		self.assertEqual([ ], list(graph.edges))

	def test_create_graph_similar_documents(self):
		"""
		Test that when creating a graph with similar documents, edges are created between them.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a pipe', { 'pipe': 1 }),
		 		   Document('this is not a cigar', { 'cigar': 1 }),
				   Document('this is not a pipe, but a cigar', { 'pipe': 1, 'cigar': 1 }), ]
		for document in corpus:
			document.normalize()

		algo = DGS()
		graph = algo._to_graph(corpus)
		self.assertEqual(corpus, list(graph.nodes))
		self.assertEqual(2, len(list(graph.edges)))
		self.assertTrue((corpus[0], corpus[2]) in graph.edges)
		self.assertTrue((corpus[1], corpus[2]) in graph.edges)

	def test_create_graph_triangle(self):
		"""
		Test that when creating a graph with three documents, all of which are similar, three edges are created.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a pipe', { 'pipe': 1 }),
		 		   Document('this is a different pipe', { 'pipe': 1 }),
				   Document('this is not a pipe, but a cigar', { 'pipe': 1, 'cigar': 1 }), ]
		for document in corpus:
			document.normalize()

		algo = DGS()
		graph = algo._to_graph(corpus)
		self.assertEqual(corpus, list(graph.nodes))
		self.assertEqual(3, len(list(graph.edges)))
		self.assertTrue((corpus[0], corpus[1]) in graph.edges)
		self.assertTrue((corpus[0], corpus[2]) in graph.edges)
		self.assertTrue((corpus[1], corpus[2]) in graph.edges)
		self.assertLess(graph.edges[(corpus[0], corpus[1])]['weight'], graph.edges[(corpus[0], corpus[2])]['weight'])
		self.assertLess(graph.edges[(corpus[1], corpus[0])]['weight'], graph.edges[(corpus[0], corpus[2])]['weight'])

	def test_create_graph_undirected_edges(self):
		"""
		Test that when creating a graph with similar documents, the edges are undirected.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a pipe', { 'pipe': 1 }),
		 		   Document('this is not a cigar', { 'cigar': 1 }),
				   Document('this is not a pipe, but a cigar', { 'pipe': 1, 'cigar': 1 }), ]
		for document in corpus:
			document.normalize()

		algo = DGS()
		graph = algo._to_graph(corpus)
		self.assertEqual(corpus, list(graph.nodes))
		self.assertEqual(2, len(list(graph.edges)))
		self.assertTrue(graph.edges[(corpus[0], corpus[2])])
		self.assertTrue(graph.edges[(corpus[2], corpus[0])])
		self.assertTrue(graph.edges[(corpus[1], corpus[2])])
		self.assertTrue(graph.edges[(corpus[2], corpus[1])])

	def test_create_graph_weight(self):
		"""
		Test that when creating a graph, the weight is the inverted similarity.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a pipe', { 'pipe': 1 }),
				   Document('this is a pipe', { 'pipe': 1 }), ]
		for document in corpus:
			document.normalize()

		algo = DGS()
		graph = algo._to_graph(corpus)
		self.assertEqual(corpus, list(graph.nodes))
		self.assertEqual(1, len(list(graph.edges)))
		self.assertEqual(0, graph.edges[(corpus[0], corpus[1])]['weight'])

	def test_create_graph_duplicate_document(self):
		"""
		Test that when creating a graph with two documents having the same text and attributes, they are created as separate nodes.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a pipe', { 'pipe': 1 }),
				   Document('this is not a pipe', { 'pipe': 1 }), ]
		for document in corpus:
			document.normalize()

		algo = DGS()
		graph = algo._to_graph(corpus)
		self.assertEqual(corpus, list(graph.nodes))
		self.assertEqual(2, len(list(graph.nodes)))

	def test_create_graph_documents_attributes(self):
		"""
		Test that when creating a graph, the documents are added as attributes.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a pipe', { 'pipe': 1 }),
				   Document('this is not a pipe', { 'pipe': 1 }), ]
		for document in corpus:
			document.normalize()

		algo = DGS()
		graph = algo._to_graph(corpus)
		self.assertEqual(corpus, list(graph.nodes))
		self.assertEqual(2, len(list(graph.nodes)))
		self.assertEqual(corpus[0], graph.nodes[corpus[0]]['document'])
		self.assertEqual(corpus[1], graph.nodes[corpus[1]]['document'])
