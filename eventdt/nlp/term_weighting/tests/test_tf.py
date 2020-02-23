"""
Run unit tests on the :class:`nlp.term_weighting.tf.TF` class.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from tf import TF

class TestTF(unittest.TestCase):
	"""
	Test the :class:`nlp.term_weighting.tf.TF` class.
	"""

	def test_empty_list_score(self):
		"""
		Test that weighting an empty list returns no weights.
		"""

		tokens = []
		document = TF().create(tokens)
		self.assertEqual({ }, document.dimensions)

	def test_list_score(self):
		"""
		Test that weighting a list returns the weights of the documents.
		"""

		tokens = [ 'a', 'b' ]
		document = TF().create(tokens)
		self.assertEqual({ 'a': 1, 'b': 1 }, document.dimensions)

	def test_repeated_score(self):
		"""
		Test that weighting a list with repeated features returns frequency counts.
		"""

		tokens = [ 'a', 'b', 'a' ]
		document = TF().create(tokens)
		self.assertEqual({ 'a': 2, 'b': 1 }, document.dimensions)
