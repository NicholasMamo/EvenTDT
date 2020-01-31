"""
Run unit tests on the :class:`eventdt.nlp.document.Document` class.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from document import Document
from term_weighting import TF

class TestDocument(unittest.TestCase):
	"""
	Test the :class:`eventdt.nlp.document.Document` class.
	"""

	def test_empty_document(self):
		"""
		Test that the document may be created empty.
		"""

		d = Document()
		self.assertEqual('', d.text)
		self.assertEqual({ }, d.dimensions)

	def test_document_constructor(self):
		"""
		Test creating a document with text and dimensions.
		"""

		d = Document('text', { 'text': 1 })
		self.assertEqual('text', d.text)
		self.assertEqual({ 'text': 1 }, d.dimensions)

	def test_document_attributes(self):
		"""
		Test creating a document with text, dimensions, and attributes.
		"""

		d = Document('text', { 'text': 1 }, attributes={ 'label': True })
		self.assertEqual('text', d.text)
		self.assertEqual({ 'text': 1 }, d.dimensions)
		self.assertTrue(d.get_attribute('label'))

	def test_create_document_with_tokens(self):
		"""
		Test creating a document with tokens and a term-weighting scheme.
		"""

		text = 'this is not a pipe'
		d = Document(text, text.split(), scheme=TF())
		self.assertEqual({ 'this': 1, 'is': 1, 'not': 1, 'a': 1, 'pipe': 1 }, d.dimensions)

	def test_export(self):
		"""
		Test exporting and importing documents.
		"""

		text = 'this is not a pipe'
		d = Document(text, text.split(), attributes={ 'timestamp': 10 })
		e = d.to_array()
		self.assertEqual(d.get_attributes(), Document.from_array(e).get_attributes())
		self.assertEqual(d.get_dimensions(), Document.from_array(e).get_dimensions())
		self.assertEqual(d.text, Document.from_array(e).text)
		self.assertEqual(d.get_attribute('timestamp'), Document.from_array(e).get_attribute('timestamp'))
		self.assertEqual(d.__dict__, Document.from_array(e).__dict__)
