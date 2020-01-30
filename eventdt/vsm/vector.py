"""
The :class:`vsm.vector.Vector` class is used in clustering and other applications that adopt the Vector Space Model.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), "../")
if path not in sys.path:
    sys.path.append(path)

from objects.attributable import Attributable
from objects.exportable import Exportable
from . import vector_math

class Vector(Attributable):
	"""
	The :class:`vsm.vector.Vector` class is the smallest building block in the Vector Space Model.
	It is used for tasks such as clustering and to represent documents.
	Vectors are based on :class:`objects.Attributable` so that they may have additional properties.

	:ivar _dimensions: The dimensions—name-value pairs—of the Vector.
	:vartype _dimensions: dict
	"""

	def __init__(self, dimensions=None, attributes=None):
		"""
		By default, the :class:`vsm.vector.Vector` object has no dimensions.
		The :class:`vsm.vector.Vector` object is represented using an associative array (dictionary).

		:param dimensions: The initial dimensions of the :class:`vsm.vector.Vector` object.
			If none are given, they are initialized to an empty dict.
		:type dimensions: dict
		:param attributes: The list of attributes of the :class:`vsm.vector.Vector` object.
		:type attributes: dict
		"""

		super(Vector, self).__init__(attributes)
		self._dimensions = dict() if dimensions is None else dimensions

	def initialize_dimension(self, name, value):
		"""
		Initialize an dimension's value if it does not eixst.

		:param name: The dimension's name.
		:type name: :class:`object`
		:param value: The default value for the dimension, assigned if a value does not already exist.
		:type value: :class:`object`
		"""

		self._dimensions[name] = self._dimensions.get(name, value)

	def set_dimensions(self, dimensions=None):
		"""
		Overwrite the dimensions, clearing them if nothing is given.

		:param dimensions: The new set of dimensions.
		:type dimensions: dict
		"""

		self._dimensions = dict() if dimensions is None else dimensions

	def set_dimension(self, name, value=None):
		"""
		Set a single dimension.
		If no value is provided, the dimension is unset.

		:param name: The dimension's name.
		:type name: :class:`object`
		:param value: The default value for the dimension, assigned if a value does not already exist.
		:type value: :class:`object`
		"""

		if value:
			self._dimensions[name] = value
		else:
			if name in self._dimensions:
				del self._dimensions[name]

	def get_dimension(self, name):
		"""
		Get the value of a single dimension.

		:param name: The dimension's name.
		:type name: :class:`object`
		"""

		return self._dimensions.get(name, 0)

	def get_dimensions(self):
		"""
		Get all the dimensions.

		:return: The dimensions dict.
		:type: dict
		"""

		return self._dimensions

	def clear_dimension(self, name):
		"""
		Remove a single dimension.

		:param name: The name of the dimension too remove.
		:type name: :class:`object`
		"""

		self.set_dimension(name)

	def clear_dimensions(self):
		"""
		Remove all dimensions.
		"""

		self.set_dimensions()

	def normalize(self):
		"""
		Normalize the vector.
		"""
		self._dimensions = vector_math.normalize(self).get_dimensions()

	def copy(self):
		"""
		Create a copy of the vector.

		:return: A copy of the :class:`vsm.vector.Vector` object
		:rtype: :class:`vector.vector.Vector`
		"""

		return Vector(self._dimensions.copy(), self._attributes.copy())

	def to_array(self):
		"""
		Export the vector as an associative array.

		:return: The vector as an associative array.
		:rtype: dict
		"""

		array = Attributable.to_array(self)
		array.update({
			"dimensions": self._dimensions,
		})
		return array

	@staticmethod
	def from_array(array):
		"""
		Create an instance of the vector from the given associative array.

		:param array: The associative array with the attributes to create the vector.
		:type array: dict

		:return: A new instance of an object with the same attributes stored in the object.
		:rtype: :class:`vector.vector.Vector`
		"""

		return Vector(attributes=array.get("attributes", {}), dimensions=array.get("dimensions", {}))
