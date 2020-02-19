"""
Run unit tests on the Vector class
"""

import math
import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '..')
if path not in sys.path:
    sys.path.append(path)

from vector import Vector
from vector_math import *

class TestVector(unittest.TestCase):
	"""
	Test the Vector class.
	"""

	def test_empty_constructor(self):
		"""
		Test providing an empty constructor.
		"""

		v = Vector()
		self.assertEqual({ }, v.dimensions)

	def test_constructor(self):
		"""
		Test providing the dimensions to the vector constructor.
		"""

		v = Vector({"x": 2, "y": 1})
		self.assertEqual({"x": 2, "y": 1}, v.dimensions)

	def test_dimensions(self):
		"""
		Test setting and getting dimensions.
		"""

		v = Vector({"x": 2, "y": 1})
		v.set_dimension("x")
		self.assertEqual({"y": 1}, v.dimensions)

		v.set_dimension("x", 1)
		self.assertEqual({"x": 1, "y": 1}, v.dimensions)

		v.initialize_dimension("x", 2)
		self.assertEqual(1, v.get_dimension("x"))

	def test_initialize_existing_dimension(self):
		"""
		Test initializing a dimension that already exists.
		"""

		v = Vector({"x": 1, "y": 1})
		v.initialize_dimension("x", 2)
		self.assertEqual(1, v.get_dimension("x"))

	def test_initialize_dimension(self):
		"""
		Test initializing a dimension if it doesn't exist.
		"""

		v = Vector({"x": 2, "y": 1})
		v.initialize_dimension("w", 2)
		self.assertEqual(2, v.get_dimension("w"))
		self.assertEqual(1, v.get_dimension("y"))
		self.assertEqual(0, v.get_dimension("p"))

	def test_clear_all_dimensions(self):
		"""
		Test clearing all dimensions.
		"""

		v = Vector({"x": 3, "y": 2, "z": 4})
		v.clear_dimensions()
		self.assertEqual({ }, v.dimensions)

	def test_clear_nonexisting_dimension(self):
		"""
		Test clearing a dimension that does not exist.
		"""

		v = Vector({"x": 3, "y": 2, "z": 4})
		v.clear_dimension("w")
		self.assertEqual({"x": 3, "y": 2, "z": 4}, v.dimensions)

	def test_clear_dimension(self):
		"""
		Test clearing a single dimension.
		"""

		v = Vector({"x": 3, "y": 2, "z": 4})
		v.clear_dimension("x")
		self.assertEqual({"y": 2, "z": 4}, v.dimensions)

	def test_normalization(self):
		"""
		Test normalizing vectors.
		"""

		v = Vector({"x": 3, "y": 1.2, "z": -2})
		v.normalize()
		self.assertEqual({ "x": 0.789474, "y": 0.315789, "z": -0.526316 }, { key: round(value, 6) for key, value in v.dimensions.items() })

	def test_double_normalization(self):
		"""
		Test that normalizing the same vector twice returns the same vector as when normalized once.
		"""

		v = Vector({"x": 3, "y": 1.2, "z": -2})
		v.normalize()
		w = v.copy()
		w.normalize()
		self.assertEqual(v.dimensions, w.dimensions)

	def test_normalize_empty_vector(self):
		"""
		Test that when normalizing an empty vector, the resulting vector is also empty.
		"""

		v = Vector({ })
		v.normalize()
		self.assertEqual({ }, v.dimensions)

	def test_normalize_zero_length_vector(self):
		"""
		Test that when normalizing a vector with a zero length, the resulting vector is also empty.
		"""

		v = Vector({ 'x': 0 })
		v.normalize()
		self.assertEqual({ 'x': 0 }, v.dimensions)

	def test_copy(self):
		"""
		Test copying.
		"""

		v = Vector({ "x": 3 }, { "y": True })
		n = v.copy()

		self.assertEqual(v.get_attributes(), n.get_attributes())
		self.assertEqual(v.dimensions, n.get_dimensions())

		v.set_attribute("y", False)
		self.assertFalse(v.get_attribute("y"))
		self.assertTrue(n.get_attribute("y"))
		v.set_attribute("y", True)

		v.set_dimension("x", 2)
		self.assertEqual(2, v.get_dimension("x"))
		self.assertEqual(3, n.get_dimension("x"))
		v.set_dimension("x", 3)

	def test_export(self):
		"""
		Test exporting and importing vectors.
		"""

		v = Vector({ "x": 3 }, { "y": True })
		e = v.to_array()
		self.assertEqual(v.get_attributes(), Vector.from_array(e).get_attributes())
		self.assertEqual(v.dimensions, Vector.from_array(e).get_dimensions())
		self.assertEqual(v.__dict__, Vector.from_array(e).__dict__)
