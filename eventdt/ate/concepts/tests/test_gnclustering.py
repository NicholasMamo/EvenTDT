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

    def test_remove_loops_copy(self):
        """
        Test that when removing loops, a new dictionary is created.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']
            _correlations = json.dumps(correlations) # encode the correlations so they don't change

            # remove loops and ensure that the original dictionary has not changed
            algo._remove_loops(correlations)
            self.assertEqual(correlations, json.loads(_correlations))

    def test_remove_loops_no_loops(self):
        """
        Test that when removing loops, there really are no remaining loops.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']

            # remove the loops
            correlations = algo._remove_loops(correlations)
            self.assertTrue(not any( term in correlations[term] for term in correlations ))

    def test_remove_loops_all_other_terms(self):
        """
        Test that when removing loops, all term correlations are kept, except for loops.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']
            terms = correlations.keys()

            # remove the loops
            correlations = algo._remove_loops(correlations)
            self.assertTrue(all( set(correlations[t1].keys()) == { t2 for t2 in terms if t2 != t1  } for t1 in correlations ))
            self.assertTrue(not any( term in correlations[term] for term in correlations ))

    def test_remove_loops_same_outer_terms(self):
        """
        Test that when removing loops, the outer terms are not changed.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']
            terms = correlations.keys()

            # remove the loops
            correlations = algo._remove_loops(correlations)
            self.assertEqual(set(terms), set(correlations.keys()))

    def test_remove_loops_same_scores(self):
        """
        Test that when removing loops, the correlation scores do not change.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']

            # remove the loops
            filtered = algo._remove_loops(correlations)
            self.assertTrue(all( filtered[t1][t2] == correlations[t1][t2]
                                 for t1 in filtered.keys()
                                 for t2 in filtered[t1].keys() ))
