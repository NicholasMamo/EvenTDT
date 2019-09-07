"""
Run unit tests on vector mathematics
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

class TestVectorMath(unittest.TestCase):
	"""
	Test the vector math functions
	"""

	def test_normalization(self):
		"""
		Test the normalization method
		"""

		v = Vector({ "x": 3, "y": 2, "z": 1 })
		self.assertEqual(magnitude(v), math.sqrt(14))

		self.assertEqual(normalize(v).get_dimensions(), {"x": 3./math.sqrt(14), "y": math.sqrt(4./14), "z": math.sqrt(1./14)})

		v = Vector({ })
		self.assertEqual(normalize(v).get_dimensions(), { })

	def test_augmented_normalization(self):
		"""
		Test the augmented normalization method
		"""

		v = Vector({ "x": 1, "y": 2, "z": 0 })
		self.assertEqual(augmented_normalize(v, 0.5).get_dimensions(), { "x": 0.75, "y": 1., "z": 0.5 })
		self.assertEqual({ dimension: round(value, 5) for dimension, value in augmented_normalize(v, 0.2).get_dimensions().items() }, { "x": 0.6, "y": 1, "z": 0.2 })
		self.assertEqual({ dimension: round(value, 5) for dimension, value in augmented_normalize(v, 0).get_dimensions().items() }, { "x": 0.5, "y": 1, "z": 0 })

		v = Vector({ })
		self.assertEqual(augmented_normalize(v).get_dimensions(), { })

	def test_concatenation(self):
		"""
		Test the concatenation function
		"""

		v = Vector()
		self.assertEqual(concatenate([v]).get_dimensions(), {})

		vectors = [
			Vector({ "a": 1, "b": 2, "c": 3 }),
			Vector({ "c": 2, "d": 1 })
		]
		self.assertEqual(concatenate(vectors).get_dimensions(), { "a": 1, "b": 2, "c": 5, "d": 1 })

	def test_euclidean(self):
		"""
		Test the Euclidean distance
		"""

		v1, v2 = Vector({"x": -1, "y": 2, "z": 3}), Vector({"x": 4, "z": -3})
		self.assertEqual(euclidean(v1, v2), math.sqrt(65))

		self.assertEqual(euclidean(v1, v1), 0)

	def test_manhattan(self):
		"""
		Test the Manhattan distance
		"""

		v1, v2 = Vector({"x": -1, "y": 2, "z": 3}), Vector({"x": 4, "z": -3})
		self.assertEqual(manhattan(v1, v2), 13)

		self.assertEqual(manhattan(v1, v1), 0)

	def test_cosine(self):
		"""
		Test the cosine similarity and distance
		"""

		v1, v2 = Vector({"x": 1/3.74, "y": 2/3.74, "z": 3/3.74}), Vector({"x": 4/8.77, "y": -5/8.77, "z": 6/8.77})
		self.assertEqual(round(cosine(v1, v2), 2), 0.37)

		# same vector
		self.assertEqual(cosine(v1, v1), 1)

		# opposite
		v1, v2 = Vector({"x": 1/3.74, "y": 2/3.74, "z": 3/3.74}), Vector({"x": -1/3.74, "y": -2/3.74, "z": -3/3.74})
		self.assertEqual(cosine(v1, v2), -1)

		# orthogonal
		v1, v2 = Vector({"x": 2, "y": 4}), Vector({"x": -2, "y": 1})
		self.assertEqual(cosine(v1, v2), 0)

		v1, v2 = Vector({"x": 1/3.74, "y": 2/3.74, "z": 3/3.74}), Vector({"x": 4/8.77, "y": -5/8.77, "z": 6/8.77})
		self.assertEqual(round(cosine_distance(v1, v2), 2), 1 - 0.37)

# unittest.main()
