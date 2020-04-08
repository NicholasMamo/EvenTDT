"""
Run unit tests on the :class:`~objects.exportable.Exportable` class.
"""

import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from objects.exportable import Exportable
from vsm.vector import Vector

class TestAttributable(unittest.TestCase):
	"""
	Test the :class:`~objects.exportable.Exportable` class.
	"""

	def test_encode_not_dict(self):
		"""
		Test that when encoding something that is not a dictionary, a TypeError is returned.
		"""

		self.assertRaises(TypeError, Exportable.encode, [ 1 ])
		self.assertRaises(TypeError, Exportable.encode, 1)
		self.assertRaises(TypeError, Exportable.encode, True)

	def test_encode_empty_dict(self):
		"""
		Test that when encoding an empty dictionary, another empty dictionary is returned.
		"""

		self.assertEqual({ }, Exportable.encode({ }))

	def test_encode_primitive_dict(self):
		"""
		Test that when encoding a dictionary with primitive values, the same dictionary is returned.
		"""

		data = { 'a': 1, 'b': [ 1, 2 ] }
		self.assertEqual(data, Exportable.encode({ 'a': 1, 'b': [ 1, 2 ] }))

	def test_encode_primitive_recursive_dict(self):
		"""
		Test that when encoding a dictionary with primitive values stored recursively, the same dictionary is returned.
		"""

		data = { 'a': 1, 'b': { 'c': 1 } }
		self.assertEqual(data, Exportable.encode({ 'a': 1, 'b': { 'c': 1 } }))

	def test_encode_primitive_copy(self):
		"""
		Test that when encoding a dictionary of primitives, the encoding is a copy.
		"""

		data = { 'a': 1, 'b': { 'c': 1 } }
		encoding = Exportable.encode({ 'a': 1, 'b': { 'c': 1 } })
		self.assertEqual(data, encoding)
		data['b']['c'] = 2
		self.assertEqual(2, data['b']['c'])
		self.assertEqual(1, encoding['b']['c'])

	def test_encode_vector(self):
		"""
		Test that when encoding a vector, it is converted into a dictionary.
		"""

		v = Vector({ 'a': 1 }, { 'b': 2 })
		data = { 'vector': v }
		encoding = Exportable.encode(data)
		json.loads(json.dumps(encoding))
		self.assertEqual("<class 'vsm.vector.Vector'>", encoding['vector']['class'])
		self.assertEqual({ 'a': 1 }, encoding['vector']['dimensions'])
		self.assertEqual({ 'b': 2 }, encoding['vector']['attributes'])

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
