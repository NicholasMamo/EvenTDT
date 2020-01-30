"""
An interface of nutrition stores, describing the list of methods that they must implement.
This can be implemented to store data in a database, for example, or in memory.

Although the specification assumes a dict type for nutrition sets, the nutrition store should be flexible.
This would allow for narrower or newer definitions of nutrition, including volume - an integer.
"""

from abc import ABC, abstractmethod

class NutritionStore(ABC):
	"""
	An interface of NutritionStore objects.

	This class assumes that the nutrition store is stored in a variable called `_nutrition_store.`
	"""

	@abstractmethod
	def __init__(self):
		"""
		Create the NutritionStore with the actual store.
		"""

		pass

	@abstractmethod
	def add_nutrition_set(self, timestamp, nutrition_set):
		"""
		Add a nutrition set to the store at the given timestamp.

		:param timestamp: The timestamp of the nutrition set.
		:type timestamp: int
		:param nutrition_set: The nutrition set to add.
		:type nutrition_set: mixed
		"""

		pass

	@abstractmethod
	def get_nutrition_set(self, timestmap):
		"""
		Get the nutrition set at the given timestamp.

		:param timestamp: The timestamp of the nutrition set.
		:type timestamp: int

		:return: The nutrition set at the given timestamp.
		:rtype: mixed
		"""

		pass

	@abstractmethod
	def get_all_nutrition_sets(self):
		"""
		Get all the nutrition sets.

		:return: All the nutrition sets in the nutrition store.
		:rtype: dict
		"""

		pass

	@abstractmethod
	def get_recent_nutrition_sets(self, sets=None, timestamp=None):
		"""
		Get a list of nutrition sets.
		Start from the given timestamp and work backwards.
		If no timestamp is given, start from the most recent.
		Return a list of nutrition sets in reverse chronological order.

		:param sets: The number of nutrition sets to return.
		:type sets: int
		:param timestamp: The timestamp before which all the returned nutrition sets should be.
		:type timestamp: int

		:return: The recent nutrition sets.
		:rtype: list
		"""

		pass

	@abstractmethod
	def between(self, start, end):
		"""
		Get a list of nutrition sets that are between the given timestamps.
		The start timestamp is inclusive, the end timestamp is exclusive.

		:param start: The first timestamp that should be included in the returned nutrition sets.
			If no time window with the given timestamp exists, all returned time windows succeed it.
		:type start: int
		:param end: The timestamp that should be higher than all returned nutrition sets.
		:type end: int

		:return: All the nutrition sets that are between the given timestamps.
		;rtype: dict
		"""

		pass

	def since(self, start):
		"""
		Get a list of nutrition sets since the given timestamp.
		The start timestamp is inclusive.

		:param start: The first timestamp that should be included in the returned nutrition sets.
			If no time window with the given timestamp exists, all returned time windows succeed it.
		:type start: int

		:return: All the nutrition that happened on or after the given timestamp.
		:rtype: dict
		"""

		max_timestamp = int(max(list(self._nutrition_store.keys())))
		return self.between(start, max_timestamp + 1)

	def before(self, end):
		"""
		Get a list of nutrition sets that came before the given timestamp.
		The end timestamp is exclusive.

		:param end: The timestamp that should be higher than all returned nutrition sets.
		:type end: int

		:return: All the nutrition sets that came before the given timestamp.
		:rtype dict
		"""

		return self.between(0, end)

	@abstractmethod
	def remove_old_nutrition_sets(self, timestamp):
		"""
		Remove nutrition sets that are older than the given timestamp.

		:param timestamp: The timestamp before which no nutrition sets may exist.
		:type timestamp: int
		"""

		pass
