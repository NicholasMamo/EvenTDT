"""
Run unit tests on the :class:`eventdt.nlp.term_weighting.global.idf.IDF` class.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from idf import IDF

class TestTF(unittest.TestCase):
	"""
	Test the :class:`eventdt.nlp.term_weighting.global.idf.IDF` class.
	"""

	def test_high_value(self):
		"""
		Test that the IDF raises an error when the highest IDF value is higher than the number of documents.
		"""

		idf = { 'a': 3, 'b': 1 }
		self.assertRaises(ValueError, IDF, idf, 2)

	def test_negative_value(self):
		"""
		Test that the IDF raises an error when any IDF value is negative.
		"""

		idf = { 'a': 3, 'b': -1 }
		self.assertRaises(ValueError, IDF, idf, 3)

	def test_negative_documents(self):
		"""
		Test that the IDF raises an error when the number of documents is negative.
		"""

		idf = { 'a': 3, 'b': 1 }
		self.assertRaises(ValueError, IDF, idf, -1)

	def test_idf_equal_documents(self):
		"""
		Test that when the DF of a feature is cloes to the number of documents, the result is 0.
		"""

		idf = { 'a': 3, 'b': 1 }
		idf = IDF(idf, 4)
		tokens = [ 'a' ]
		self.assertEqual(0, idf.score(tokens)['a'])

	def test_idf(self):
		"""
		Test IDF in normal conditions.
		"""

		idf = { 'a': 3, 'b': 1 }
		idf = IDF(idf, 4)
		tokens = [ 'b' ]
		self.assertEqual(0.30103, round(idf.score(tokens)['b'], 5))

	def test_idf_zero_term(self):
		"""
		Test that IDF scores terms even if they do not appear in the IDF table.
		"""

		idf = { 'a': 3, 'b': 1 }
		idf = IDF(idf, 4)
		tokens = [ 'c' ]
		self.assertEqual(0.60206, round(idf.score(tokens)['c'], 5))
