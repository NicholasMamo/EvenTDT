"""
Run unit tests on the Document class
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '../')
if path not in sys.path:
    sys.path.append(path)

from libraries.vector.nlp.document import Document
from libraries.vector.nlp.term_weighting import TF

class TestDocument(unittest.TestCase):
	"""
	Test the Document class
	"""

	def test_init(self):
		"""
		Test the Document constructor
		"""
		tf = TF()

		d = Document()
		self.assertEqual(d.get_dimensions(), {})

		d = Document("", {"x": 2}, scheme=tf)
		self.assertEqual(d.get_label(), None)
		self.assertEqual(d.get_dimensions(), {"x": 2})

		d = Document(label="L", scheme=tf)
		self.assertEqual(d.get_label(), "L")

		d = Document("", ["he", "would", "never", "do", "that"], scheme=tf)
		self.assertEqual(d.get_dimensions(), {"he": 0.2, "would": 0.2, "never": 0.2, "do": 0.2, "that": 0.2})

		d = Document("", ["he", "would", "never", "do", "that", "would", "he"], scheme=tf)
		self.assertEqual(d.get_dimensions(), {"he": 2/7, "would": 2/7, "never": 1/7, "do": 1/7, "that": 1/7})

	def test_label(self):
		"""
		Test the label methods
		"""

		d = Document()
		self.assertEqual(d.get_label(), None)

		d.set_label("L")
		self.assertEqual(d.get_label(), "L")
