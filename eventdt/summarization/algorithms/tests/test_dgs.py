"""
Run unit tests on the Document Graph Summarizer by Mamo et al. (2019)'s algorithm.
"""

import math
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from nlp.term_weighting.tf import TF
from summarization import Summary
from summarization.algorithms import DGS
from vsm import vector_math

class TestDGS(unittest.TestCase):
	"""
	Test Document Graph Summarizer by Mamo et al. (2019)'s algorithm.
	"""

	def test_negative_length(self):
		"""
		Test that when providing a negative length, the function raises a ValueError.
		"""

		c = [ ]
		algo = DGS()
		self.assertRaises(ValueError, algo.summarize, c, -1)

	def test_zero_length(self):
		"""
		Test that when providing a length of zero, the function raises a ValueError.
		"""

		c = [ ]
		algo = DGS()
		self.assertRaises(ValueError, algo.summarize, c, 0)

	def test_compute_query_empty(self):
		"""
		Test that the query is empty when no documents are given.
		"""

		algo = DGS()
		self.assertEqual({ }, algo._compute_query([ ]).dimensions)

	def test_compute_query_one_document(self):
		"""
		Test that the query construction is identical to the given document when there is just one document.
		"""

		d = Document('this is not a pipe', { 'pipe': 1 })
		algo = DGS()
		self.assertEqual(d.dimensions, algo._compute_query([ d ]).dimensions)

	def test_compute_query_normalized(self):
		"""
		Test that the query is normallized.
		"""

		d = Document('this is not a pipe', { 'this': 1, 'pipe': 1 })
		d.normalize()
		algo = DGS()
		self.assertEqual(1, round(vector_math.magnitude(algo._compute_query([ d ])), 10))

	def test_compute_query(self):
		"""
		Test the query construction with multiple documents.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a pipe', { 'this': 1 }),
		 		   Document('this is not a pipe', { 'pipe': 1 }) ]

		algo = DGS()
		self.assertEqual(round(math.sqrt(2)/2., 10), round(algo._compute_query(corpus).dimensions['this'], 10))
		self.assertEqual(round(math.sqrt(2)/2., 10), round(algo._compute_query(corpus).dimensions['pipe'], 10))
		self.assertEqual(1, round(vector_math.magnitude(algo._compute_query(corpus)), 10))
