"""
Clusters are used in conjunction with :class:`eventdt.vsm.vector.Vector` instances to group them together.
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
from vsm import vector_math

class Cluster(Attributable):
	"""
	The cluster class is a collection of vectors, or documents.
	It also has a centroid.
	Clusters are based on :class:`objects.Attributable` so that they may have additional properties.

	:ivar vectors: The list of vectors that make up the cluster.
	:vartype vectors: list of :class:`eventdt.vsm.vector.Vector` instances instances
	:ivar centroid: The centroid of the cluster, representing the average vector.
	:vartype centroid: :class:`eventdt.vsm.vector.Vector` instances
	"""

	def __init__(self, vectors=None):
		"""
		Initiate the cluster with an empty centroid and a list of vectors.

		:param vectors: An initial list of vectors, or a single vector.
						If `None` is given, an empty list is initialized instead.
		:type vectors: list of :class:`eventdt.vsm.vector.Vector` or :class:`eventdt.vsm.vector.Vector`
		"""

		super(Cluster, self).__init__()
		if type(vectors) is not list and vectors is not None:
			self.set_vectors([ vectors ])
		else:
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
		:type vector: :class:`eventdt.vsm.vector.Vector` instances
		"""

		self.vectors.append(vector)
		vectors = len(self.vectors)
		dimensions = vector.get_dimensions().keys() | self.centroid.get_dimensions().keys()

		"""
		Update the cluster's centroid incrimentally.
		"""
		for dimension in dimensions:
			new_weight = (self.centroid.get_dimension(dimension) * (vectors - 1) + vector.get_dimension(dimension)) / vectors
			self.centroid.set_dimension(dimension, new_weight)

	def recalculate_centroid(self):
		"""
		Recalculate the centroid.
		This is important if, for example, one of the vector instances change in memory.
		"""

		self.centroid = Vector()
		old_vectors = list(self.vectors) # make a copy of the Vectors
		self.vectors = [] # remove all Vectors
		for vector in old_vectors:
			self.add_vector(vector)

	def remove_vector(self, vector):
		"""
		Remove a vector from the cluster.

		:param vector: The vector to remove from the cluster.
		:type vector: :class:`eventdt.vsm.vector.Vector` instances
		"""

		self.vectors.remove(vector)
		vectors = len(self.vectors)
		copy = vector.get_dimensions().copy()
		dimensions = list(self.centroid.get_dimensions().keys())

		"""
		Update the cluster's centroid incrimentally
		"""
		for dimension in dimensions:
			value = self.centroid.get_dimension(dimension)
			new_value = (value * (vectors + 1) - copy[dimension]) / max(vectors, 1)
			self.centroid.set_dimension(dimension, new_value)

	def similarity(self, vector, similarity_measure=vector_math.cosine):
		"""
		Calculate the similarity between the given vector and this cluster's centroid.

		:param vector: The vector that will be compared with the centroid.
		:type vector: :class:`eventdt.vsm.vector.Vector` instances
		:param similarity_measure: The similarity function to use to compare the likeliness of the vector with the cluster.
		:type similarity_measure: function

		:return: The similarity between the cluster and the vector.
		:rtype: float
		"""

		return similarity_measure(self.centroid, vector)

	# TODO: Needs to become a property
	def set_vectors(self, vectors=None):
		"""
		Reset the list of vectors.

		:param vectors: The new list of vectors.
			If none are given, an empty list is initialized instead.
		:type vectors: list of :class:`eventdt.vsm.vector.Vector` instances instances
		"""

		vectors = list() if vectors is None else vectors
		self.centroid = Vector()
		self.vectors = []
		for vector in vectors:
			self.add_vector(vector)

	def get_representative_vectors(self, vectors=1, similarity_measure=vector_math.cosine):
		"""
		Get the vectors that are closest to the centroid.
		If the number of vectors that is sought is one, only the vector is returned.
		Otherwise, a list of vectors is returned.

		:param vectors: The number of vectors the fetch.
		:type vectors: int
		:param similarity_measure: The similarity function to use to compare the likeliness of the vector with the cluster.
		:type similarity_measure: function

		:return: The representative vectors.
		:rtype: :class:`eventdt.vsm.vector.Vector` instances or list of :class:`eventdt.vsm.vector.Vector` instances instances
		"""

		similarities = [ self.similarity(vector, similarity_measure) for vector in self.vectors ] # calculate the similarities
		similarities = zip(self.vectors, similarities) # combine the similarities with the vectors
		similarities = sorted(similarities, key=lambda x:x[1])[::-1] # sort the vectors in descending order of similarity

		"""
		If only one vector is needed, just return the vector, not a list of vectors.
		Otherwise return a list.
		"""
		if (vectors == 1):
			return similarities[0][0]
		else:
			return [ similarities[i][0] for i in range(0, vectors) ]

	def get_intra_similarity(self, similarity_measure=vector_math.cosine):
		"""
		Get the average similarity between vectors and the cluster.

		:param similarity_measure: The similarity function to use to compare the likeliness of the vector with the cluster.
		:type similarity_measure: function

		:return: The average intra-similarity of the cluster.
		:rtype: float
		"""
		similarities = [ self.similarity(vector, similarity_measure) for vector in self.vectors ] # calculate the similarities
		return sum(similarities)/len(similarities)

	def size(self):
		"""
		Get the number of vectors in the cluster.

		:return: The number of vectors in the cluster.
		:rtype: int
		"""

		return len(self.vectors)

	def to_array(self):
		"""
		Export the cluster as an associative array.
		The centroid is not included as it is calculated upon instantiation.

		:return: The cluster as an associative array.
		:rtype: dict
		"""

		array = Attributable.to_array(self)
		array.update({
			"vectors": [ vector.to_array() for vector in self.vectors ]
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
