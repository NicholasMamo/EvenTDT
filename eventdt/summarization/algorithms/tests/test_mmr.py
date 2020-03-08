"""
Run unit tests on Carbonell and Goldstein (1998)'s algorithm.
"""

import math
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from summarization import Summary
from summarization.algorithms import MMR
from vsm import vector_math

class TestMMR(unittest.TestCase):
	"""
	Test Carbonell and Goldstein (1998)'s algorithm.
	"""

	def test_negative_length(self):
		"""
		Test that when providing a negative length, the function raises a ValueError.
		"""

		c = [ ]
		algo = MMR()
		self.assertRaises(ValueError, algo.summarize, c, -1)

	def test_zero_length(self):
		"""
		Test that when providing a length of zero, the function raises a ValueError.
		"""

		c = [ ]
		algo = MMR()
		self.assertRaises(ValueError, algo.summarize, c, 0)

	def test_negative_lambda(self):
		"""
		Test that when lambda is negative, the function raises a ValueError.
		"""

		c = [ ]
		algo = MMR()
		self.assertRaises(ValueError, algo.summarize, c, 0, l=-0.1)

	def test_large_lambda(self):
		"""
		Test that when lambda is large, the function raises a ValueError.
		"""

		c = [ ]
		algo = MMR()
		self.assertRaises(ValueError, algo.summarize, c, 0, l=1.1)

	def test_compute_query_empty(self):
		"""
		Test that the query is empty when no documents are given.
		"""

		algo = MMR()
		self.assertEqual({ }, algo._compute_query([ ]).dimensions)

	def test_compute_query_one_document(self):
		"""
		Test that the query construction is identical to the given document when there is just one document.
		"""

		d = Document('this is not a pipe', { 'pipe': 1 })
		algo = MMR()
		self.assertEqual(d.dimensions, algo._compute_query([ d ]).dimensions)

	def test_compute_query_normalized(self):
		"""
		Test that the query is normallized.
		"""

		d = Document('this is not a pipe', { 'this': 1, 'pipe': 1 })
		d.normalize()
		algo = MMR()
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

		algo = MMR()
		self.assertEqual(round(math.sqrt(2)/2., 10), round(algo._compute_query(corpus).dimensions['this'], 10))
		self.assertEqual(round(math.sqrt(2)/2., 10), round(algo._compute_query(corpus).dimensions['pipe'], 10))
		self.assertEqual(1, round(vector_math.magnitude(algo._compute_query(corpus)), 10))

	def test_compute_similarity_matrix_documents_empty(self):
		"""
		Test that the cimilarity matrix has only one row and column when no documents are given.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]
		for document in corpus:
			document.normalize()

		algo = MMR()
		query = algo._compute_query(corpus)
		matrix = algo._compute_similarity_matrix([ ], query)
		self.assertEqual(1, len(matrix))
		self.assertEqual(1, len(matrix[query]))

	def test_compute_similarity_matrix_documents_unchanged(self):
		"""
		Test that the documents given to the similarity matrix are unchanged.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]
		for document in corpus:
			document.normalize()

		algo = MMR()
		query = algo._compute_query(corpus)
		copy = list(corpus)
		matrix = algo._compute_similarity_matrix(corpus, query)
		self.assertEqual(copy, corpus)

	def test_compute_similarity_matrix_query_unchanged(self):
		"""
		Test that the query given to the similarity matrix is unchanged.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]
		for document in corpus:
			document.normalize()

		algo = MMR()
		query = algo._compute_query(corpus)
		copy = query.copy()
		matrix = algo._compute_similarity_matrix(corpus, query)
		self.assertEqual(copy.dimensions, query.dimensions)

	def test_compute_similarity_matrix_diagonal(self):
		"""
		Test that the diagonal of a similarity matrix is 1.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]
		for document in corpus:
			document.normalize()

		algo = MMR()
		query = algo._compute_query(corpus)

		matrix = algo._compute_similarity_matrix(corpus, query)
		self.assertTrue(all(round(matrix[document][document], 10) == 1 for document in corpus + [query]))

	def test_compute_similarity_matrix_symmetrical(self):
		"""
		Test that the similarity matrix is symmetrical.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]
		for document in corpus:
			document.normalize()

		algo = MMR()
		query = algo._compute_query(corpus)

		matrix = algo._compute_similarity_matrix(corpus, query)
		self.assertTrue(all(matrix[document][other] == matrix[other][document]
							for document in corpus + [query]
							for other in matrix[document]))

	def test_filter_documents_empty(self):
		"""
		Test that when filtering an empty list of documents, an empty list is returned.
		"""

		algo = MMR()
		self.assertEqual([ ], algo._filter_documents([ ], Summary(), 0))

	def test_filter_documents_empty_summary(self):
		"""
		Test that when filtering a list of documents with an empty summary, the same documents are returned.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]

		algo = MMR()
		self.assertEqual(set(corpus), set(algo._filter_documents(corpus, Summary(), 99)))

	def test_filter_documents_in_summary(self):
		"""
		Test filtering documents in the summary.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]

		algo = MMR()
		self.assertEqual([ corpus[1] ], algo._filter_documents(corpus, Summary(corpus[0]), 99))

	def test_filter_all_documents(self):
		"""
		Test that when filtering all of the documents in the summary, an empty list is returned.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]

		algo = MMR()
		self.assertEqual([ ], algo._filter_documents(corpus, Summary(corpus), 99))

	def test_filter_extra_documents(self):
		"""
		Test that when the summary contains extra documents, an empty list is returned.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]

		algo = MMR()
		self.assertEqual([ ], algo._filter_documents(corpus[:1], Summary(corpus), 99))

	def test_filter_zero_length(self):
		"""
		Test that when filtering with a length of zero, no documents are retained.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]

		algo = MMR()
		self.assertEqual([ ], algo._filter_documents(corpus, Summary(), 0))

	def test_filter_exact_length(self):
		"""
		Test that when a document has the same length as the filter length, it is retained.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]

		algo = MMR()
		self.assertEqual(set(corpus), set(algo._filter_documents(corpus, Summary(), len(str(corpus[0])))))

	def test_filter_length(self):
		"""
		Test that when filtering with a length, longer documents are excluded.
		"""

		"""
		Create the test data.
		"""
		corpus = [ Document('this is not a cigar', { 'this': 1, 'cigar': 1 }),
		 		   Document('this is a pipe', { 'this': 1, 'pipe': 1 }) ]

		algo = MMR()
		self.assertEqual(corpus[1:], algo._filter_documents(corpus, Summary(), len(str(corpus[1]))))
