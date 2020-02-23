"""
An attributable object is a normal object, but it contains a list of attributes.
"""

from .exportable import Exportable

class Attributable(object):
	"""
	The Attributable class defines an attribute store and helper functions.

	:ivar _attributes: The key-value attributes associated with the object.
	:vartype _attributes: dict
	"""

	def __init__(self, attributes=None):
		"""
		Create the list of attributes.
		If none are provided, an empty attribute dict is created.

		:param attributes: The starting set of attributes.
		:type attributes: dict
		"""

		self._attributes = dict() if attributes is None else attributes

	def initialize_attribute(self, name, value):
		"""
		Initialize an attribute's value if it does not eixst.

		:param name: The attribute's name.
		:type name: :class:`~object`
		:param value: The default value for the attribute, assigned if a value does not already exist.
		:type value: :class:`~object`
		"""

		self._attributes[name] = self._attributes.get(name, value)

	def set_attributes(self, attributes=None):
		"""
		Overwrite the attributes, clearing them if nothing is given.

		:param attributes: The new set of attributes.
		:type attributes: dict
		"""
		self._attributes = dict() if attributes is None else attributes

	def set_attribute(self, name, value=None):
		"""
		Set a single attribute.
		If no value is provided, the attribute is unset.

		:param name: The attribute's name.
		:type name: :class:`~object`
		:param value: The default value for the attribute, assigned if a value does not already exist.
		:type value: :class:`~object`
		"""
		if value is not None:
			self._attributes[name] = value
		else:
			if name in self._attributes:
				del self._attributes[name]

	def get_attribute(self, name, default=None):
		"""
		Get the value of a single attribute.

		:param name: The attribute's name.
		:type name: :class:`~object`
		:param default: The default value for the attribute, returned if no value is set yet.
		:type default: :class:`~object`
		"""
		return self._attributes.get(name, default)

	def get_attributes(self):
		"""
		Get all the attributes.

		:return: The attributes dict.
		:type: dict
		"""
		return self._attributes

	def clear_attribute(self, name):
		"""
		Remove a single attribute.

		:param name: The name of the attribute too remove.
		:type name: :class:`~object`
		"""
		self.set_attribute(name)

	def clear_attributes(self):
		"""
		Remove all attributes.
		"""
		self.set_attributes()

	def to_array(self):
		"""
		Export the attributable object as an associative array.

		:return: The attributable object as an associative array.
		:rtype: dict
		"""

		return { "attributes": self._attributes }

	@staticmethod
	def from_array(array):
		"""
		Create an instance of the attributable object from the given associative array.

		:param array: The associative array with the attributes to create the :class:`~objects.attributable.Attributable` instance.
		:type array: dict

		:return: A new instance of an object with the same attributes stored in the object.
		:rtype: :class:`~objects.attributable.Attributable`
		"""

		return Attributable(attributes=array.get("attributes", {}))
