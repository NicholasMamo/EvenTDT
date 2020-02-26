"""
Run unit tests on the No-K-Means algorithms.
"""

import math
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from vsm.clustering.cluster import Cluster
from vsm.clustering.algorithms.no_k_means import NoKMeans, TemporalNoKMeans

class TestNoKMeans(unittest.TestCase):
	"""
	Test the No-K-Means algorithms.
	"""

	def test_increment_age(self):
		"""
		Test that when incrementing the age, the cluster attribute is updated.
		"""

		cluster = Cluster()
		algo = NoKMeans(0.5, 10)
		cluster.set_attribute('age', 10)
		self.assertEqual(10, cluster.get_attribute('age'))
		algo._increment_age(cluster, 1)
		self.assertEqual(11, cluster.get_attribute('age'))

	def test_increment_age_without_previous(self):
		"""
		Test that when incrementing the age, the cluster attribute is updated even if there is no previous value.
		"""

		cluster = Cluster()
		algo = NoKMeans(0.5, 10)
		self.assertFalse(cluster.get_attribute('age'))
		algo._increment_age(cluster, 1)
		self.assertEqual(1, cluster.get_attribute('age'))

	def test_increment_age_parameter(self):
		"""
		Test that when incrementing the age with a custom parameter, the cluster attribute is updated accordingly.
		"""

		cluster = Cluster()
		algo = NoKMeans(0.5, 10)
		cluster.set_attribute('age', 10)
		self.assertEqual(10, cluster.get_attribute('age'))
		algo._increment_age(cluster, 12)
		self.assertEqual(22, cluster.get_attribute('age'))

	def test_to_freeze_low_age(self):
		"""
		Test that when the cluster's age is lower than the freeze period, the cluster is not marked as to be frozen.
		"""

		cluster = Cluster()
		algo = NoKMeans(0.5, 10)
		cluster.set_attribute('age', 9)
		self.assertFalse(algo._to_freeze(cluster))

	def test_to_freeze_same_age(self):
		"""
		Test that when the cluster's age is equivalent to the freeze period, it is marked to be frozen.
		"""

		cluster = Cluster()
		algo = NoKMeans(0.5, 10)
		cluster.set_attribute('age', 10)
		self.assertTrue(algo._to_freeze(cluster))

	def test_to_freeze_high_age(self):
		"""
		Test that when the cluster's age is higher than the freeze period, it is marked to be frozen.
		"""

		cluster = Cluster()
		algo = NoKMeans(0.5, 10)
		cluster.set_attribute('age', 11)
		self.assertTrue(algo._to_freeze(cluster))

	# def test_no_k_means(self):
	# 	"""
	# 	Test the No-K-Means algorithm
	# 	"""
	#
	# 	tf = TF()
	#
	# 	documents = [
	# 		Document("", ["a", "b", "a", "c"], scheme=tf),
	# 		Document("", ["a", "b", "a"], scheme=tf),
	# 		Document("", ["x", "y", "z"], scheme=tf),
	# 		Document("", ["x", "y"], scheme=tf),
	# 		Document("", ["y", "z"], scheme=tf),
	# 		Document("", ["a", "b"], scheme=tf),
	# 		Document("", ["p", "q"], scheme=tf),
	# 		Document("", ["q", "p"], scheme=tf),
	# 		Document("", ["p"], scheme=tf),
	# 	]
	#
	# 	for document in documents:
	# 		document.normalize()
	#
	# 	algo = NoKMeans(similarity_measure=vector_math.cosine)
	# 	clusters = algo.cluster(documents, 0.67, 2)
