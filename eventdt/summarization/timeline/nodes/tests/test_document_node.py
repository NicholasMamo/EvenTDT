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

	def test_add(self):
		"""
		Test adding documents to the node.
		"""

		node = DocumentNode()
		self.assertEqual([ ], node.documents)
		document = Document('')
		node.add([ document ])
		self.assertEqual([ document ], node.documents)

	def test_add_multiple(self):
		"""
		Test adding multiple documents to the node.
		"""

		node = DocumentNode()
		self.assertEqual([ ], node.documents)
		documents = [ Document('') for i in range(2)]
		node.add(documents)
		self.assertEqual(documents, node.documents)

	def test_add_repeated(self):
		"""
		Test adding documents one at a time to the node.
		"""

		node = DocumentNode()
		self.assertEqual([ ], node.documents)
		documents = [ Document('') for i in range(2)]
		node.add([ documents[0] ])
		self.assertEqual([ documents[0] ], node.documents)
		node.add([ documents[1] ])
		self.assertEqual(documents, node.documents)
