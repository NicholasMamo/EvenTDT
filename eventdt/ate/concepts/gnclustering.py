"""
The :class:`~ate.concepts.gnclustering.GNClustering` algorithm is a graph-based term clustering algorithm based on the `Girvan-Newman algorithm <https://www.pnas.org/content/99/12/7821>`_.
This algorithm constructs a graph made up of terms, with the edges between them representing their correlations.

.. note::

    This algorithm uses the `networkx <https://networkx.org/>`_ package for Python to construct the graph.
"""

import networkx as nx
from networkx.algorithms.centrality import edge_betweenness_centrality

from . import TermClusteringAlgorithm

class GNClustering(TermClusteringAlgorithm):
    """
    The Girvan-Newman term clustering algorithm keeps in its state a graph that it constructs.
    Later, the term clusters can be extracted from this graph by calling the :func:`~ate.concepts.gnclustering.GNClustering.cluster` method.

    :ivar graph: The term graph, constructed from the term correlations.
                 The nodes are the terms, and edges between them are weighted based on correlations.
    :vartype graph: :class:`nx.Graph`
    """

    def __init__(self, file, percentile=0.95, *args, **kwargs):
        """
        Initialize the clustering algorithm by loading the term similarities from file.
        Afterwards, the function creates a term graph.

        :param file: The open file wrapper.
                     This function loads the term similarities from this file.
        :class file: :class:`_io.TextIOWrapper`
        :param percentile: The percentile of edges to keep when constructing the graph.
                           The percentile must be between 0 and 1.
                           A percentile of 0.95% means that only edges that have a higher correlation than 95% of the rest are retained.
        :type percentile: float
        """

        super(GNClustering, self).__init__(file)
        self.graph = self._construct_graph(percentile)

    def cluster(self, n, *args, **kwargs):
        """
        Create lexical concepts by clustering the terms.
        This function returns sets of terms extracted using the Girvan-Newman algorithm.

        :param n: The number of clusters to return.
        :type n: int

        :return: A group of term clusters.
        :rtype: set of set

        :raises ValueError: When the number of clusters is not an integer.
        :raises ValueError: When the number of clusters is not between 1 and the order of the graph.
        """

        if not type(n) is int:
            raise ValueError(f"The number of clusters should be an integer, received { type(n) }")

        if not 1 <= n <= self.graph.order():
            raise ValueError(f"The number of clusters should be between 1 and the number of terms ({ self.graph.order() }), received { n }")

        return set( set( ) )

    def _most_central_edge(self, graph):
        """
        Find the most central edge in the given graph.
        The algorithm uses NetworkX's betweenness centrality, but it is based on weight.
        The lower the weight, the more shortest paths could go through it.

        In the term graph, the lower the weight, the less correlated two terms are.
        Therefore this function breaks links between terms that are not closely-correlated.

        :param graph: The graph on which the algorithm operates.
        :type graph: :class:`~networkx.Graph`

        :return: The most central edge, made up of the source and edge nodes.
        :rtype: tuple
        """

        centrality = edge_betweenness_centrality(graph, weight='weight')
        edge = max(centrality, key=centrality.get)
        return edge

    def _construct_graph(self, percentile):
        """
        Construct the term graph.

        :param percentile: The percentile of edges to retain.
                           The percentile must be between 0 and 1.
        :type percentile: float

        :return: The term graph, constructed from the term correlations.
                 The nodes are the terms, and edges between them are weighted based on correlations.
        :rtype: :class:`networkx.Graph`
        """

        correlations = self._remove_loops(self.similarity)
        correlations = self._normalize_edges(correlations)
        edges = self._to_edges(correlations)
        edges = self._filter_edges(edges, percentile)
        return self._to_graph(list(correlations.keys()), edges)

    def _remove_loops(self, correlations):
        """
        Remove edges between a term and itself, loops.

        :param: A correlation dictionary.
                The outer level is each term, and the inner level is the term's correlation with the other terms.
        :type: dict of dict

        :return: A correlation dictionary without loops.
        :rtype: dict of dict
        """

        return { t1: { t2: weight
                       for t2, weight in correlations[t1].items()
                       if t1 != t2 }
                 for t1 in correlations }

    def _normalize_edges(self, correlations):
        """
        Normalize the correlations as probabilities.
        For each edge, the sum of the correlations add up to 1.
        Higher values indicate that two terms are closely correlated.

        :param: A correlation dictionary.
                The outer level is each term, and the inner level is the term's correlation with the other terms.
        :type: dict of dict

        :return: A correlation dictionary with normalized edges.
        :rtype: dict of dict
        """

        return { t1: { t2: weight / sum(correlations[t1].values())
                       for t2, weight in correlations[t1].items() }
                 for t1 in correlations }

    def _to_edges(self, correlations):
        """
        Convert the correlations to weighted edges.
        The weight is the average correlation between the two terms.

        :param: A correlation dictionary.
                The outer level is each term, and the inner level is the term's correlation with the other terms.
        :type: dict of dict

        :return: A list of tuples, each one representing an edge.
                 Edge tuples include the source term, the target term, and a weight.
        :rtype: list of tuple
        """

        return [ (t1, t2, (correlations[t1][t2] + correlations[t2][t1]) / 2.)
                 for t1 in correlations
                 for t2 in correlations[t1] ]

    def _filter_edges(self, edges, percentile):
        """
        Convert the correlations to weighted edges.

        :param edges: A list of tuples, each one representing an edge.
                      Edge tuples include the source term, the target term, and a weight.
        :type edges: list of tuple
        :param percentile: The percentile of edges to retain.
                           The percentile must be between 0 and 1.
        :type percentile: float

        :return: A list of tuples, each one representing an edge.
                 Edge tuples include the source term, the target term, and a
        :rtype: list of tuple

        :raises ValueError: When the percentile is not between 0 and 1.
        """

        if not 0 <= percentile <= 1:
            raise ValueError(f"The edge percentile must be between 0 and 1, received { percentile }")

        edges = sorted(edges, key=lambda x: x[2], reverse=True) # sort the edges in descending order of weight
        keep = round((1 - percentile) * len(edges)) # get the number of edges to keep
        return edges[:keep]

    def _to_graph(self, nodes, edges):
        """
        Convert the given edges to a graph.

        :param nodes: The nodes, or terms, in the graph.
                      These are given separately from the edges so that isolated nodes, which have no edes, are still in the graph.
        :type nodes: list of str or tuple of str or set of str
        :param edges: A list of tuples, each one representing an edge.
                      Edge tuples include the source term, the target term, and a
        :type edges: list of tuple

        :return: An undirected term graph.
                 The nodes are the terms, and edges between them are weighted based on correlations.
        :rtype: :class:`networkx.Graph`
        """

        G = nx.Graph()
        G.add_nodes_from(nodes) # so that isolated nodes are still added
        G.add_weighted_edges_from(edges)
        return G
