"""
Test the functionality of the Wikipedia extrapolator.
"""

import os
import random
import re
import string
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

import networkx as nx
from nltk.corpus import stopwords

from apd.extractors.local.entity_extractor import EntityExtractor
from apd.scorers.local.tf_scorer import TFScorer
from apd.filters.local.threshold_filter import ThresholdFilter
from apd.resolvers.external.wikipedia_search_resolver import WikipediaSearchResolver
from apd.extrapolators.external.wikipedia_extrapolator import WikipediaExtrapolator

from nlp.document import Document
from nlp.tokenizer import Tokenizer
from nlp.term_weighting.tf import TF

class TestWikipediaExtrapolator(unittest.TestCase):
	"""
	Test the implementation and results of the Wikipedia extrapolator.
	"""

	def test_edge_centrality(self):
		"""
		Test that the edge centrality correctly identifies the most central edge.
		"""

		nodes =  [ 'A', 'B', 'C', 'D', 'W', 'X', 'Y', 'Z' ]
		edges = { ('A', 'B', 0.1), ('A', 'C', 0.1), ('A', 'D', 0.1),
		 		  ('B', 'C', 0.1), ('B', 'D', 0.1), ('C', 'D', 0.1),

				  ('W', 'X', 0.1), ('W', 'Y', 0.1), ('W', 'Z', 0.1),
		  		  ('X', 'Y', 0.1), ('X', 'Z', 0.1), ('Y', 'Z', 0.1),

				  ('D', 'W', 0.1)
				}

		graph = nx.Graph()
		graph.add_nodes_from(nodes)
		graph.add_weighted_edges_from(edges)

		extrapolator = WikipediaExtrapolator([ ], TF())
		self.assertEqual(('D', 'W'), extrapolator._most_central_edge(graph))

	def test_edge_centrality_multiple(self):
		"""
		Test that the edge centrality correctly identifies the most central edge when there are two such edges.
		This edge should be the one with the lowest weight.
		"""

		nodes =  [ 'A', 'B', 'C', 'D', 'W', 'X', 'Y', 'Z' ]
		edges = { ('A', 'B', 0.1), ('A', 'C', 0.1), ('A', 'D', 0.1),
		 		  ('B', 'C', 0.1), ('B', 'D', 0.1), ('C', 'D', 0.1),

				  ('W', 'X', 0.1), ('W', 'Y', 0.1), ('W', 'Z', 0.1),
		  		  ('X', 'Y', 0.1), ('X', 'Z', 0.1), ('Y', 'Z', 0.1),

				  ('D', 'W', 0.1), ('C', 'X', 0.05),
				}

		graph = nx.Graph()
		graph.add_nodes_from(nodes)
		graph.add_weighted_edges_from(edges)

		extrapolator = WikipediaExtrapolator([ ], TF())
		self.assertEqual(('C', 'X'), extrapolator._most_central_edge(graph))
