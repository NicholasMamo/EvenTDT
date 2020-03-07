"""
Exportable objects are normal objects that can be exported as a JSON string and loaded back.
"""

from abc import ABC, abstractmethod
import re

class Exportable(ABC):
	"""
	An abstract class of an object that can be exported as a JSON string and imported back.
	"""

	@abstractmethod
	def to_array(self):
		"""
		Export the object as a dictionary.

		:return: The object as a dictionary.
		:rtype: dict
		"""

		pass

	@staticmethod
	@abstractmethod
	def from_array(array):
		"""
		Create an instance of the object from the given dictionary.

		:param array: The dictionary with the attributes to create the object instance.
		:type array: dict

		:return: A new instance of an object with the same attributes stored in the object.
		:rtype: object
		"""

		pass

	def _get_module(self, cls):
		"""
		Get the module name from the given path.

		:param cls: The full class name.
		:type cls: str

		:return: The module name.
		:rtype: str

		:raises ValueError: When the class name is invalid.
		"""

		class_pattern = re.compile('<class \'(.+)?\.?\'>')
		if not class_pattern.match(cls):
			raise ValueError(f"Invalid class name {cls}")

		path = class_pattern.findall(cls)[0].split('.')
		return '.'.join(path[:-1])

	def _get_class(self, cls):
		"""
		Get the class name from the given path.

		:param cls: The full class name.
		:type cls: str

		:return: The class name.
		:rtype: str

		:raises ValueError: When the class name is invalid.
		"""

		class_pattern = re.compile('<class \'(.+)?\.?\'>')
		if not class_pattern.match(cls):
			raise ValueError(f"Invalid class name {cls}")

		path = class_pattern.findall(cls)[0].split('.')
		return path[-1]
