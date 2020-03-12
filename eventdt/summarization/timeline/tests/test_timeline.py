"""
Run unit tests on the timeline.
"""

import math
import os
import sys
import time
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from summarization.timeline import Timeline
from summarization.timeline.nodes import ClusterNode, DocumentNode

class TestTimeline(unittest.TestCase):
	"""
	Test the timeline.
	"""

	def test_create_empty_timeline(self):
		"""
		Test that when creating an empty timeline, the list of nodes is empty.
		"""

		self.assertEqual([ ], Timeline(ClusterNode, 60, 0.5).nodes)

	def test_create_node_type_cluster_node(self):
		"""
		Test that when creating a timeline with a cluster node, the node type is saved.
		"""

		self.assertEqual(ClusterNode, Timeline(ClusterNode, 60, 0.5).node_type)

	def test_create_node_type_document_node(self):
		"""
		Test that when creating a timeline with a document node, the node type is saved.
		"""

		self.assertEqual(DocumentNode, Timeline(DocumentNode, 60, 0.5).node_type)

	def test_create_expiry(self):
		"""
		Test that when creating a timeline with the expiry, it is saved.
		"""

		self.assertEqual(60, Timeline(DocumentNode, 60, 0.5).expiry)

	def test_create_expiry_negative(self):
		"""
		Test that when the timeline is created with a negative expiry, a ValueError is raised.
		"""

		self.assertRaises(ValueError, Timeline, DocumentNode, -1, 0.5)

	def test_create_expiry_zero(self):
		"""
		Test that when the timeline is created with an expiry of zero, no ValueError is raised.
		"""

		self.assertTrue(Timeline(DocumentNode, 0, 0.5))

	def test_create_min_similarity(self):
		"""
		Test that when creating a timeline with the minimum similarity, it is saved.
		"""

		self.assertEqual(0.5, Timeline(DocumentNode, 60, 0.5).min_similarity)

	def test_create_document_node(self):
		"""
		Test that when creating a node, the node type is as given in the constructor.
		"""

		timeline = Timeline(DocumentNode, 60, 0.5)
		timeline._create()
		self.assertEqual(DocumentNode, type(timeline.nodes[0]))

	def test_create_cluster_node(self):
		"""
		Test that when creating a node, the node type is as given in the constructor.
		"""

		timeline = Timeline(ClusterNode, 60, 0.5)
		timeline._create()
		self.assertEqual(ClusterNode, type(timeline.nodes[0]))

	def test_create_node_created_at(self):
		"""
		Test that when the creation time is given, it is passed on to the node.
		"""

		timeline = Timeline(ClusterNode, 60, 0.5)
		timeline._create(created_at=1000)
		self.assertEqual(1000, timeline.nodes[0].created_at)

	def test_create_node_created_at_none(self):
		"""
		Test that when the creation time is not given, the time is real-time.
		"""

		timeline = Timeline(ClusterNode, 60, 0.5)
		timeline._create()
		self.assertEqual(round(time.time()), round(timeline.nodes[0].created_at))
