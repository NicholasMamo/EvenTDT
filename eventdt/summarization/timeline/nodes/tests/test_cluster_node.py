"""
Run unit tests on the cluster node.
"""

import math
import os
import sys
import time
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from summarization.timeline.nodes import ClusterNode
from vsm.clustering import Cluster

class TestClusterNode(unittest.TestCase):
	"""
	Test the cluster node.
	"""

	def test_create_empty(self):
		"""
		Test that the cluster node is created empty.
		"""

		self.assertEqual([ ], ClusterNode().clusters)

	def test_create_with_timestamp_zero(self):
		"""
		Test that the cluster node saves the timestamp correctly even if it is zero.
		"""

		self.assertEqual(0, ClusterNode(0).created_at)

	def test_create_with_timestamp(self):
		"""
		Test that the cluster node saves the timestamp correctly.
		"""

		self.assertEqual(1000, ClusterNode(1000).created_at)

	def test_create_default_timestamp(self):
		"""
		Test that the cluster node uses the current timestamp if it is not given.
		"""

		self.assertEqual(round(time.time()), round(ClusterNode().created_at))

	def test_add(self):
		"""
		Test adding a cluster to the node.
		"""

		node = ClusterNode()
		self.assertEqual([ ], node.clusters)
		cluster = Cluster()
		node.add(cluster)
		self.assertEqual([ cluster ], node.clusters)

	def test_add_repeated(self):
		"""
		Test adding clusters one at a time to the node.
		"""

		node = ClusterNode()
		self.assertEqual([ ], node.clusters)
		clusters = [ Cluster() for i in range(2)]
		node.add(clusters[0])
		self.assertEqual([ clusters[0] ], node.clusters)
		node.add(clusters[1])
		self.assertEqual(clusters, node.clusters)

	def test_add_cluster_dynamic(self):
		"""
		Test that when changing a cluster, the node's cluster also changes.
		"""

		node = ClusterNode()
		self.assertEqual([ ], node.clusters)
		cluster = Cluster()
		node.add(cluster)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual(cluster, node.clusters[0])
		self.assertEqual(cluster.vectors, node.clusters[0].vectors)
		document = Document('', { 'a': 1 })
		cluster.vectors.append(document)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual(cluster, node.clusters[0])
		self.assertEqual(cluster.vectors, node.clusters[0].vectors)
		self.assertEqual(document, node.clusters[0].vectors[0])

	def test_get_all_documents_empty(self):
		"""
		Test that when getting all documents from an empty node, an empty list is returned.
		"""

		node = ClusterNode()
		self.assertEqual([ ], node.get_all_documents())

	def test_get_all_documents(self):
		"""
		Test that when getting all documents, the cluster documents are returned.
		"""

		node = ClusterNode()
		clusters = [ Cluster(Document('', { })), Cluster(Document('', { })) ]
		self.assertEqual([ ], node.get_all_documents())
		node.add(clusters[0])
		self.assertEqual(clusters[0].vectors, node.get_all_documents())
		node.add(clusters[1])
		self.assertEqual(clusters[0].vectors + clusters[1].vectors, node.get_all_documents())

	def test_similarity_empty_node(self):
		"""
		Test that the similarity between a cluster and an empty cluster node, the similarity is 0.
		"""

		node = ClusterNode()
		self.assertEqual([ ], node.clusters)
		self.assertEqual(0, node.similarity(Cluster(Document('', { 'x': 1 }))))

	def test_similarity_empty_cluster(self):
		"""
		Test that the similarity between a node and an empty cluster, the similarity is 0.
		"""

		"""
		Create the test data.
		"""
		documents = [ Document('this is not a pipe', { 'pipe': 1 }),
		 			  Document('this is not a cigar', { 'cigar': 1 }) ]
		cluster = Cluster(documents)

		node = ClusterNode()
		node.add(cluster)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual(0, node.similarity(Cluster(Document('', { }))))

	def test_similarity(self):
		"""
		Test calculating the similarity between a node and a cluster.
		"""

		"""
		Create the test data.
		"""
		documents = [ Document('this is not a pipe', { 'pipe': 1 }),
		 			  Document('this is not a cigar', { 'cigar': 1 }) ]

		node = ClusterNode()
		cluster = Cluster(documents)
		node.add(cluster)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual(math.sqrt(2)/2., node.similarity(Cluster(Document('this is not a pipe', { 'pipe': 1 }))))

	def test_similarity_lower_bound(self):
		"""
		Test that the similarity lower-bound between a node and a cluster is 0.
		"""

		"""
		Create the test data.
		"""
		documents = [ Document('this is not a pipe', { 'pipe': 1 }),
		 			  Document('this is not a cigar', { 'cigar': 1 }) ]

		node = ClusterNode()
		cluster = Cluster(documents)
		node.add(cluster)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual(0, node.similarity(Cluster(Document('this is a picture of dorian gray', { 'picture': 1, 'dorian': 1, 'gray': 1 }))))

	def test_similarity_upper_bound(self):
		"""
		Test that the similarity upper-bound between a node and a cluster is 1.
		"""

		"""
		Create the test data.
		"""
		documents = [ Document('this is not a pipe', { 'pipe': 1 }),
		 			  Document('this is not a cigar', { 'cigar': 1 }) ]

		node = ClusterNode()
		cluster = Cluster(documents)
		node.add(cluster)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual(1, node.similarity(Cluster(Document('this is not a pipe and this is not a cigar', { 'cigar': 1, 'pipe': 1 }))))

	def test_similarity_max(self):
		"""
		Test that the returned similarity is the maximum between the cluster and the node's clusters.
		"""

		"""
		Create the test data.
		"""
		documents = [ Document('this is not a pipe', { 'pipe': 1 }),
		 			  Document('this is not a cigar', { 'cigar': 1 }) ]
		document = Document('this is a picture of dorian gray', { 'picture': 1, 'dorian': 1, 'gray': 1 })

		node = ClusterNode()
		cluster = Cluster(documents)
		node.add(cluster)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual(0, node.similarity(Cluster(document)))
		node.add(Cluster(document))
		self.assertEqual(1, round(node.similarity(Cluster(document), 10)))

		"""
		Reverse the procedure.
		"""

		node = ClusterNode()
		cluster = Cluster(document)
		node.add(cluster)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual(1, round(node.similarity(Cluster(document)), 10))
		node.add(Cluster(documents))
		self.assertEqual(1, round(node.similarity(Cluster(document)), 10))

	def test_expired_inclusive(self):
		"""
		Test that the expiry is inclusive.
		"""

		node = ClusterNode(created_at=1000)
		self.assertTrue(node.expired(10, 1010))

	def test_expired_far_timestamp(self):
		"""
		Test that a node is expired if the timestamp is sufficiently far.
		"""

		node = ClusterNode(created_at=1000)
		self.assertTrue(node.expired(10, 1011))

	def test_expired_close_timestamp(self):
		"""
		Test that a node is not expired if the timestamp is close.
		"""

		node = ClusterNode(created_at=1000)
		self.assertFalse(node.expired(10, 1001))

	def test_expired_past_timestamp(self):
		"""
		Test that a node is not expired if the timestamp is in the past.
		"""

		node = ClusterNode(created_at=1000)
		self.assertFalse(node.expired(10, 999))

	def test_expired_realtime(self):
		"""
		Test that when the timestamp is not given, the current timestamp is used.
		"""

		node = ClusterNode(created_at=time.time())
		self.assertFalse(node.expired(1))

	def test_expired_realtime_sleep(self):
		"""
		Test that when the timestamp is not given, the current timestamp is used.
		"""

		node = ClusterNode(created_at=time.time())
		time.sleep(1)
		self.assertTrue(node.expired(1))

	def test_expired_zero(self):
		"""
		Test that a node immediately expired if the expiry is 0.
		"""

		node = ClusterNode(created_at=1000)
		self.assertTrue(node.expired(0, 1000))

	def test_expired_negative(self):
		"""
		Test that a ValueError is raised when the expiry is negative.
		"""

		node = ClusterNode(created_at=1000)
		self.assertRaises(ValueError, node.expired, -1, 0)
