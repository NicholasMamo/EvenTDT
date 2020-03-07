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

	def test_repr_empty(self):
		"""
		Test that the string representation of an empty summary is an empty string.
		"""

		summary = Summary()
		self.assertEqual('', str(summary))

	def test_repr(self):
		"""
		Test that the string representation of the summary is equivalent to all of the documents in it.
		"""

		documents = [ Document('this is not'), Document('a pipe') ]
		summary = Summary(documents)
		self.assertEqual('this is not a pipe', str(summary))

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
