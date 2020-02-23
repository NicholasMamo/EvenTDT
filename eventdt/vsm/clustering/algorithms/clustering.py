"""
Clusters are normally the product of clustering algorithms
A clustering algorithm takes in vectors or documents and clusters them.

Clustering algorithms are represented as classes so that they maintain their state.
Each class stores, at least, a list of :class:`~vsm.clustering.cluster.Cluster` instances.
New documents can be clustered by calling the :func:`~vsm.clustering.algorithms.clustering.ClusteringAlgorithm.cluster` method.
"""

from abc import ABC, abstractmethod

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

class ClusteringAlgorithm(ABC):
	"""
	Clustering algorithms maintain a state.
	The state is, at least, a list of :class:`~vsm.clustering.cluster.Cluster` instances.

	:ivar clusters: A list of clusters.
	:vartype clusters: list of :class:`~vsm.clustering.cluster.Cluster`
	"""

	@abstractmethod
	def __init__(self):
		"""
		Initialize the state of the clustering algorithm with an empty list of clusters.
		"""

		self.clusters = [ ]

	@abstractmethod
	def cluster(self, vectors, *args, **kwargs):
		"""
		Cluster the given vectors.
		The function returns the active clusters.

		:param vectors: The vectors to cluster.
		:type vectors: list of :class:`~vsm.vector.Vector`

		:return: The clusters in the algorithm state.
		:rtpye: list of :class:`~vsm.clustering.cluster.Cluster`
		"""

		pass
