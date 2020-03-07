"""
Run unit tests on the :class:`~nlp.document.Document` class.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from document import Document
from tokenizer import Tokenizer
from term_weighting.tf import TF

class TestDocument(unittest.TestCase):
	"""
	Test the :class:`~nlp.document.Document` class.
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
		self.assertTrue(d.attributes['label'])

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
		self.assertEqual(d.dimensions, Document.from_array(e).dimensions)
		self.assertEqual(d.text, Document.from_array(e).text)
		self.assertEqual(d.__dict__, Document.from_array(e).__dict__)

	def test_export_attributes(self):
		"""
		Test that exporting and importing documents include their attributes.
		"""

		text = 'this is not a pipe'
		d = Document(text, text.split(), attributes={ 'timestamp': 10 })
		e = d.to_array()
		self.assertEqual(d.attributes, Document.from_array(e).attributes)
		self.assertEqual(d.attributes['timestamp'], Document.from_array(e).attributes['timestamp'])

	def test_concatenate(self):
		"""
		Test that when documents are concatenated, all documents are part of the new document.
		"""

		"""
		Create the test data.
		"""
		strings = [
			'this is not a pipe',
			'this is just a cigarette',
			'still just as deadly'
		]

		tokenizer = Tokenizer(stem=False)
		documents = [
			Document(string, tokenizer.tokenize(string), scheme=TF()) for string in strings
		]

		document = Document.concatenate(*documents, tokenizer=tokenizer, scheme=TF())
		self.assertEqual(2, document.dimensions.get('this'))
		self.assertEqual(2, document.dimensions.get('just'))
		self.assertEqual(1, document.dimensions.get('pipe'))
		self.assertEqual(1, document.dimensions.get('cigarette'))
		self.assertEqual(1, document.dimensions.get('deadly'))
		self.assertEqual(' '.join(strings), document.text)

	def test_concatenate_zero_documents(self):
		"""
		Test that when no documents are given to be concatenated, an empty document is created.
		"""

		tokenizer = Tokenizer(stem=False)
		documents = [ ]

		document = Document.concatenate(*documents, tokenizer=tokenizer, scheme=TF())
		self.assertFalse(document.dimensions)
		self.assertEqual('', document.text)

	def test_concatenate_with_attributes(self):
		"""
		Test that when attributes are given to the concatentation, they are included in the new document.
		"""

		"""
		Create the test data.
		"""
		strings = [
			'this is not a pipe',
			'this is just a cigarette',
			'still just as deadly'
		]

		tokenizer = Tokenizer(stem=False)
		documents = [
			Document(string, tokenizer.tokenize(string), scheme=TF()) for string in strings
		]

		document = Document.concatenate(*documents, tokenizer=tokenizer, scheme=TF(),
										attributes={ 'attr': True })
		self.assertTrue(document.attributes['attr'])

	def test_repr(self):
		"""
		Test that the string representation of the document is equivalent to its text.
		"""

		document = Document('this is not a pipe')
		self.assertEqual('this is not a pipe', str(document))
