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

    def test_init_saves_graph(self):
        """
        Test that when initializing the algorithm, the graph is saved as an instance variable.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)
            self.assertTrue(algo.graph)

    def test_init_graph_is_graph(self):
        """
        Test that when constructing a graph, the function actually returns a graph.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)
            self.assertEqual(nx.Graph, type(algo.graph))

    def test_init_graph_undirected(self):
        """
        Test that when constructing a graph, the resulting graph is not directed.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)
            self.assertFalse(nx.is_directed(algo.graph))

    def test_init_graph_no_loops(self):
        """
        Test that when constructing a graph, the resulting graph has no loops.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file)
            terms = set(algo.similarity)
            self.assertTrue(not any( (term, term) in list(algo.graph.edges)
                            for term in terms ))

    def test_init_graph_filtered(self):
        """
        Test that when constructing a graph, the percentile is used to filter edges.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file, percentile=0.9)
            terms = set(algo.similarity)
            self.assertEqual((len(terms) * (len(terms) - 1))/20, # 1/10 (90th percentile) × 1/2 (remove duplicate edges)
                             len(algo.graph.edges))

    def test_cluster_float_clusters(self):
        """
        Test that when clustering terms with a floating number of clusters, the function raises a ValueError.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file, percentile=0.9)
            self.assertRaises(ValueError, algo.cluster, 0.1)

    def test_cluster_0_clusters(self):
        """
        Test that when clustering terms with 0 clusters, the function raises a ValueError.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file, percentile=0.9)
            self.assertRaises(ValueError, algo.cluster, 0)

    def test_cluster_n_1_clusters(self):
        """
        Test that when clustering terms with :math:`n+1` clusters, where :math:`n` is the number of terms, the function raises a ValueError.
        """

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file, percentile=0.9)
            terms = set(algo.similarity)
            self.assertRaises(ValueError, algo.cluster, len(terms) + 1)

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

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file, percentile=0.9)
            self.assertEqual(('D', 'W'), algo._most_central_edge(graph)) # ('D', 'W') connects A–D and W–Z

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

        path = os.path.join(os.path.dirname(__file__), '../../../tests/corpora/ate/correlations.json')
        with open(path) as file:
            algo = GNClustering(file, percentile=0.9)
            self.assertEqual(('C', 'X'), algo._most_central_edge(graph)) # ('C', 'X') has a lower weight than ('D', 'W')

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

    def test_filter_edges_percentile_below_0(self):
        """
        Test when filtering edges, a percentile below 0 raises a ValueError.
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
            self.assertRaises(ValueError, algo._filter_edges, edges, -1)

    def test_filter_edges_percentile_above_1(self):
        """
        Test when filtering edges, a percentile above 1 raises a ValueError.
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
            self.assertRaises(ValueError, algo._filter_edges, edges, 2)

    def test_filter_edges_percentile_0(self):
        """
        Test that when filtering edges with a percentile of 0, all edges are retained.
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
            _edges = algo._filter_edges(edges, 0)
            self.assertEqual(set(edges), set(_edges))

    def test_filter_edges_percentile_1(self):
        """
        Test that when filtering edges with a percentile of 1, no edges are retained.
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
            edges = algo._filter_edges(edges, 1)
            self.assertFalse(edges)

    def test_filter_edges_does_not_change_edges(self):
        """
        Test that when filtering edges, the original list of edges does not change.
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
            _edges = json.dumps(edges)
            algo._filter_edges(edges, 1)
            self.assertEqual([ tuple(edge) for edge in json.loads(_edges) ], edges)

    def test_filter_edges_uses_percentile(self):
        """
        Test that when filtering edges, the percentile is used to filter edges.
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

            # test using the median
            _edges = algo._filter_edges(edges, 0.5)
            self.assertEqual((len(terms) * (len(terms) - 1))/2., len(_edges))

            # test using a split that is not in the middle
            _edges = algo._filter_edges(edges, 0.9)
            self.assertEqual((len(terms) * (len(terms) - 1))/10., len(_edges))

    def test_filter_edges_highest_weighted_retained(self):
        """
        Test that when filtering edges, the highest-weighted edges are retained.
        The highest-weighted edges correspond to the most correlated terms.
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
            filtered = algo._filter_edges(edges, 0.9)

            # sort the edges in descending order of weight, and then check that the highest-rated
            edges = sorted(edges, key=lambda x: x[2], reverse=True)
            self.assertGreater(edges[0][2], edges[-1][2]) # ensure that the sorting is correct
            self.assertEqual(set(filtered), set(edges[:int(len(edges)/10.)])) # check that the top-weighted edges are retained
            self.assertTrue(all( edge[2] > max([weight for _, _, weight in edges[int(len(edges)/2.):]])
                                 for edge in filtered )) # check that the edge weights are greater than the ones that weren't chosen

    def test_filter_edges_sorted_edges(self):
        """
        Test that the filtered edges are returned sorted in descending order of weight.
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
            edges = algo._filter_edges(edges, 0.5)
            self.assertTrue(all( edges[i][2] >= edges[i+1][2] for i in range(len(edges) - 1) ))

    def test_filter_edges_duplicates(self):
        """
        Test that filtered edges still have duplicates (t1⇒t2 and t2⇒t1).
        This is how we know that the filtering is being done correctly.
        If t1⇒t2 is in the list, then t2⇒t1 should be too.
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
            edges = algo._filter_edges(edges, 0.5)
            self.assertTrue(all( any( _t1 == t2 and _t2 == t1 # test that the reciprocal exists
                                     for _t1, _t2, _ in edges )
                                for t1, t2, _ in edges ))

    def test_to_graph_retains_edges(self):
        """
        Test that when converting edges to a graph, the original edges are not changed.
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
            edges = algo._filter_edges(edges, 0.5)
            _edges = json.dumps(edges)
            algo._to_graph(terms, edges)
            self.assertEqual([ tuple(edge) for edge in json.loads(_edges) ], edges)

    def test_to_graph_returns_graph(self):
        """
        Test that when converting edges to a graph, the function actually returns a graph.
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
            edges = algo._filter_edges(edges, 0.5)
            graph = algo._to_graph(terms, edges)
            self.assertEqual(nx.Graph, type(graph))

    def test_to_graph_is_undirected(self):
        """
        Test that when converting edges to a graph, the graph is undirected.
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
            edges = algo._filter_edges(edges, 0.5)
            graph = algo._to_graph(terms, edges)
            self.assertFalse(graph.is_directed())

    def test_to_graph_is_weighted(self):
        """
        Test that when converting edges to a graph, the graph is weighted.
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
            edges = algo._filter_edges(edges, 0.5)
            graph = algo._to_graph(terms, edges)
            self.assertTrue(nx.is_weighted(graph))

    def test_to_graph_no_duplicate_edges(self):
        """
        Test that when converting edges to a graph, there are no duplicate edges.
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
            edges = algo._filter_edges(edges, 0.5)
            graph = algo._to_graph(terms, edges)
            self.assertEqual((len(terms) * (len(terms) - 1))/4, len(graph.edges))
            self.assertTrue(all( (( t1, t2 ) in list(graph.edges) and not ( t2, t1 ) in list(graph.edges)) or
                                 (not ( t1, t2 ) in list(graph.edges) and ( t2, t1 ) in list(graph.edges))
                                 for ( t1, t2, _ ) in edges ))

    def test_to_graph_all_terms(self):
        """
        Test that when converting edges to a graph, all terms are in it.
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
            edges = algo._filter_edges(edges, 0.95)
            graph = algo._to_graph(terms, edges)
            self.assertEqual(len(terms), len(graph.nodes))

    def test_to_graph_all_edges(self):
        """
        Test that when converting edges to a graph, the new graph includes all filtered edges.
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
            edges = algo._filter_edges(edges, 0.5)
            graph = algo._to_graph(terms, edges)
            self.assertTrue(all( ( t1, t2 ) in list(graph.edges) or ( t2, t1 ) in list(graph.edges)
                                 for ( t1, t2, _ ) in edges ))

    def test_to_graph_correct_weights(self):
        """
        Test that when converting edges to a graph, all edges have the correct weights.
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
            edges = algo._filter_edges(edges, 0.5)
            graph = algo._to_graph(terms, edges)
            self.assertTrue(all( graph.get_edge_data(t1, t2)['weight'] == weight
                                 for (t1, t2, weight) in edges ))
