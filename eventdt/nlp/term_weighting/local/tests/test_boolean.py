"""
Run unit tests on the :class:`eventdt.nlp.term_weighting.local.boolean.Boolean` class.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from boolean import Boolean

class TestBoolean(unittest.TestCase):
	"""
	Test the :class:`eventdt.nlp.term_weighting.local.boolean.Boolean` class.
	"""

	def test_empty_list_score(self):
		"""
		Test that weighting an empty list returns no weights.
		"""

		tokens = []
		scheme = Boolean()
		self.assertEquals({ }, scheme.score(tokens))

	def test_list_score(self):
		"""
		Test that weighting a list returns the weights of the documents.
		"""

		tokens = [ 'a', 'b' ]
		scheme = Boolean()
		self.assertEquals({ 'a': 1, 'b': 1 }, scheme.score(tokens))

	def test_repeated_score(self):
		"""
		Test that weighting a list with repeated features returns boolean weights.
		"""

		tokens = [ 'a', 'b', 'a' ]
		scheme = Boolean()
		self.assertEquals({ 'a': 1, 'b': 1 }, scheme.score(tokens))
