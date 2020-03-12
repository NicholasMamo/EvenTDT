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

		self.assertEqual([ ], Timeline(ClusterNode).nodes)

	def test_create_node_type_cluster_node(self):
		"""
		Test that when creating a timeline with a cluster node, the node type is saved.
		"""

		self.assertEqual(ClusterNode, Timeline(ClusterNode).node_type)

	def test_create_node_type_document_node(self):
		"""
		Test that when creating a timeline with a document node, the node type is saved.
		"""

		self.assertEqual(DocumentNode, Timeline(DocumentNode).node_type)
