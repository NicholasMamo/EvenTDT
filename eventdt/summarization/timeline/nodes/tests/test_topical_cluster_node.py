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
from summarization.timeline.nodes import TopicalClusterNode
from vsm import vector_math
from vsm.vector import Vector
from vsm.clustering import Cluster

class TestClusterNode(unittest.TestCase):
	"""
	Test the cluster node.
	"""

	def no_test_create_empty(self):
		"""
		Test that the cluster node is created empty.
		"""

		self.assertEqual([ ], TopicalClusterNode().clusters)
		self.assertEqual([ ], TopicalClusterNode().topics)

	def no_test_create_with_timestamp_zero(self):
		"""
		Test that the cluster node saves the timestamp correctly even if it is zero.
		"""

		self.assertEqual(0, TopicalClusterNode(0).created_at)

	def no_test_create_with_timestamp(self):
		"""
		Test that the cluster node saves the timestamp correctly.
		"""

		self.assertEqual(1000, TopicalClusterNode(1000).created_at)

	def no_test_create_default_timestamp(self):
		"""
		Test that the cluster node uses the current timestamp if it is not given.
		"""

		self.assertEqual(round(time.time()), round(TopicalClusterNode().created_at))

	def no_test_add(self):
		"""
		Test adding a cluster to the node.
		"""

		node = TopicalClusterNode()
		self.assertEqual([ ], node.clusters)
		self.assertEqual([ ], node.topics)
		cluster = Cluster()
		topic = Vector()
		node.add(cluster, topic)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual([ topic ], node.topics)

	def no_test_add_repeated(self):
		"""
		Test adding clusters one at a time to the node.
		"""

		node = TopicalClusterNode()
		self.assertEqual([ ], node.clusters)
		clusters = [ Cluster() for i in range(2)]
		topics = [ Vector() for i in range(2)]
		node.add(clusters[0], topics[0])
		self.assertEqual([ clusters[0] ], node.clusters)
		self.assertEqual([ topics[0] ], node.topics)
		node.add(clusters[1], topics[1])
		self.assertEqual(clusters, node.clusters)
		self.assertEqual(topics, node.topics)

	def no_test_add_cluster_dynamic(self):
		"""
		Test that when changing a topic, the node's topic also changes.
		"""

		node = TopicalClusterNode()
		self.assertEqual([ ], node.topics)
		topic = Vector()
		node.add(Cluster(), topic)
		self.assertEqual(topic, node.topics[0])
		self.assertEqual({ }, node.topics[0].dimensions)

		topic.dimensions['a'] = 1
		self.assertEqual({ 'a': 1 }, node.topics[0].dimensions)
		self.assertEqual(topic, node.topics[0])

	def no_test_get_all_documents(self):
		"""
		Test that when getting all documents, the cluster documents are returned.
		"""

		node = TopicalClusterNode()
		clusters = [ Cluster(Document('', { })), Cluster(Document('', { })) ]
		self.assertEqual([ ], node.get_all_documents())
		node.add(clusters[0], Vector())
		self.assertEqual(clusters[0].vectors, node.get_all_documents())
		node.add(clusters[1], Vector())
		self.assertEqual(clusters[0].vectors + clusters[1].vectors, node.get_all_documents())

	def test_similarity_empty_node(self):
		"""
		Test that the similarity between a cluster and an empty cluster node, the similarity is 0.
		"""

		node = TopicalClusterNode()
		self.assertEqual([ ], node.clusters)
		self.assertEqual(0, node.similarity(Cluster(Document('', { 'x': 1 })), Vector()))

	def test_similarity_empty_cluster(self):
		"""
		Test that the similarity between a node and an empty topic, the similarity is 0.
		"""

		"""
		Create the test data.
		"""
		documents = [ Document('this is not a pipe', { 'pipe': 1 }),
		 			  Document('this is not a cigar', { 'cigar': 1 }) ]
		cluster = Cluster(documents)

		node = TopicalClusterNode()
		node.add(cluster, cluster.centroid)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual([ cluster.centroid ], node.topics)
		self.assertEqual(0, node.similarity(Cluster(), Vector()))

	def test_similarity(self):
		"""
		Test calculating the similarity between a node and a topic.
		"""

		"""
		Create the test data.
		"""
		documents = [ Document('this is not a pipe', { 'pipe': 1 }),
		 			  Document('this is not a cigar', { 'cigar': 1 }) ]

		node = TopicalClusterNode()
		cluster = Cluster(documents)
		node.add(cluster, cluster.centroid)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual(math.sqrt(2)/2., node.similarity(Cluster(), Vector({ 'pipe': 1 })))

	def test_similarity_lower_bound(self):
		"""
		Test that the similarity lower-bound between a node and a cluster is 0.
		"""

		"""
		Create the test data.
		"""
		documents = [ Document('this is not a pipe', { 'pipe': 1 }),
		 			  Document('this is not a cigar', { 'cigar': 1 }) ]

		node = TopicalClusterNode()
		cluster = Cluster(documents)
		node.add(cluster, cluster.centroid)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual(0, node.similarity(Cluster(), Vector({ 'picture': 1 })))

	def test_similarity_upper_bound(self):
		"""
		Test that the similarity upper-bound between a node and a cluster is 1.
		"""

		"""
		Create the test data.
		"""
		documents = [ Document('this is not a pipe', { 'pipe': 1 }),
		 			  Document('this is not a cigar', { 'cigar': 1 }) ]

		node = TopicalClusterNode()
		cluster = Cluster(documents)
		node.add(cluster, cluster.centroid)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual(1, node.similarity(Cluster(), vector_math.normalize(Vector({ 'cigar': 1, 'pipe': 1 }))))

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

		node = TopicalClusterNode()
		cluster = Cluster(documents)
		node.add(cluster, cluster.centroid)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual(0, node.similarity(Cluster(document), Cluster(document).centroid))
		node.add(Cluster(document), Cluster(document).centroid)
		self.assertEqual(1, round(node.similarity(Cluster(document), Cluster(document).centroid), 10))

		"""
		Reverse the procedure.
		"""

		node = TopicalClusterNode()
		cluster = Cluster(document)
		node.add(cluster, cluster.centroid)
		self.assertEqual([ cluster ], node.clusters)
		self.assertEqual(1, round(node.similarity(Cluster(document), Cluster(document).centroid), 10))
		node.add(Cluster(documents), Cluster(documents).centroid)
		self.assertEqual(1, round(node.similarity(Cluster(document), Cluster(document).centroid), 10))

	def test_similarity_with_node_topic(self):
		"""
		Test that similarity is computed with the node's topic, not the cluster.
		"""

		"""
		Create the test data.
		"""
		document = Document('this is a pipe and this is a cigar', { 'cigar': 1, 'pipe': 1 })

		node = TopicalClusterNode()
		cluster = Cluster(document)
		node.add(cluster, Vector({ 'pipe': 1 }))

		self.assertEqual(1, node.similarity(Document('this is a pipe', { 'pipe': 1 }), Vector({ 'pipe': 1 })))
		self.assertEqual(0, node.similarity(Document('this is a cigar', { 'cigar': 1 }), Vector({ 'cigar': 1 })))

	def test_similarity_with_topic(self):
		"""
		Test that similarity is computed with the given topic, not the given cluster.
		"""

		"""
		Create the test data.
		"""
		document = Document('this is a pipe and this is a cigar', { 'cigar': 1, 'pipe': 1 })

		node = TopicalClusterNode()
		cluster = Cluster(document)
		node.add(cluster, Vector({ 'pipe': 1 }))

		self.assertEqual(1, node.similarity(Document('this is a cigar', { 'cigar': 1 }), Vector({ 'pipe': 1 })))
		self.assertEqual(0, node.similarity(Document('this is a pipe', { 'pipe': 1 }), Vector({ 'cigar': 1 })))
