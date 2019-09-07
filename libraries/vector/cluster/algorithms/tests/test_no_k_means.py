"""
Run unit tests on the No-K-Means algorithms
"""

import math
import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '../')
if path not in sys.path:
    sys.path.append(path)

from libraries.vector import vector_math
from libraries.vector.vector import Vector
from libraries.vector.nlp.document import Document
from libraries.vector.nlp.term_weighting import TF
from libraries.vector.cluster.algorithms.nokmeans import ClusterType, NoKMeans, TemporalNoKMeans

class TestNoKMeans(unittest.TestCase):
	"""
	Test the No-K-Means algorithms
	"""

	def test_no_k_means(self):
		"""
		Test the No-K-Means algorithm
		"""

		tf = TF()

		documents = [
			Document("", ["a", "b", "a", "c"], scheme=tf),
			Document("", ["a", "b", "a"], scheme=tf),
			Document("", ["x", "y", "z"], scheme=tf),
			Document("", ["x", "y"], scheme=tf),
			Document("", ["y", "z"], scheme=tf),
			Document("", ["a", "b"], scheme=tf),
			Document("", ["p", "q"], scheme=tf),
			Document("", ["q", "p"], scheme=tf),
			Document("", ["p"], scheme=tf),
		]

		for document in documents:
			document.normalize()

		algo = NoKMeans(similarity_measure=vector_math.cosine)
		algo.cluster(documents, 0.67, 2)
		frozen_clusters, active_clusters = algo.get_clusters(ClusterType.FROZEN), algo.get_clusters(ClusterType.ACTIVE)

		self.assertTrue(documents[0] in frozen_clusters[0].get_vectors())
		self.assertTrue(documents[1] in frozen_clusters[0].get_vectors())
		self.assertTrue(documents[2] in frozen_clusters[1].get_vectors())
		self.assertTrue(documents[3] in frozen_clusters[1].get_vectors())
		self.assertTrue(documents[4] in frozen_clusters[1].get_vectors())
		self.assertTrue(documents[5] in frozen_clusters[2].get_vectors())
		self.assertTrue(documents[6] in active_clusters[0].get_vectors())
		self.assertTrue(documents[7] in active_clusters[0].get_vectors())
		self.assertTrue(documents[8] in active_clusters[0].get_vectors())

		# it should be noted that the No-K-Means' implementation is intended for similarity measures, not distance measures
		algo = NoKMeans(similarity_measure=vector_math.manhattan)
		algo.cluster(documents, 0.4, 3)
		frozen_clusters, active_clusters = algo.get_clusters(ClusterType.FROZEN), algo.get_clusters(ClusterType.ACTIVE)

		self.assertTrue(documents[0] in frozen_clusters[0].get_vectors())
		self.assertTrue(documents[1] in frozen_clusters[0].get_vectors())
		self.assertTrue(documents[2] in frozen_clusters[1].get_vectors())
		self.assertTrue(documents[3] in frozen_clusters[2].get_vectors())
		self.assertTrue(documents[4] in frozen_clusters[3].get_vectors())
		self.assertTrue(documents[5] in active_clusters[0].get_vectors())
		self.assertTrue(documents[6] in active_clusters[1].get_vectors())
		self.assertTrue(documents[7] in active_clusters[1].get_vectors())
		self.assertTrue(documents[8] in active_clusters[2].get_vectors())

		"""
		Test the returned clusters.
		"""

		algo = NoKMeans(similarity_measure=vector_math.cosine)
		clusters = algo.cluster(documents, 0.4, 3)
		self.assertTrue(documents[5] in clusters[0].get_vectors())
		self.assertTrue(documents[6] in clusters[1].get_vectors())
		self.assertTrue(documents[7] in clusters[1].get_vectors())
		self.assertTrue(documents[8] in clusters[1].get_vectors())

		algo = NoKMeans(similarity_measure=vector_math.cosine)
		clusters = algo.cluster(documents[:7], 0.4, 3)
		clusters = algo.cluster(documents[7:], 0.4, 3)
		self.assertEqual(len(clusters), 1)
		self.assertTrue(documents[6] in clusters[0].get_vectors())
		self.assertTrue(documents[7] in clusters[0].get_vectors())
		self.assertTrue(documents[8] in clusters[0].get_vectors())

	def test_temporal_no_k_means(self):
		"""
		Test the temporal No-K-Means algorithm
		"""

		tf = TF()

		documents = [
			Document("", ["a", "b", "a", "c"], { "time": 0 }, scheme=tf),
			Document("", ["a", "b", "a"], { "time": 1 }, scheme=tf),
			Document("", ["x", "y", "z"], { "time": 2 }, scheme=tf),
			Document("", ["x", "y"], { "time": 2 }, scheme=tf),
			Document("", ["y", "z"], { "time": 6 }, scheme=tf),
			Document("", ["a", "b"], { "time": 7 }, scheme=tf),
			Document("", ["p", "q"], { "time": 3 }, scheme=tf),
			Document("", ["q", "p"], { "time": 4 }, scheme=tf),
			Document("", ["p"], { "time": 5 }, scheme=tf),
		]
		for document in documents:
			document.normalize()

		algo = TemporalNoKMeans(similarity_measure=vector_math.cosine)
		algo.cluster(documents, 0.67, 3, "time")
		frozen_clusters, active_clusters = algo.get_clusters(ClusterType.FROZEN), algo.get_clusters(ClusterType.ACTIVE)

		self.assertTrue(documents[0] in frozen_clusters[0].get_vectors())
		self.assertTrue(documents[1] in frozen_clusters[0].get_vectors())
		self.assertTrue(documents[2] in frozen_clusters[1].get_vectors())
		self.assertTrue(documents[3] in frozen_clusters[1].get_vectors())
		self.assertTrue(documents[4] in active_clusters[1].get_vectors())
		self.assertTrue(documents[5] in active_clusters[2].get_vectors())
		self.assertTrue(documents[6] in active_clusters[0].get_vectors())
		self.assertTrue(documents[7] in active_clusters[0].get_vectors())
		self.assertTrue(documents[8] in active_clusters[0].get_vectors())

		"""
		Test the returned clusters.
		"""

		algo = TemporalNoKMeans(similarity_measure=vector_math.cosine)
		clusters = algo.cluster(documents, 0.4, 3, "time")
		self.assertTrue(documents[4] in clusters[1].get_vectors())
		self.assertTrue(documents[6] in clusters[0].get_vectors())
		self.assertTrue(documents[7] in clusters[0].get_vectors())
		self.assertTrue(documents[8] in clusters[0].get_vectors())

		algo = TemporalNoKMeans(similarity_measure=vector_math.cosine)
		clusters = algo.cluster(documents[:4] + documents[7:], 0.4, 3, "time")
		clusters = algo.cluster([documents[i] for i in [4, 5]], 0.4, 3, "time")
		self.assertEqual(len(clusters), 2)
		self.assertTrue(documents[4] in clusters[0].get_vectors())
		self.assertTrue(documents[5] in clusters[1].get_vectors())
