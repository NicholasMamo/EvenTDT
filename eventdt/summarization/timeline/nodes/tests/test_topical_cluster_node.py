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
from vsm.vector import Vector
from vsm.clustering import Cluster

class TestClusterNode(unittest.TestCase):
	"""
	Test the cluster node.
	"""

	def test_create_empty(self):
		"""
		Test that the cluster node is created empty.
		"""

		self.assertEqual([ ], TopicalClusterNode().clusters)
		self.assertEqual([ ], TopicalClusterNode().topics)

	def test_create_with_timestamp_zero(self):
		"""
		Test that the cluster node saves the timestamp correctly even if it is zero.
		"""

		self.assertEqual(0, TopicalClusterNode(0).created_at)

	def test_create_with_timestamp(self):
		"""
		Test that the cluster node saves the timestamp correctly.
		"""

		self.assertEqual(1000, TopicalClusterNode(1000).created_at)

	def test_create_default_timestamp(self):
		"""
		Test that the cluster node uses the current timestamp if it is not given.
		"""

		self.assertEqual(round(time.time()), round(TopicalClusterNode().created_at))

	def test_add(self):
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

	def test_add_repeated(self):
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

	def test_add_cluster_dynamic(self):
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

	def test_get_all_documents(self):
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
