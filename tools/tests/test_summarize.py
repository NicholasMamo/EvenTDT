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

from tools import summarize
from summarization.algorithms import MMR, DGS

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
