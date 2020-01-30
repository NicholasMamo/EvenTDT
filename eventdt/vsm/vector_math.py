"""
Mathematical functions related to vectors.
"""

import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), "..")
if path not in sys.path:
    sys.path.append(path)

from vsm import vector

def magnitude(v):
	"""
	Get the magnitude of the given vector.

	:param v: The vector whose magnitude will be calculated.
	:type v: :class:`vector.vector.Vector`
	"""

	return math.sqrt(sum([value ** 2 for value in v.dimensions.values()]))

def normalize(v):
	"""
	Normalize the given vector.

	:param v: The vector that will be normalized.
	:type v: :class:`vector.vector.Vector`
	"""

	n = v.copy()

	m = magnitude(n)
	if m > 0:
		dimensions = n.dimensions
		dimensions = { dimension: float(value)/m for dimension, value in dimensions.items() }
		return vector.Vector(dimensions)
	else:
		return v

def augmented_normalize(v, a=0.5):
	"""
	Normalize the given vector using the formula: \

		f_j = a + (1 - a) f_j / x_j \

	where `x_j` is the highest `f_j` in the vector.

	:param v: The vector that will be normalized
	:type v: :class:`vector.vector.Vector`
	:param a: The minimum magnitude of each dimension.
	:type a: float
	"""

	n = v.copy()

	dimensions = n.dimensions
	x = max(dimensions.values()) if len(dimensions) > 0 else 1
	dimensions = { dimension: a + (1 - a) * value / x for dimension, value in dimensions.items() }
	n.set_dimensions(dimensions)
	return n

def concatenate(vectors):
	"""
	Concatenate a list of vectors and return a new vector.
	This means adding the dimensions together.

	:param vectors: A list of vectors
	:type vectors: list of :class:`vector.vector.Vector` instances

	:return: A single vector
	:rtype: :class:`vector.vector.Vector`
	"""

	concatenated = { }
	for v in vectors:
		for dimension in v.dimensions:
			concatenated[dimension] = concatenated.get(dimension, 0) + v.get_dimension(dimension)

	return vector.Vector(concatenated)

def euclidean(v1, v2):
	"""
	Compute similarity using Euclidean distance.

	:param v1: The first vector.
	:type v1: :class:`vector.vector.Vector`
	:param v2: The second vector.
	:type v2: :class:`vector.vector.Vector`
	"""

	dimensions = list(set(v1.dimensions.keys()).union(v2.dimensions.keys()))
	differences = [ (v1.get_dimension(dimension) - v2.get_dimension(dimension)) ** 2 for dimension in dimensions ]
	return math.sqrt(sum(differences))

def manhattan(v1, v2):
	"""
	Compute similarity using Manhattan distance.

	:param v1: The first vector.
	:type v1: :class:`vector.vector.Vector`
	:param v2: The second vector.
	:type v2: :class:`vector.vector.Vector`
	"""

	dimensions = list(set(v1.dimensions.keys()).union(v2.dimensions.keys()))
	differences = [ abs(v1.get_dimension(dimension) - v2.get_dimension(dimension)) for dimension in dimensions ]
	return sum(differences)

def cosine(v1, v2):
	"""
	Compute similarity using Cosine similarity.

	:param v1: The first vector.
	:type v1: :class:`vector.vector.Vector`
	:param v2: The second vector.
	:type v2: :class:`vector.vector.Vector`
	"""

	dimensions = list(set(v1.dimensions.keys()).intersection(v2.dimensions.keys()))
	products = [ v1.get_dimension(dimension) * v2.get_dimension(dimension) for dimension in dimensions ]
	if (magnitude(v1) > 0 and magnitude(v2) > 0):
		return sum(products) / (magnitude(v1) * magnitude(v2))
	else:
		return 0

def cosine_distance(v1, v2):
	"""
	Compute the Cosine distance:
		1 - cosine similarity.

	:param v1: The first vector.
	:type v1: :class:`vector.vector.Vector`
	:param v2: The second vector.
	:type v2: :class:`vector.vector.Vector`
	"""

	return 1 - cosine(v1, v2)
