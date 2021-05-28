"""
The :class:`~ate.concepts.gnclustering.GNClustering` algorithm is a graph-based term clustering algorithm based on the `Girvan-Newman algorithm <https://www.pnas.org/content/99/12/7821>`_.
This algorithm constructs a graph made up of terms, with the edges between them representing their correlations.

.. note::

    This algorithm uses the `networkx <https://networkx.org/>`_ package for Python to construct the graph.
"""

from . import TermClusteringAlgorithm

class GNClustering(TermClusteringAlgorithm):
    """
    The Girvan-Newman term clustering algorithm keeps in its state a graph that it constructs.
    Later, the term clusters can be extracted from this graph by calling the :func:`~ate.concepts.gnclustering.GNClustering.cluster` method.
    """

    def __init__(self, file):
        """
        Initialize the clustering algorithm by loading the term similarities from file.
        Afterwards, the function creates a term graph.

        :param file: The open file wrapper.
                     This function loads the term similarities from this file.
        :class file: :class:`_io.TextIOWrapper`
        """

        super(GNClustering).__init__(file)

    def cluster(self, *args, **kwargs):
        """
        Create lexical concepts by clustering the terms.
        This function returns sets of terms extracted using the Girvan-Newman algorithm.

        :return: A group of term clusters.
        :rtype: set of set
        """

        pass
