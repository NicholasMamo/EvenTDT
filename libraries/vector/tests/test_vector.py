"""
Run unit tests on the Vector class
"""

import math
import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '../')
if path not in sys.path:
    sys.path.append(path)

# sys.path.insert(1, os.path.join(sys.path[0], '..'))
# from vector import Vector

from libraries.vector.vector import Vector
from libraries.vector.vector_math import *

class TestVector(unittest.TestCase):
	"""
	Test the Vector class
	"""

	def test_init(self):
		"""
		Test the Vector constructor
		"""

		v = Vector()
		self.assertEqual(v.get_dimensions(), {})

		v = Vector({"x": 2, "y": 1})
		self.assertEqual(v.get_dimensions(), {"x": 2, "y": 1})

	def test_dimensions(self):
		"""
		Test setting and getting dimensions
		"""

		v = Vector({"x": 2, "y": 1})
		v.set_dimension("x")
		self.assertEqual(v.get_dimensions(), {"y": 1})

		v.set_dimension("x", 1)
		self.assertEqual(v.get_dimensions(), {"x": 1, "y": 1})

		v.initialize_dimension("x", 2)
		self.assertEqual(v.get_dimension("x"), 1)

		v.initialize_dimension("w", 2)
		self.assertEqual(v.get_dimension("w"), 2)

		self.assertEqual(v.get_dimension("y"), 1)

		self.assertEqual(v.get_dimension("p"), 0)

	def test_clear_dimensions(self):
		"""
		Test clearing dimensions
		"""

		v = Vector({"x": 3, "y": 2, "z": 4})
		v.clear_dimensions()
		self.assertEqual(v.get_dimensions(), {})

		v = Vector({"x": 3, "y": 2, "z": 4})
		v.clear_dimension("w")
		self.assertEqual(v.get_dimensions(), {"x": 3, "y": 2, "z": 4})

		v.clear_dimension("x")
		self.assertEqual(v.get_dimensions(), {"y": 2, "z": 4})

	def test_normalization(self):
		"""
		Test normalizing vectors
		"""

		v = Vector({"x": 3, "y": 1.2, "z": -2})
		v.normalize()
		self.assertEqual({ key: round(value, 6) for key, value in v.get_dimensions().items() }, { "x": 0.789474, "y": 0.315789, "z": -0.526316 })

	def test_copy(self):
		"""
		Test copying
		"""

		v = Vector({ "x": 3 }, { "y": True })
		n = v.copy()

		self.assertEqual(v.get_attributes(), n.get_attributes())
		self.assertEqual(v.get_dimensions(), n.get_dimensions())

		v.set_attribute("y", False)
		self.assertFalse(v.get_attribute("y"))
		self.assertTrue(n.get_attribute("y"))
		v.set_attribute("y", True)

		v.set_dimension("x", 2)
		self.assertTrue(v.get_dimension("x") == 2)
		self.assertTrue(n.get_dimension("x") == 3)
		v.set_dimension("x", 3)

	def test_export(self):
		"""
		Test exporting and importing vectors.
		"""

		v = Vector({ "x": 3 }, { "y": True })
		e = v.to_array()
		self.assertEqual(v.get_attributes(), Vector.from_array(e).get_attributes())
		self.assertEqual(v.get_dimensions(), Vector.from_array(e).get_dimensions())
		self.assertEqual(v.__dict__, Vector.from_array(e).__dict__)
