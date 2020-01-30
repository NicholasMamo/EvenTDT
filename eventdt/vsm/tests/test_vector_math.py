"""
Run unit tests on vector mathematics
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

class TestVectorMath(unittest.TestCase):
	"""
	Test the vector math functions.
	"""

	def test_normalization(self):
		"""
		Test the normalization method.
		"""

		v = Vector({ "x": 3, "y": 2, "z": 1 })
		self.assertEqual(math.sqrt(14), magnitude(v))

		self.assertEqual({"x": 3./math.sqrt(14), "y": math.sqrt(4./14), "z": math.sqrt(1./14)}, normalize(v).get_dimensions())

		v = Vector({ })
		self.assertEqual({ }, normalize(v).get_dimensions())

	def test_augmented_normalization(self):
		"""
		Test the augmented normalization method.
		"""

		v = Vector({ "x": 1, "y": 2, "z": 0 })
		self.assertEqual({ "x": 0.75, "y": 1., "z": 0.5 }, augmented_normalize(v, 0.5).get_dimensions())
		self.assertEqual({ "x": 0.6, "y": 1, "z": 0.2 }, { dimension: round(value, 5) for dimension, value in augmented_normalize(v, 0.2).get_dimensions().items() })
		self.assertEqual({ "x": 0.5, "y": 1, "z": 0 }, { dimension: round(value, 5) for dimension, value in augmented_normalize(v, 0).get_dimensions().items() })

		v = Vector({ })
		self.assertEqual(augmented_normalize(v).get_dimensions(), { })

	def test_concatenation(self):
		"""
		Test the concatenation function.
		"""

		v = Vector()
		self.assertEqual({}, concatenate([v]).get_dimensions())

		vectors = [
			Vector({ "a": 1, "b": 2, "c": 3 }),
			Vector({ "c": 2, "d": 1 })
		]
		self.assertEqual({ "a": 1, "b": 2, "c": 5, "d": 1 }, concatenate(vectors).get_dimensions())

	def test_euclidean(self):
		"""
		Test the Euclidean distance.
		"""

		v1, v2 = Vector({"x": -1, "y": 2, "z": 3}), Vector({"x": 4, "z": -3})
		self.assertEqual(math.sqrt(65), euclidean(v1, v2))

		self.assertEqual(0, euclidean(v1, v1))

	def test_manhattan(self):
		"""
		Test the Manhattan distance.
		"""

		v1, v2 = Vector({"x": -1, "y": 2, "z": 3}), Vector({"x": 4, "z": -3})
		self.assertEqual(13, manhattan(v1, v2))

		self.assertEqual(0, manhattan(v1, v1))

	def test_cosine(self):
		"""
		Test the cosine similarity and distance.
		"""

		v1, v2 = Vector({"x": 1/3.74, "y": 2/3.74, "z": 3/3.74}), Vector({"x": 4/8.77, "y": -5/8.77, "z": 6/8.77})
		self.assertEqual(0.37, round(cosine(v1, v2), 2))

		# same vector
		self.assertEqual(1, cosine(v1, v1))

		# opposite
		v1, v2 = Vector({"x": 1/3.74, "y": 2/3.74, "z": 3/3.74}), Vector({"x": -1/3.74, "y": -2/3.74, "z": -3/3.74})
		self.assertEqual(-1, cosine(v1, v2))

		# orthogonal
		v1, v2 = Vector({"x": 2, "y": 4}), Vector({"x": -2, "y": 1})
		self.assertEqual(0, cosine(v1, v2))

		v1, v2 = Vector({"x": 1/3.74, "y": 2/3.74, "z": 3/3.74}), Vector({"x": 4/8.77, "y": -5/8.77, "z": 6/8.77})
		self.assertEqual(1 - 0.37, round(cosine_distance(v1, v2), 2))
