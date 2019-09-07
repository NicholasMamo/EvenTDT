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

		d = Document("He would never do that", ["he", "would", "never", "do", "that"], scheme=tf)
		self.assertEqual(d.get_dimensions(), {"he": 1, "would": 1, "never": 1, "do": 1, "that": 1})

		d = Document("He would never do that, would he?", ["he", "would", "never", "do", "that", "would", "he"], scheme=tf)
		self.assertEqual(d.get_dimensions(), {"he": 2, "would": 2, "never": 1, "do": 1, "that": 1})

	def test_label(self):
		"""
		Test the label methods
		"""

		d = Document()
		self.assertEqual(d.get_label(), None)

		d.set_label("L")
		self.assertEqual(d.get_label(), "L")

	def test_export(self):
		"""
		Test exporting and importing documents.
		"""

		d = Document("He would never do that", ["he", "would", "never", "do", "that"], { "timestamp": 0 }, label="Test")
		e = d.to_array()
		self.assertEqual(d.get_attributes(), Document.from_array(e).get_attributes())
		self.assertEqual(d.get_dimensions(), Document.from_array(e).get_dimensions())
		self.assertEqual(d.get_text(), Document.from_array(e).get_text())
		self.assertEqual(d.get_label(), Document.from_array(e).get_label())
		self.assertEqual(d.__dict__, Document.from_array(e).__dict__)
