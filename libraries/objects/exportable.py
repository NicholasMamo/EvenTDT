"""
An exportable object can be exported as a JSON string and loaded back.
"""

from abc import ABC, abstractmethod

class Exportable(ABC):
	"""
	An abstract class of an object that can be exported as a JSON string, and imported back.
	The representation returns an associative array.
	"""

	@abstractmethod
	def to_array(self):
		"""
		Export the object as an associative array.

		:return: The object as an associative array.
		:rtype: dict
		"""

		pass

	@staticmethod
	@abstractmethod
	def from_array(array):
		"""
		Create an instance of the object from the given associative array.

		:param array: The associative array with the attributes to create the object instance.
		:type array: dict

		:return: A new instance of an object with the same attributes stored in the object.
		:rtype: object
		"""

		pass
