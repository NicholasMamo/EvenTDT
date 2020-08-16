"""
Test the functionality of the summarization tool.
"""

import json
import math
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
from summarization.timeline import Timeline
from summarization.timeline.nodes import TopicalClusterNode
from tools import summarize
from vsm import Vector
from vsm.clustering import Cluster

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

	def test_summarizer_with_query(self):
		"""
		Test that when summarizing with a query, the summaries are more topical.
		"""

		summarizer = summarize.create_summarizer(DGS)
		timeline = Timeline(TopicalClusterNode, 60, 0.5)
		documents = [ Document('this is not a pipe', { 'this': 1/math.sqrt(2), 'pipe': 1/math.sqrt(2) }),
		 			  Document('this is not a cigar', { 'this': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }),
					  Document('cigars are where it is at', { 'where': 1/math.sqrt(2), 'cigar': 1/math.sqrt(2) }) ]
		cluster = Cluster(documents)
		timeline.add(cluster=cluster, topic=Vector({ 'where': 1 }))

		summaries = summarize.summarize(summarizer, timeline, length=30, with_query=False)
		self.assertEqual(1, len(summaries[0].documents))
		self.assertEqual(str(documents[2]), str(summaries[0]))

		summaries = summarize.summarize(summarizer, timeline, length=30, with_query=True)
		self.assertEqual(1, len(summaries[0].documents))
		self.assertEqual(str(documents[2]), str(summaries[0]))

		timeline = Timeline(TopicalClusterNode, 60, 0.5)
		timeline.add(cluster=cluster, topic=Vector({ 'this': 1 }))
		summaries = summarize.summarize(summarizer, timeline, length=30, with_query=True)
		self.assertEqual(1, len(summaries[0].documents))
		self.assertEqual(str(documents[1]), str(summaries[0]))

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

	def test_filter_documents_with_duplicates_case_insensitive(self):
		"""
		Test that when filtering documents, duplicates are removed automatically even if they have different capitalization.
		"""

		documents = [ Document('a'), Document('b'), Document('c'), Document('A') ]
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
