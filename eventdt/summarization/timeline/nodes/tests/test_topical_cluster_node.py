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
