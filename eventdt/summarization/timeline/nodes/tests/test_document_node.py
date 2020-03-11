"""
Run unit tests on the document node.
"""

import os
import sys
import time
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from summarization.timeline.nodes import DocumentNode

class TestDocumentNode(unittest.TestCase):
	"""
	Test the document node.
	"""

	def test_create_empty(self):
		"""
		Test that the document node is created empty.
		"""

		self.assertEqual([ ], DocumentNode().documents)

	def test_create_with_timestamp(self):
		"""
		Test that the document node saves the timestamp correctly.
		"""

		self.assertEqual(1000, DocumentNode(1000).created_at)

	def test_create_default_timestamp(self):
		"""
		Test that the document node uses the current timestamp if it is not given.
		"""

		self.assertEqual(round(time.time()), round(DocumentNode().created_at))
