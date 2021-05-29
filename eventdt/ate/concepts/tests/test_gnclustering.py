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

    def test_normalize_edges_copy(self):
        """
        Test that when normalizing edges, a new dictionary is created.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']

            # normalize the edges and ensure that the original dictionary has not changed
            filtered = algo._remove_loops(correlations)
            _filtered = json.dumps(filtered) # encode the correlations so they don't change
            normalized = algo._normalize_edges(filtered)
            self.assertEqual(filtered, json.loads(_filtered))

    def test_normalize_edges_sum_one(self):
        """
        Test that when normalizing edges, the sums of the weights are 1.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']

            # normalize the edges
            filtered = algo._remove_loops(correlations)
            normalized = algo._normalize_edges(filtered)
            self.assertTrue(all( 1 == round(sum(normalized[term].values()), 10) for term in normalized ))

    def test_normalize_edges_max(self):
        """
        Test that when normalizing edges, the maximum probability for each term gets the maximum normalized weight.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']

            # normalize the edges
            filtered = algo._remove_loops(correlations)
            top_correlations = { term: max(filtered[term], key=filtered[term].get) for term in filtered }
            normalized = algo._normalize_edges(filtered)
            self.assertTrue(all( top_correlations[term] == max(normalized[term], key=normalized[term].get)
                                 for term in normalized ))

    def test_normalize_edges_same_outer_terms(self):
        """
        Test that when normalizing edges, all outer-level terms are retained.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']
            terms = set(correlations)

            # normalize the edges
            filtered = algo._remove_loops(correlations)
            normalized = algo._normalize_edges(filtered)
            self.assertEqual(terms, set(normalized))

    def test_normalize_edges_same_inner_terms(self):
        """
        Test that when normalizing edges, all inner-level terms are retained.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']
            terms = set(correlations)

            # normalize the edges
            filtered = algo._remove_loops(correlations)
            normalized = algo._normalize_edges(filtered)
            self.assertTrue(all( set(normalized[t1]) == { t2 for t2 in terms if t2 != t1 } for t1 in normalized ))

    def test_to_edges_retains_correlations(self):
        """
        Test that when converting correlations to edges, the correlations are unchanged.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']

            # create the edges and ensure that the original dictionary has not changed
            filtered = algo._remove_loops(correlations)
            normalized = algo._normalize_edges(filtered)
            _normalized = json.dumps(normalized) # encode the normalized correlations so they don't change
            edges = algo._to_edges(normalized)
            self.assertEqual(json.loads(_normalized), normalized)

    def test_to_edges_all_edges(self):
        """
        Test that when converting correlations to edges, all edges are returned.
        This includes duplicate edges (:math:`t1⇒t2` and :math:`t2⇒t1`).
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']
            terms = set(correlations)

            filtered = algo._remove_loops(correlations)
            normalized = algo._normalize_edges(filtered)
            edges = algo._to_edges(normalized)

            # check that there are mirrored edges by re-constructing the edges
            reconstructed = { t1: { t2: weight
                                    for _t1, t2, weight in edges
                                    if _t1 == t1 }
                              for t1 in terms }
            self.assertEqual(len(terms) * (len(terms) - 1), len(edges))
            self.assertTrue(all( t1 in reconstructed for t1 in terms ))
            self.assertTrue(all( t2 in reconstructed[t1]
                                 for t1 in terms
                                 for t2 in terms
                                 if t1 != t2 ))

    def test_to_edges_average_weight(self):
        """
        Test that when converting correlations to edges, the weights are averaged.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']

            filtered = algo._remove_loops(correlations)
            normalized = algo._normalize_edges(filtered)
            edges = algo._to_edges(normalized)

            self.assertTrue(all( weight == (normalized[t1][t2] + normalized[t2][t1]) / 2.
                                for t1, t2, weight in edges ))

    def test_to_edges_mirrored_weights(self):
        """
        Test that when converting correlations to edges, the weights between :math:`t1⇒t2` and :math:`t2⇒t1` are the same.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)

            # load the terms 'manually'
            file.seek(0)
            correlations = json.loads(file.readline())['correlations']
            terms = set(correlations)

            filtered = algo._remove_loops(correlations)
            normalized = algo._normalize_edges(filtered)
            edges = algo._to_edges(normalized)

            # check that there are mirrored edges by re-constructing the edges
            reconstructed = { t1: { t2: weight
                                    for _t1, t2, weight in edges
                                    if _t1 == t1 }
                              for t1 in terms }
            self.assertTrue(all( reconstructed[t1][t2] == reconstructed[t2][t1]
                                 for t1 in terms
                                 for t2 in terms
                                 if t1 != t2 ))
