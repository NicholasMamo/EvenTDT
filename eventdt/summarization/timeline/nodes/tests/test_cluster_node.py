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
