"""
Test the functionality of the summarization tool.
"""

import json
import os
import re
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
 		  os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

from nlp import Document
from summarization.algorithms import MMR, DGS
from tools import summarize

class TestSummarize(unittest.TestCase):
	"""
	Test the functionality of the summarization tool.
	"""

	def test_create_mmr_custom_lambda(self):
		"""
		Test that when creating MMR with a custom lambda, it is saved
		"""

		summarizer = summarize.create_summarizer(MMR, l=0.7)
		self.assertEqual(0.7, summarizer.l)

	def test_filter_documents_order(self):
		"""
		Test that when filtering documents, the documents are returned in the same order.
		"""

		documents = [ Document('a'), Document('b'), Document('c') ]
		self.assertEqual(documents, summarize.filter_documents(documents))

	def test_filter_documents_with_duplicates(self):
		"""
		Test that when filtering documents, duplicates are removed automatically.
		"""

		documents = [ Document('a'), Document('b'), Document('c'), Document('a') ]
		self.assertEqual(documents[-3:], summarize.filter_documents(documents))

	def test_filter_documents_empty(self):
		"""
		Test that when filtering an empty list of documents, another empty list is returned.
		"""

		documents = [ ]
		self.assertEqual([ ], summarize.filter_documents(documents))

	def test_filter_documents_None(self):
		"""
		Test that when filtering a list of documents, if no maximum number of documents is given, all documents are retained.
		"""

		documents = [ Document('a'), Document('b'), Document('c') ]
		self.assertEqual(documents, summarize.filter_documents(documents, max_documents=None))

	def test_filter_documents_too_few(self):
		"""
		Test that when filtering a list of documents, if the maximum number of documents exceed the number of documents, all documents are returned.
		"""

		documents = [ Document('a'), Document('b'), Document('c') ]
		self.assertEqual(documents, summarize.filter_documents(documents, max_documents=len(documents)+1))

	def test_filter_documents_longest(self):
		"""
		Test that when filtering a list of documents, the longest documents are returned.
		"""

		documents = [ Document('aaa'), Document('bb'), Document('c') ]
		self.assertEqual(documents[:2], summarize.filter_documents(documents, max_documents=2))
