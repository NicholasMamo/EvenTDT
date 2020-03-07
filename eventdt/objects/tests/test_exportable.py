"""
Run unit tests on the :class:`~objects.exportable.Exportable` class.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from exportable import Exportable

class TestAttributable(unittest.TestCase):
	"""
	Test the :class:`~objects.exportable.Exportable` class.
	"""

	def test_get_module_empty(self):
		"""
		Test that when getting the module name from an invalid string, a ValueError is raised.
		"""

		self.assertRaises(ValueError, Exportable.get_module, '')

	def test_get_module_class_only(self):
		"""
		Test that when getting the module name from a string that contains only a class name, nothing is returned.
		"""

		self.assertEqual('', Exportable.get_module("<class 'Document'>"))

	def test_get_module(self):
		"""
		Test getting the module name from a string.
		"""

		self.assertEqual('nlp.document', Exportable.get_module("<class 'nlp.document.Document'>"))

	def test_get_class_empty(self):
		"""
		Test that when getting the class name from an invalid string, a ValueError is raised.
		"""

		self.assertRaises(ValueError, Exportable.get_class, '')

	def test_get_class_class_only(self):
		"""
		Test that when getting the class name from a string that contains only a class name, that name is returned.
		"""

		self.assertEqual('Document', Exportable.get_class("<class 'Document'>"))

	def test_get_class(self):
		"""
		Test getting the class name from a string.
		"""

		self.assertEqual('Document', Exportable.get_class("<class 'nlp.document.Document'>"))
