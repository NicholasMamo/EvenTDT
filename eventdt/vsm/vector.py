"""
The :class:`~vsm.vector.Vector` is the basis of the Vector Space Model (VSM).
The class contains is used in clustering and Natural Language Processing (NLP) to represent documents.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), "..")
if path not in sys.path:
    sys.path.append(path)

from objects.attributable import Attributable
from objects.exportable import Exportable
from vsm import vector_math

class VectorSpace(dict):
	"""
	The vector space is the space of all dimensions.
	This class is based on a normal dictionary.
	The only thing that changes is that when a non-existent dimension is requested, a value of 0 is returned.
	"""

	def __getitem__(self, key):
		"""
		Get the dimension represented by the given key.
		If the dimension does not exist, 0 is returned instead.

		:param key: The name of the dimension whose value will be fetched.
		:type key: str

		:return: The magnitude of the dimension, or 0 if it does not exist.
		:rtype: float
		"""

		return self.get(key, 0)

class Vector(Attributable, Exportable):
	"""
	The :class:`~vsm.vector.Vector` class is the smallest building block in the Vector Space Model (VSM).
	It is used for tasks such as clustering and to represent documents.
	Vectors are based on :class:`~objects.Attributable` so that they may have additional properties.

	:ivar dimensions: The dimensions—name-value pairs—of the vector.
	:vartype dimensions: dict
	"""

	def __init__(self, dimensions=None, *args, **kwargs):
		"""
		By default, the :class:`~vsm.vector.Vector` object has no dimensions.
		The :class:`~vsm.vector.Vector` object is represented using an associative array (dictionary).
		Any additional attributes can be passed as arguments or keyword arguments.

		:param dimensions: The initial dimensions of the :class:`~vsm.vector.Vector` object.
			If none are given, they are initialized to an empty dict.
		:type dimensions: dict
		"""

		super(Vector, self).__init__(*args, **kwargs)
		self.dimensions = dimensions

	@property
	def dimensions(self):
		"""
		Get the dimensions of the vector.

		:return: The dimensions of the vector.
		:rtype: :class:`~vsm.vector.VectorSpace`
		"""

		return self.__dimensions

	@dimensions.setter
	def dimensions(self, dimensions=None):
		"""
		Reset the list of dimensions.
		If a dictionary is given, its keys are used as the new dimensions.
		Otherwise, a new vector space is initialized.

		:param dimensions: The new dimensions as a dictionary.
						   If `None` is given, an empty vector space is initialized instead.
		:type dimensions: dict or `None`
		"""

		self.__dimensions = VectorSpace() if dimensions is None else VectorSpace(dimensions)

	def normalize(self):
		"""
		Normalize the vector.
		"""

		self.dimensions = vector_math.normalize(self).dimensions

	def copy(self):
		"""
		Create a copy of the vector.

		:return: A copy of the :class:`~vsm.vector.Vector` object
		:rtype: :class:`~vsm.vector.Vector`
		"""

		return Vector(self.dimensions.copy(), self.attributes.copy())

	def to_array(self):
		"""
		Export the vector as an associative array.

		:return: The vector as an associative array.
		:rtype: dict
		"""

		return {
			'class': str(Vector),
			'attributes': self.attributes,
			'dimensions': self.dimensions,
		}

	@staticmethod
	def from_array(array):
		"""
		Create an instance of the vector from the given associative array.

		:param array: The associative array with the attributes to create the vector.
		:type array: dict

		:return: A new instance of the vector with the same attributes stored in the object.
		:rtype: :class:`~vsm.vector.Vector`
		"""

		return Vector(dimensions=array.get('dimensions'), attributes=array.get('attributes'))
