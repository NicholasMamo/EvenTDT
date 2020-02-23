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
	The magnitude is computed as:

	.. math::

		||v|| = \\sqrt{\\sum_{n=1}^{V} {v_n^2}}

	where :math:`v` is a vector having :math:`V` dimensions.

	:param v: The vector whose magnitude will be calculated.
	:type v: :class:`~vsm.vector.Vector`
	"""

	return math.sqrt(sum([value ** 2 for value in v.dimensions.values()]))

def normalize(v):
	"""
	Normalize the given vector.
	Normalization is computed as:

	.. math::

		f = \\frac{f}{||v||}

	where :math:`f` is a feature in vector :math:`v`.

	:param v: The vector that will be normalized.
	:type v: :class:`~vsm.vector.Vector`
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
	Normalize the given vector using the formula:

	.. math::

		f = a + (1 - a) \\frac{f}{x}

	where :math:`x` is the magnitude of the highest dimension :math:`f` in the vector.
	:math:`a` is the augmentation, between 0 and 1, inclusive.

	:param v: The vector that will be normalized
	:type v: :class:`~vsm.vector.Vector`
	:param a: The minimum magnitude of each dimension.
	:type a: float

	:raises ValueError: When the augmentation is not between 0 and 1
	"""

	if not 0 <= a <= 1:
		raise ValueError(f"The augmentation must be between 0 and 1 inclusive, {a} received")

	n = v.copy()

	dimensions = n.dimensions
	x = max(dimensions.values()) if len(dimensions) > 0 else 1
	dimensions = { dimension: a + (1 - a) * value / x for dimension, value in dimensions.items() }
	n.set_dimensions(dimensions)
	return n

def concatenate(vectors):
	"""
	Concatenate a list of vectors and return a new vector.
	This means adding the dimensions together:

	.. math::

		f = \\sum_{i=1}^{|V|}{f_i}

	where :math:`f` is the weight of the concatenated vector, and :math:`f_i` is the weight of the same feature `f` in each vector in the set :math:`V`.

	:param vectors: A list of vectors
	:type vectors: list of :class:`~vsm.vector.Vector` instances

	:return: A single vector
	:rtype: :class:`~vsm.vector.Vector`
	"""

	concatenated = { }
	for v in vectors:
		for dimension in v.dimensions:
			concatenated[dimension] = concatenated.get(dimension, 0) + v.get_dimension(dimension)

	return vector.Vector(concatenated)

def euclidean(v1, v2):
	"""
	Compute similarity using Euclidean distance.
	The Euclidean distance :math:`e_{p, q}` is computed as:

	.. math::

		e_{p, q} = \\sqrt{ \\sum_{i=1}^{n}{ (q_i - p_i)^2 } }

	Where :math:`q_i` is feature :math:`i` in vector :math:`q`, and :math:`p_i` is the same feature :math:`i` in vector :math:`p`.
	:math:`n` is the union of features in vectors :math:`q` and :math:`p`.

	:param v1: The first vector.
	:type v1: :class:`~vsm.vector.Vector`
	:param v2: The second vector.
	:type v2: :class:`~vsm.vector.Vector`
	"""

	dimensions = list(set(v1.dimensions.keys()).union(v2.dimensions.keys()))
	differences = [ (v1.get_dimension(dimension) - v2.get_dimension(dimension)) ** 2 for dimension in dimensions ]
	return math.sqrt(sum(differences))

def manhattan(v1, v2):
	"""
	Compute similarity using Manhattan distance.
	The Manhattan distance :math:`m_{p, q}` is computed as:

	.. math::

		m_{p, q} = \\sum_{i=1}^{n}{ |q_i - p_i| }

	Where :math:`q_i` is feature :math:`i` in vector :math:`q`, and :math:`p_i` is the same feature :math:`i` in vector :math:`p`.
	:math:`n` is the union of features in vectors :math:`q` and :math:`p`.

	:param v1: The first vector.
	:type v1: :class:`~vsm.vector.Vector`
	:param v2: The second vector.
	:type v2: :class:`~vsm.vector.Vector`
	"""

	dimensions = list(set(v1.dimensions.keys()).union(v2.dimensions.keys()))
	differences = [ abs(v1.get_dimension(dimension) - v2.get_dimension(dimension)) for dimension in dimensions ]
	return sum(differences)

def cosine(v1, v2):
	"""
	Compute similarity using cosine similarity.
	The cosine similarity :math:`cos_{p, q}` is computed as:

	.. math::

		cos_{p, q} = \\frac{\\sum_{i=1}^{n}{ q_i \\cdot p_i }}{ ||p|| + ||q|| }

	Where :math:`q_i` is feature :math:`i` in vector :math:`q`, and :math:`p_i` is the same feature :math:`i` in vector :math:`p`.
	:math:`n` is the intersection of features in vectors :math:`q` and :math:`p`.

	:param v1: The first vector.
	:type v1: :class:`~vsm.vector.Vector`
	:param v2: The second vector.
	:type v2: :class:`~vsm.vector.Vector`
	"""

	dimensions = list(set(v1.dimensions.keys()).intersection(v2.dimensions.keys()))
	products = [ v1.get_dimension(dimension) * v2.get_dimension(dimension) for dimension in dimensions ]
	if (magnitude(v1) > 0 and magnitude(v2) > 0):
		return sum(products) / (magnitude(v1) * magnitude(v2))
	else:
		return 0

def cosine_distance(v1, v2):
	"""
	Compute the cosine distance.
	The cosine distance :math:`cosd_{p, q}` is computed as:

	.. math::

		cosd_{p, q} = 1 - cos_{p, q}

	.. warning::

		The cosine distance is not a real distance metric.

	:param v1: The first vector.
	:type v1: :class:`~vsm.vector.Vector`
	:param v2: The second vector.
	:type v2: :class:`~vsm.vector.Vector`
	"""

	return 1 - cosine(v1, v2)
