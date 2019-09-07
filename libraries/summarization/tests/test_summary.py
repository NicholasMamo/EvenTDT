"""
Run unit tests on the Summary class.
"""

import math
import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '../')
if path not in sys.path:
    sys.path.append(path)

from libraries.summarization.summary import Summary

from libraries.vector.nlp.document import Document

class TestSummary(unittest.TestCase):
	"""
	Test the Summary class.
	"""

	def test_export(self):
		"""
		Test exporting and importing vectors.
		"""

		d = [
			Document(text="A"),
			Document(text="B")
		]
		s = Summary(d, 100)
		e = s.to_array()

		self.assertEqual(s.created_at(), Summary.from_array(e).created_at())
		self.assertEqual(s.last_updated(), Summary.from_array(e).last_updated())
		self.assertEqual(s.generate_summary(), Summary.from_array(e).generate_summary())
