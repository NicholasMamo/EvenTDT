"""
Run unit tests on the document node.
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

	def test_add_dynamic(self):
		"""
		Test that when changing a document, the node's document also changes.
		"""

		node = DocumentNode()
		self.assertEqual([ ], node.documents)
		document = Document('', { })
		node.add([ document ])
		self.assertEqual([ document ], node.documents)
		document.dimensions['x'] = 1
		self.assertEqual({ 'x': 1 }, document.dimensions)
		self.assertEqual(document.dimensions, node.documents[0].dimensions)

	def test_get_all_documents_empty(self):
		"""
		Test that when getting all documents from an empty node, an empty list is returned.
		"""

		node = DocumentNode()
		self.assertEqual([ ], node.get_all_documents())

	def test_get_all_documents(self):
		"""
		Test that when getting all documents from a node, all documents are returned.
		"""

		node = DocumentNode()
		corpus = [ Document('', { }), Document('', { }) ]
		self.assertEqual([ ], node.get_all_documents())
		node.add([ corpus[0] ])
		self.assertEqual([ corpus[0] ], node.get_all_documents())
		node.add([ corpus[1] ])
		self.assertEqual(corpus, node.get_all_documents())

	def test_similarity_empty_node(self):
		"""
		Test that the similarity between a document and an empty document node, the similarity is 0.
		"""

		node = DocumentNode()
		self.assertEqual([ ], node.documents)
		self.assertEqual(0, node.similarity(Document('', { 'x': 1 })))

	def test_similarity_empty_document(self):
		"""
		Test that the similarity between a node and an empty document, the similarity is 0.
		"""

		"""
		Create the test data.
		"""
		documents = [ Document('this is not a pipe', { 'pipe': 1 }),
		 			  Document('this is not a cigar', { 'cigar': 1 }) ]

		node = DocumentNode()
		node.add(documents)
		self.assertEqual(documents, node.documents)
		self.assertEqual(0, node.similarity(Document('', { })))

	def test_similarity(self):
		"""
		Test calculating the similarity between a node and a document.
		"""

		"""
		Create the test data.
		"""
		documents = [ Document('this is not a pipe', { 'pipe': 1 }),
		 			  Document('this is not a cigar', { 'cigar': 1 }) ]

		node = DocumentNode()
		node.add(documents)
		self.assertEqual(documents, node.documents)
		self.assertEqual(math.sqrt(2)/2., node.similarity(Document('this is not a pipe', { 'pipe': 1 })))

	def test_similarity_lower_bound(self):
		"""
		Test that the similarity lower-bound between a node and a document is 0.
		"""

		"""
		Create the test data.
		"""
		documents = [ Document('this is not a pipe', { 'pipe': 1 }),
		 			  Document('this is not a cigar', { 'cigar': 1 }) ]

		node = DocumentNode()
		node.add(documents)
		self.assertEqual(documents, node.documents)
		self.assertEqual(0, node.similarity(Document('this is a picture of dorian gray', { 'picture': 1, 'dorian': 1, 'gray': 1 })))

	def test_similarity_upper_bound(self):
		"""
		Test that the similarity upper-bound between a node and a document is 1.
		"""

		"""
		Create the test data.
		"""
		documents = [ Document('this is not a pipe', { 'pipe': 1 }),
		 			  Document('this is not a cigar', { 'cigar': 1 }) ]

		node = DocumentNode()
		node.add(documents)
		self.assertEqual(documents, node.documents)
		self.assertEqual(1, node.similarity(Document('this is not a pipe and this is not a cigar', { 'cigar': 1, 'pipe': 1 })))

	def test_expired_inclusive(self):
		"""
		Test that the expiry is inclusive.
		"""

		node = DocumentNode(created_at=1000)
		self.assertTrue(node.expired(10, 1010))

	def test_expired_far_timestamp(self):
		"""
		Test that a node is expired if the timestamp is sufficiently far.
		"""

		node = DocumentNode(created_at=1000)
		self.assertTrue(node.expired(10, 1011))

	def test_expired_close_timestamp(self):
		"""
		Test that a node is not expired if the timestamp is close.
		"""

		node = DocumentNode(created_at=1000)
		self.assertFalse(node.expired(10, 1001))

	def test_expired_past_timestamp(self):
		"""
		Test that a node is not expired if the timestamp is in the past.
		"""

		node = DocumentNode(created_at=1000)
		self.assertFalse(node.expired(10, 999))

	def test_expired_realtime(self):
		"""
		Test that when the timestamp is not given, the current timestamp is used.
		"""

		node = DocumentNode(created_at=time.time())
		self.assertFalse(node.expired(1))

	def test_expired_realtime_sleep(self):
		"""
		Test that when the timestamp is not given, the current timestamp is used.
		"""

		node = DocumentNode(created_at=time.time())
		time.sleep(1)
		self.assertTrue(node.expired(1))

	def test_expired_zero(self):
		"""
		Test that a node immediately expired if the expiry is 0.
		"""

		node = DocumentNode(created_at=1000)
		self.assertTrue(node.expired(0, 1000))

	def test_expired_negative(self):
		"""
		Test that a ValueError is raised when the expiry is negative.
		"""

		node = DocumentNode(created_at=1000)
		self.assertRaises(ValueError, node.expired, -1, 0)
