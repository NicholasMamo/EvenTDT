"""
A cluster is a group of :class:`~vsm.vector.Vector` instances, or other classes that inherit from the :class:`~vsm.vector.Vector` class.
The purpose of clusters is that they represent a single topic.
To achieve this goal, good clusters:

1. Have a high distance between them if they (or, their instances) represent different topics, and
2. Have a small distance between their own :class:`~vsm.vector.Vector` instances.

Although you can create a :class:`~vsm.cluster.Cluster` instance yourself, it is more common to generate clusters automatically using a :class:`~vsm.clustering.algorithms.clustering.ClusteringAlgorithm`.
"""

import importlib
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from objects.attributable import Attributable
from objects.exportable import Exportable

from vsm import Vector, vector_math

class Cluster(Attributable, Exportable):
	"""
	The cluster class is a collection of vectors, or documents.
	It also has a centroid.
	Clusters are based on :class:`~objects.Attributable` so that they may have additional properties.

	:ivar vectors: The list of vectors that make up the cluster.
	:vartype vectors: list of :class:`~vsm.vector.Vector`
	:ivar centroid: The centroid of the cluster, representing the average vector.
	:vartype centroid: :class:`~vsm.vector.Vector`
	"""

	def __init__(self, vectors=None, *args, **kwargs):
		"""
		Initialize the cluster with an empty centroid and a list of vectors.

		:param vectors: An initial list of vectors, or a single vector.
						If `None` is given, an empty list is initialized instead.
		:type vectors: list of :class:`~vsm.vector.Vector` or :class:`~vsm.vector.Vector` or `None`
		"""

		super(Cluster, self).__init__(*args, **kwargs)
		self.vectors = vectors
		self.centroid = Vector()

	def similarity(self, vector, similarity_measure=vector_math.cosine):
		"""
		Calculate the similarity between the given vector and this cluster's centroid.

		:param vector: The vector that will be compared with the centroid.
		:type vector: :class:`~vsm.vector.Vector`
		:param similarity_measure: The similarity function to use to compare the likeliness of the vector with the cluster.
		:type similarity_measure: func

		:return: The similarity between the cluster and the vector.
		:rtype: float
		"""

		return similarity_measure(self.centroid, vector)

	def recalculate_centroid(self):
		"""
		Recalculate the centroid.
		"""

		dimensions = set([ dimension for vector in self.vectors
									 for dimension in vector.dimensions ])

		for dimension in dimensions:
			weight = sum([ vector.dimensions[dimension] for vector in self.vectors ])
			self.__centroid.dimensions[dimension] = weight/len(self.vectors)

		self.__centroid.normalize()

	@property
	def centroid(self):
		"""
		Get the cluster's centroid.

		:return: The cluster's centroid.
		:rtype: :class:`~vsm.vector.Vector`
		"""

		self.recalculate_centroid()
		return self.__centroid

	@centroid.setter
	def centroid(self, centroid):
		"""
		Override the centroid.

		:param centroid: The new centroid.
		:type centroid: :class:`~vsm.vector.Vector`
		"""

		self.__centroid = centroid

	@property
	def vectors(self):
		"""
		Get the list of vectors in the cluster.

		:return: The list of vectors in the cluster.
		:rtype: list of :class:`~vsm.vector.Vector`
		"""

		return self.__vectors

	@vectors.setter
	def vectors(self, vectors=None):
		"""
		Override the vectors.

		:param vectors: The new vectors.
		:type vectors: list of :class:`~vsm.vector.Vector` or :class:`~vsm.vector.Vector` or None
		"""

		if vectors is None:
			self.__vectors = [ ]
		elif type(vectors) is list:
			self.__vectors = list(vectors)
		else:
			self.__vectors = [ vectors ]

	def get_representative_vectors(self, vectors=1, similarity_measure=vector_math.cosine):
		"""
		Get the vectors that are closest to the centroid.
		If the number of vectors that is sought is one, only the vector is returned.
		Otherwise, a list of vectors is returned.

		:param vectors: The number of vectors the fetch.
		:type vectors: int
		:param similarity_measure: The similarity function to use to compare the likeliness of the vector with the cluster.
		:type similarity_measure: func

		:return: The representative vectors.
		:rtype: :class:`~vsm.vector.Vector` or list of :class:`~vsm.vector.Vector`
		"""

		"""
		First calculate all the similarities between the centroid and each vector in the cluster.
		Then, rank all vectors by their similarity score.
		"""

		similarities = [ self.similarity(vector, similarity_measure) for vector in self.vectors ]
		similarities = zip(self.vectors, similarities)
		similarities = sorted(similarities, key=lambda x:x[1])[::-1]

		"""
		If only one vector is needed, just return the vector, not a list of vectors.
		Otherwise return a list.
		"""
		if vectors == 1:
			return similarities[0][0] if len(similarities) else None
		else:
			similarities = similarities[:vectors]
			return [ similarity[0] for similarity in similarities ]

	def get_intra_similarity(self, similarity_measure=vector_math.cosine):
		"""
		Get the average similarity between vectors and the cluster.

		:param similarity_measure: The similarity function to use to compare the likeliness of the vector with the cluster.
		:type similarity_measure: func

		:return: The average intra-similarity of the cluster.
		:rtype: float
		"""

		if self.vectors:
			similarities = [ self.similarity(vector, similarity_measure) for vector in self.vectors ] # calculate the similarities
			return sum(similarities)/len(similarities)

		return 0

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

		return {
			'class': str(Cluster),
			'attributes': self.attributes,
			'vectors': [ vector.to_array() for vector in self.vectors ]
		}

	@staticmethod
	def from_array(array):
		"""
		Create an instance of the cluster from the given associative array.

		:param array: The associative array with the attributes to create the cluster.
		:type array: dict

		:return: A new instance of an object with the same attributes stored in the object.
		:rtype: :class:`~vsm.cluster.cluster.Cluster`
		"""

		vectors = [ ]
		for vector in array.get('vectors'):
			module = importlib.import_module(Exportable.get_module(vector.get('class')))
			cls = getattr(module, Exportable.get_class(vector.get('class')))
			vectors.append(cls.from_array(vector))

		return Cluster(vectors=vectors, attributes=array.get('attributes'))
