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
from vsm.clustering.algorithms.temporal_no_k_means import TemporalNoKMeans

class TestNoKMeans(unittest.TestCase):
	"""
	Test the No-K-Means algorithms.
	"""

	def test_update_age_without_vector_time(self):
		"""
		Test that when updating the age of a cluster, a TypeError is raised when the last vector has no time attribute.
		"""

		cluster = Cluster(Document('', [ ]))
		algo = TemporalNoKMeans(0.5, 10)
		self.assertRaises(TypeError, algo._update_age, cluster, 0, 'time')

	def test_update_age_without_vector(self):
		"""
		Test that when updating the age of a cluster without vectors, a ValueError is raised.
		"""

		cluster = Cluster()
		algo = TemporalNoKMeans(0.5, 10)
		self.assertRaises(IndexError, algo._update_age, cluster, 0, 'time')

	def test_update_age(self):
		"""
		Test that when updating the age, the cluster attribute is updated.
		"""

		cluster = Cluster(Document('', [ ], attributes={ 'timestamp': 10 }))
		algo = TemporalNoKMeans(0.5, 10)
		cluster.set_attribute('age', 8)
		self.assertEqual(8, cluster.get_attribute('age'))
		algo._update_age(cluster, 23, 'timestamp')
		self.assertEqual(13, cluster.get_attribute('age'))

	def test_update_age_without_previous(self):
		"""
		Test that when updating the age, the cluster attribute is updated even if there is no previous value.
		"""

		cluster = Cluster(Document('', [ ], attributes={ 'timestamp': 10 }))
		algo = TemporalNoKMeans(0.5, 10)
		algo._update_age(cluster, 23, 'timestamp')
		self.assertEqual(13, cluster.get_attribute('age'))

	def test_update_age_most_recent_vector(self):
		"""
		Test that when updating the age of a cluster, the most recent vector is used.
		"""

		cluster = Cluster([ Document('', [ ], attributes={ 'timestamp': 10 }),
		 					Document('', [ ], attributes={ 'timestamp': 8 })])
		algo = TemporalNoKMeans(0.5, 10)
		algo._update_age(cluster, 23, 'timestamp')
		self.assertEqual(15, cluster.get_attribute('age'))
