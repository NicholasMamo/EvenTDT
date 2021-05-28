"""
Test the functionality of the :class:`~ate.concepts.gnclustering.GNClustering` class.
"""

import json
import os
import sys
import unittest

import networkx as nx

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate.concepts import GNClustering

class TestGNClustering(unittest.TestCase):
    """
    Test the functionality of the :class:`~ate.concepts.gnclustering.GNClustering` class.
    """

    def test_construct_graph_returns_graph(self):
        """
        Test that when constructing a graph, the function actually returns a graph.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)
            self.assertEqual(nx.Graph, type(algo.graph))

    def test_construct_graph_not_directed(self):
        """
        Test that when constructing a graph, the resulting graph is not directed.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)
            self.assertFalse(nx.is_directed(algo.graph))
