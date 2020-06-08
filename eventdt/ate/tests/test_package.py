"""
Test the functionality of the ATE package-level functions.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

import ate

class TestPackage(unittest.TestCase):
	"""
	Test the functionality of the ATE package-level functions.
	"""

	def test_total_documents_empty_corpus(self):
		"""
		Test that the number of documents in an empty corpus is 0.
		"""

		path = os.path.join(os.path.dirname(__file__), 'empty.json')
		documents = ate.total_documents(path)
		self.assertEqual(0, documents)

	def test_total_documents_one_corpus(self):
		"""
		Test getting the number of documents from one corpus.
		"""

		path = os.path.join(os.path.dirname(__file__), 'c1.json')
		documents = ate.total_documents(path)

		"""
		Count the documents by reading all lines.
		"""
		with open(path, 'r') as f:
			self.assertEqual(documents, len(f.readlines()))

	def test_total_documents_multiple_corpora(self):
		"""
		Test getting the number of documents from multiple corpora.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
				  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		documents = ate.total_documents(paths)

		"""
		Count the documents by reading all lines.
		"""
		total = 0
		for path in paths:
			with open(path, 'r') as f:
				total += len(f.readlines())

		self.assertEqual(documents, total)
