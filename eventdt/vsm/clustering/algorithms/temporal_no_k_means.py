"""
The temporal No-K-Means is a variant of the No-K-Means.
Differently from the No-K-Means, clusters are frozen if they have been inactive for a long period of time.
In the No-K-Means, the freeze period is based on the number of received vectors.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from .no_k_means import NoKMeans
from cluster import Cluster

class TemporalNoKMeans(NoKMeans):
	"""
	The temporal No-K-Means is a variant of the No-K-Means.
	Differently from the No-K-Means, clusters are frozen if they have been inactive for a long period of time.
	In the No-K-Means, the freeze period is based on the number of received vectors.
	"""

	def __init__(self, threshold, freeze_period, store_frozen=False):
		"""
		Initialize the algorithm with the clusters.

		:param threshold: The minimum similarity between a vector and a cluster's centroid.
						  If any cluster exceeds this threshold, the vector is added to that cluster.
		:type threshold: float
		:param freeze_period: The number of seconds of inactivity of a cluster before it is frozen.
		:type freeze_period: int
		:param store_frozen: A boolean indicating whether frozen clusters should be retained.
		:type store_frozen: bool
		"""

		super(NoKMeans, self).__init__(threshold, freeze_period, store_frozen)

	def cluster(self, vectors, time="timestamp", *args, **kwargs):
		"""
		Cluster the given vectors.
		Any additional arguments and keyword arguments are passed on to the :func:`~vsm.cluster.cluster.Cluster.similarity` function.

		:param vectors: The list of vectors to cluster.
		:type vectors: list of :class:`~vsm.vector.Vector`
		:param time: The name of the vector attribute used as weight.
		:type time: str

		:return: The clusters that received vectors, and which are not frozen.
		:rtpye: list of :class:`~vsm.clustering.cluster.Cluster` instances
		"""

		updated_clusters = [ ]

		vectors = sorted(vectors, key=lambda vector: vector.get_attribute(time))
		for vector in vectors:
			timestamp = vector.get_attribute(time)

			"""
			Freeze inactive clusters first.
			In this way, nothing gets added to them, thereby resetting their age.
			"""
			for cluster in self.clusters:
				self._update_age(cluster)
				if self._to_freeze(cluster, time, timetamp):
					self._freeze(cluster)

			"""
			If there are active clusters, get the closest cluster.
			If the vector's similarity with the cluster exceeds the threshold, add the vector to the cluster.
			The cluster's age is resetted.
			"""
			if self.clusters:
				cluster, similarity = self._closest_cluster(vector, *args, **kwargs)
				if similarity >= self.threshold:
					cluster.add_vector(vector)
					self._reset_age(cluster)
					updated_clusters.append(cluster)
					continue

			"""
			If there was no similar cluster, create a new cluster with just that vector.
			"""
			cluster = Cluster([ vector ])
			self.clusters.append(cluster)
			updated_clusters.append(cluster)

		return list(set(updated_clusters))
