"""
The No-K-Means algorithm is an incremental clustering algorithm, described in research by `Azzopardi et al. in 2016 <https://www.researchgate.net/profile/Colin_Layfield/publication/303893387_Extended_No-K-Means_for_Search_Results_Clustering/links/575acd4208ae9a9c95518dfd.pdf>`_.
The algorithm compares incoming documents to existing clusters.
The vector is added to the most similar cluster if the similarity exceeds a certain threshold.
Otherwise, the vector is added to a new cluster.

Since clusters accumulate over time, the algorithm also has a freeze period.
Clusters that have not been updated with new vectors for an equivalent period are frozen.
No new vectors can be added to frozen clusters.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from .clustering import ClusteringAlgorithm
from cluster import Cluster

class NoKMeans(ClusteringAlgorithm):
	"""
	The No-K-Means algorithm is an incremental clustering algorithm.
	Incoming vectors are added to the most similar cluster if the similarity exceeds a threshold.
	Otherwise, a new cluster is created just for them.

	This class contains one additional field: the frozen clusters.
	Inactive clusters are frozen out, and are not checked with incoming vectors anymore.

	.. warning::

		By default, frozen clusters are not retained because they hog memory over time.

	:ivar frozen_clusters: A list of clusters that have been retired.
	:vartype frozen_clusters: list of :class:`~vsm.clustering.cluster.Cluster` instances
	:ivar threshold: The minimum similarity between a vector and a cluster's centroid.
					 If any cluster exceeds this threshold, the vector is added to that cluster.
	:vartype threshold: float
	:ivar freeze_period: The number of documents that arrive without being added to a cluster before it is frozen.
	:vartype freeze_period: int
	:ivar store_frozen: A boolean indicating whether frozen clusters should be retained.
	:vartype store_frozen: bool
	"""

	def __init__(self, threshold, freeze_period, store_frozen=False):
		"""
		Initialize the algorithm with the clusters.

		:param threshold: The minimum similarity between a vector and a cluster's centroid.
						  If any cluster exceeds this threshold, the vector is added to that cluster.
		:type threshold: float
		:param freeze_period: The number of documents that arrive without being added to a cluster before it is frozen.
		:type freeze_period: int
		:param store_frozen: A boolean indicating whether frozen clusters should be retained.
		:type store_frozen: bool
		"""

		super(NoKMeans, self).__init__()
		self.frozen_clusters = [ ]

	def cluster(self, vectors, *args, **kwargs):
		"""
		Cluster the given documents.

		:param vectors: The list of vectors to cluster.
		:type vectors: list of :class:`~vsm.vector.Vector` instances

		:return: The clusters that received documents, and which are not frozen.
		:rtpye: list of :class:`~vsm.clustering.cluster.Cluster` instances
		"""

		for index, vector in enumerate(vectors):
			"""
			Freeze inactive clusters first.
			In this way, nothing gets added to them, thereby resetting their age.
			"""
			i = 0
			while i < len(self.clusters):
				cluster = self.clusters[i]
				age = cluster.get_attribute("age") or 0
				cluster.set_attribute("age", age + 1) # increment the ages first
				if (age + 1 > freeze_period):
					self.clusters.remove(cluster)
					if store_frozen:
						self.frozen_clusters.append(cluster)
				else:
					i += 1

			"""
			Calculate the similarities between each vector and each cluster.
			The similarity is inverted if cosine similarity is not being used to get similarity instead of distance.
			"""
			similarities = [ cluster.similarity(vector, self._similarity_measure) for cluster in self.clusters ]
			similarities = [ 1 - s for s in similarities ] if self._similarity_measure != cosine else similarities

			"""
			If there are similar clusters, add the Vector to the most similar cluster.
			Otherwise, a new cluster is created for the new Vector.
			"""
			if (len([s for s in similarities if s >= threshold]) > 0):
				"""
				If there are similar clusters, first find the index of this Cluster.
				Then, add to this Cluster the Vector and reset its age.
				"""
				max_similarity = max(similarities) # get the best similarity
				best_match = similarities.index(max_similarity) # find the position of the Cluster with the minimum distance
				self.clusters[best_match].add_vector(vector)
				self.clusters[best_match].set_attribute("age", 0)
			else:
				"""
				If a new Cluster has to be created, add to it the Vector.
				At the same time, set its age to 0.
				"""
				cluster = Cluster()
				cluster.add_vector(vector)
				cluster.set_attribute("age", 0)
				self.clusters.append(cluster)

		# frozen clusters will have been dealt with already, so the check is skipped
		return [ cluster for cluster in self.clusters if cluster.get_attribute("age") <= len(vectors) ]

class TemporalNoKMeans(NoKMeans):
	"""
	The Temporal No-K-Means algorithm is an incremental clustering algorithm.
	In contrast with the normal No-K-Means, its freeze period is in seconds, not on the number of vectors seen so far.
	It is assumed that the vectors are provided in chronological order across function calls.
	Within function calls, vectors are sorted.
	"""

	def cluster(self, vectors, threshold, freeze_period, time_attribute, store_frozen=True):
		"""
		Cluster the given documents.

		:param vectors: The list of vectors to cluster.
		:type vectors: list of :class:`~vsm.vector.Vector` instances
		:param threshold: The minimum similarity for a vector to be added to a cluster.
		:type threshold: float
		:param freeze_period: The time (in seconds) of inactivity before a cluster is frozen.
		:type freeze_period: int
		:param time_attribute: The key that stores the vector's associated timestamp.
		:type time_attribute: :class:`~object`
		:param store_frozen: A boolean indicating whether frozen clusters should be retained.
			This should be turned off in long-running systems to avoid memory leaks.
		:type store_frozen: bool

		:return: The clusters that received documents, and which are not frozen.
		:rtpye: list of :class:`~vsm.clustering.cluster.Cluster` instances
		"""

		vectors = sorted(vectors, key=lambda x: x.get_attribute(time_attribute)) # sort the vectors in chronological order
		if len(vectors) > 0:
			earliest_vector = int(vectors[0].get_attribute(time_attribute))

			for index, vector in enumerate(vectors):
				"""
				Freeze inactive clusters first.
				In this way, nothing gets added to them, thereby resetting their age.
				"""
				time = int(vector.get_attribute(time_attribute)) # get the time of the current vector
				i = 0
				while i < len(self.clusters):
					cluster = self.clusters[i]
					age = time - (cluster.get_attribute("last_updated") or 0)
					if (age > freeze_period):
						self.clusters.remove(cluster)
						if store_frozen:
							self.frozen_clusters.append(cluster)
					else:
						i += 1

				"""
				Calculate the similarities between each vector and each cluster.
			The similarity is inverted if cosine similarity is not being used to get similarity instead of distance.
				"""
				similarities = [ cluster.similarity(vector, self._similarity_measure) for cluster in self.clusters ]
				similarities = [ 1 - s for s in similarities ] if self._similarity_measure != cosine else similarities

				"""
				If there are similar clusters, add the Vector to the most similar cluster.
				Otherwise, a new cluster is created for the new Vector.
				"""
				if (len([s for s in similarities if s >= threshold]) > 0):
					"""
					If there are similar clusters, first find the index of this Cluster.
					Then, add to this Cluster the Vector and reset its age.
					"""
					max_similarity = max(similarities) # get the best similarity
					best_match = similarities.index(max_similarity) # find the position of the Cluster with the minimum distance
					# print(vector.get_dimensions(), best_match, max_similarity)
					self.clusters[best_match].add_vector(vector)
					self.clusters[best_match].set_attribute("last_updated", time)
				else:
					"""
					If a new Cluster has to be created, add to it the Vector.
					At the same time, set its age to 0.
					"""
					cluster = Cluster()
					cluster.add_vector(vector)
					cluster.set_attribute("last_updated", time)
					self.clusters.append(cluster)

			# frozen clusters will have been dealt with already, so the check is skipped
			return [ cluster for cluster in self.clusters if cluster.get_attribute("last_updated") >= earliest_vector ]
		else:
			return []
