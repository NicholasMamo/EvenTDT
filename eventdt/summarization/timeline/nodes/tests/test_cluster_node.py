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

class TestClusterNode(unittest.TestCase):
	"""
	Test the cluster node.
	"""

	def test_create_empty(self):
		"""
		Test that the document node is created empty.
		"""

		self.assertEqual([ ], ClusterNode().clusters)

	def test_create_with_timestamp(self):
		"""
		Test that the document node saves the timestamp correctly.
		"""

		self.assertEqual(1000, ClusterNode(1000).created_at)

	def test_create_default_timestamp(self):
		"""
		Test that the document node uses the current timestamp if it is not given.
		"""

		self.assertEqual(round(time.time()), round(ClusterNode().created_at))
