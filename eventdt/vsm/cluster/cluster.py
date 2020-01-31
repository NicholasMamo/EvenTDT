"""
Clusters are used in conjunction with vectors, grouping them together.
Groups are meant to maximize distance between clusters of different subjects.
Simultaneously, they aim to minimize the distance between vectors in the same clusters.
"""

import importlib
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from objects.attributable import Attributable

from vsm.vector import Vector
from vsm.vector_math import *

class Cluster(Attributable):
	"""
	The cluster class is a collection of vectors, or documents.
	It also has a centroid.
	Clusters are based on :class:`objects.Attributable` so that they may have additional properties.

	:ivar _vectors: The list of vectors that make up the cluster.
	:vartype _vectors: list of :class:`vector.vector.Vector` instances
	:ivar _centroid: The centroid of the cluster, representing the average vector.
	:vartype _centroid: :class:`vector.vector.Vector`
	"""

	def __init__(self, vectors=None):
		"""
		Initiate the cluster with an empty centroid and a list of vectors.

		:param vectors: An initial list of vectors.
			If none are given, an empty list is initialized instead.
		:type vectors: list of :class:`vector.vector.Vector` instances
		"""

		super(Cluster, self).__init__()
		self.set_vectors(vectors)

	def add_vectors(self, vectors):
		"""
		Add the given vectors to the cluster.

		:param vectors: The vectors to add to the cluster.
		:type vectors: list
		"""

		for vector in vectors:
			self.add_vector(vector)

	def add_vector(self, vector):
		"""
		Add a vector to the cluster.

		:param vector: The vector to add to the cluster.
		:type vector: :class:`vector.vector.Vector`
		"""

		self._vectors.append(vector)
		vectors = len(self._vectors)
		dimensions = vector.get_dimensions().keys() | self._centroid.get_dimensions().keys()

		"""
		Update the cluster's centroid incrimentally.
		"""
		for dimension in dimensions:
			new_weight = (self._centroid.get_dimension(dimension) * (vectors - 1) + vector.get_dimension(dimension)) / vectors
			self._centroid.set_dimension(dimension, new_weight)

	def recalculate_centroid(self):
		"""
		Recalculate the centroid.
		This is important if, for example, one of the vector instances change in memory.
		"""

		self._centroid = Vector()
		old_vectors = list(self._vectors) # make a copy of the Vectors
		self._vectors = [] # remove all Vectors
		for vector in old_vectors:
			self.add_vector(vector)

	def remove_vector(self, vector):
		"""
		Remove a vector from the cluster.

		:param vector: The vector to remove from the cluster.
		:type vector: :class:`vector.vector.Vector`
		"""

		self._vectors.remove(vector)
		vectors = len(self._vectors)
		copy = vector.get_dimensions().copy()
		dimensions = list(self._centroid.get_dimensions().keys())

		"""
		Update the cluster's centroid incrimentally
		"""
		for dimension in dimensions:
			value = self._centroid.get_dimension(dimension)
			new_value = (value * (vectors + 1) - copy[dimension]) / max(vectors, 1)
			self._centroid.set_dimension(dimension, new_value)

	def similarity(self, vector, similarity_measure=cosine):
		"""
		Calculate the similarity between the given vector and this cluster's centroid.

		:param vector: The vector that will be compared with the centroid.
		:type vector: :class:`vector.vector.Vector`
		:param similarity_measure: The similarity function to use to compare the likeliness of the vector with the cluster.
		:type similarity_measure: function

		:return: The similarity between the cluster and the vector.
		:rtype: float
		"""

		return similarity_measure(self._centroid, vector)

	def set_vectors(self, vectors=None):
		"""
		Reset the list of vectors.

		:param vectors: The new list of vectors.
			If none are given, an empty list is initialized instead.
		:type vectors: list of :class:`vector.vector.Vector` instances
		"""

		vectors = list() if vectors is None else vectors
		self._centroid = Vector()
		self._vectors = []
		for vector in vectors:
			self.add_vector(vector)

	def get_vectors(self):
		"""
		Get the list of vectors in the cluster.

		:return: A list of vectors.
		:type vectors: list of :class:`vector.vector.Vector` instances
		"""

		return self._vectors

	def get_representative_vectors(self, vectors=1, similarity_measure=cosine):
		"""
		Get the vectors that are closest to the centroid.
		If the number of vectors that is sought is one, only the vector is returned.
		Otherwise, a list of vectors is returned.

		:param vectors: The number of vectors the fetch.
		:type vectors: int
		:param similarity_measure: The similarity function to use to compare the likeliness of the vector with the cluster.
		:type similarity_measure: function

		:return: The representative vectors.
		:rtype: :class:`vector.vector.Vector` or list of :class:`vector.vector.Vector` instances
		"""

		similarities = [ self.similarity(vector, similarity_measure) for vector in self._vectors ] # calculate the similarities
		similarities = zip(self._vectors, similarities) # combine the similarities with the vectors
		similarities = sorted(similarities, key=lambda x:x[1])[::-1] # sort the vectors in descending order of similarity

		"""
		If only one vector is needed, just return the vector, not a list of vectors.
		Otherwise return a list.
		"""
		if (vectors == 1):
			return similarities[0][0]
		else:
			return [ similarities[i][0] for i in range(0, vectors) ]

	def get_intra_similarity(self, similarity_measure=cosine):
		"""
		Get the average similarity between vectors and the cluster.

		:param similarity_measure: The similarity function to use to compare the likeliness of the vector with the cluster.
		:type similarity_measure: function

		:return: The average intra-similarity of the cluster.
		:rtype: float
		"""
		similarities = [ self.similarity(vector, similarity_measure) for vector in self._vectors ] # calculate the similarities
		return sum(similarities)/len(similarities)

	def size(self):
		"""
		Get the number of vectors in the cluster.

		:return: The number of vectors in the cluster.
		:rtype: int
		"""

		return len(self._vectors)

	def get_centroid(self):
		"""
		Get the cluster's centroid vector.

		:return: The centroid.
		:rtype: :class:`vector.vector.Vector`
		"""

		return self._centroid

	def to_array(self):
		"""
		Export the cluster as an associative array.
		The centroid is not included as it is calculated upon instantiation.

		:return: The cluster as an associative array.
		:rtype: dict
		"""

		array = Attributable.to_array(self)
		array.update({
			"vectors": [ vector.to_array() for vector in self._vectors ]
		})
		return array

	@staticmethod
	def from_array(array):
		"""
		Create an instance of the cluster from the given associative array.

		:param array: The associative array with the attributes to create the cluster.
		:type array: dict

		:return: A new instance of an object with the same attributes stored in the object.
		:rtype: :class:`vector.cluster.cluster.Cluster`
		"""

		vectors = array.get("vectors", [])
		loaded_vectors = []
		for vector in vectors:
			c = vector.get("class", "")
			c = c[c.index("'")+1:c.rindex("'")]
			module_name, class_name = c[:c.rindex(".")], c[c.rindex(".")+1:]
			module = importlib.import_module(module_name)
			c = getattr(module, class_name)
			loaded_vectors.append(c.from_array(vector))

		return Cluster(vectors=loaded_vectors)
