"""
A class for clustering algorithms.
The class is used to maintain state.
"""

from abc import ABC, abstractmethod

from ...vector import Vector
from ...vector_math import *
from ..cluster import Cluster

class ClusteringAlgorithm(ABC):
	"""
	The ClusteringAlgorithm class retains a state.

	:ivar _similarity_measure: The similarity function to use to compare the likeliness of the vector with the cluster.
	:vartype _similarity_measure: function
	:ivar _clusters: A list of clusters.
	:vartype _clusters: list of :class:`vector.cluster.cluster.Cluster` instances
	"""

	@abstractmethod
	def __init__(self, similarity_measure=cosine):
		"""
		The constructor is used to initialize the state.

		:param similarity_measure: The similarity function to use to compare the likeliness of the vector with the cluster.
		:type similarity_measure: function
		"""

		self._similarity_measure = similarity_measure
		self._clusters = []

		pass

	@abstractmethod
	def cluster(self, vectors):
		"""
		Cluster the given vectors.

		:param vectors: The list of vectors to cluster.
		:type vectors: list of :class:`vector.vector.Vector` instances

		:return: The clusters that received documents.
		:rtpye: list of :class:`vector.cluster.cluster.Cluster` instances
		"""

		pass

	def get_clusters(self):
		"""
		Get the list of clusters.

		:return: The stored list of clusters.
		:rtype: list of :class:`vector.cluster.cluster.Cluster` instances
		"""

		return self._clusters
