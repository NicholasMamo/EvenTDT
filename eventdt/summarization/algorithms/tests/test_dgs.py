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
