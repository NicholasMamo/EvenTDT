"""
Run unit tests on the Summary class.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from summary import Summary
from nlp.document import Document

class TestSummary(unittest.TestCase):
	"""
	Test the Summary class.
	"""

	def test_empty_summary(self):
		"""
		Test that when creating an empty summary, it is created with an empty list.
		"""

		summary = Summary()
		self.assertEqual([ ], summary.documents)

	def test_summary_one_document(self):
		"""
		Test that when creating a summary with one document, it is transformed into a list.
		"""

		d = Document('this is not a cigar', { 'this': 1, 'cigar': 1 })
		summary = Summary(d)
		self.assertEqual([ d ], summary.documents)

	def test_summary_several_documents(self):
		"""
		Test that when creating a summary with several documents, they are stored as a list.
		"""

		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]
		summary = Summary(corpus)
		self.assertEqual(corpus, summary.documents)

	def test_set_documents_empty(self):
		"""
		Test that when setting the documents to `None`, it is transformed into an empty list.
		"""

		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]
		summary = Summary(corpus)
		self.assertEqual(corpus, summary.documents)
		summary.documents = None
		self.assertEqual([ ], summary.documents)

	def test_set_documents_one(self):
		"""
		Test that when setting the documents to one document, it is transformed into a list.
		"""

		document = Document('this is not a cigar', { 'this': 1, 'cigar': 1 })
		summary = Summary()
		self.assertEqual([ ], summary.documents)
		summary.documents = document
		self.assertEqual([ document ], summary.documents)

	def test_set_documents_several(self):
		"""
		Test that when setting a list of documents, they are stored as a list.
		"""

		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]
		summary = Summary()
		summary.documents = corpus
		self.assertEqual(corpus, summary.documents)

	def test_str_empty(self):
		"""
		Test that the string representation of an empty summary is an empty string.
		"""

		summary = Summary()
		self.assertEqual('', str(summary))

	def test_str(self):
		"""
		Test that the string representation of the summary is equivalent to all of the documents in it.
		"""

		documents = [ Document('this is not'), Document('a pipe') ]
		summary = Summary(documents)
		self.assertEqual('this is not a pipe', str(summary))

	def test_str_sorted(self):
		"""
		Test that when printing a a summary, if all documents have a timestamp, they are ordered chronologically.
		"""

		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]
		summary = Summary()
		summary.documents = corpus
		self.assertEqual(' '.join(document.text for document in corpus), str(summary))

		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }, attributes={ 'timestamp': 1 } ),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }, attributes={ 'timestamp': 0 } ) ]
		summary = Summary()
		summary.documents = corpus
		self.assertEqual(' '.join(document.text for document in corpus[::-1]), str(summary))

	def test_export(self):
		"""
		Test exporting and importing summaries.
		"""

		documents = [ Document('A'), Document('B') ]
		summary = Summary(documents)
		export = summary.to_array()

		"""
		Check that the documents were exported correctly.
		"""
		self.assertEqual(len(documents), len(Summary.from_array(export).documents))
		for document in documents:
			self.assertTrue(any(document.__dict__ == imported.__dict__
								for imported in Summary.from_array(export).documents))

	def test_export_attributes(self):
		"""
		Test that exporting and importing summaries includes the attributes.
		"""

		documents = [ Document('A'), Document('B') ]
		summary = Summary(documents, { 'a': 0 })
		export = summary.to_array()

		self.assertEqual(summary.attributes, Summary.from_array(export).attributes)
