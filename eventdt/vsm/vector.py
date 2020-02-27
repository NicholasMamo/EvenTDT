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

class Vector(Attributable):
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
		self.dimensions = VectorSpace() if dimensions is None else VectorSpace(dimensions)

	def normalize(self):
		"""
		Normalize the vector.
		"""

		self.dimensions = vector_math.normalize(self).dimensions

	def copy(self):
		"""
		Create a copy of the vector.

		:return: A copy of the :class:`~vsm.vector.Vector` object
		:rtype: :class:`~vector.vector.Vector`
		"""

		return Vector(self.dimensions.copy(), self._attributes.copy())

	def to_array(self):
		"""
		Export the vector as an associative array.

		:return: The vector as an associative array.
		:rtype: dict
		"""

		array = Attributable.to_array(self)
		array.update({
			"dimensions": self.dimensions,
		})
		return array

	@staticmethod
	def from_array(array):
		"""
		Create an instance of the vector from the given associative array.

		:param array: The associative array with the attributes to create the vector.
		:type array: dict

		:return: A new instance of an object with the same attributes stored in the object.
		:rtype: :class:`~vector.vector.Vector`
		"""

		return Vector(attributes=array.get("attributes", {}), dimensions=array.get("dimensions", {}))
