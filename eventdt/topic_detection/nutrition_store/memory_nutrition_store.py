"""
Stores nutrition sets in memory.
"""

from .nutrition_store import NutritionStore

class MemoryNutritionStore(NutritionStore):
	"""
	Store the nutrition sets in memory as a dictionary.
	The timestamps are used as keys.
	The nutrition sets are the corresponding values.
	"""

	def __init__(self):
		"""
		Create the NutritionStore with the actual store.
		"""

		self._nutrition_store = {}

	def add_nutrition_set(self, timestamp, nutrition_set):
		"""
		Add a nutrition set to the store at the given timestamp.

		:param timestamp: The timestamp of the nutrition set.
		:type timestamp: int
		:param nutrition_set: The nutrition set to add.
		:type nutrition_set: mixed
		"""

		timestamp = int(timestamp)
		self._nutrition_store[timestamp] = nutrition_set

	def get_nutrition_set(self, timestamp):
		"""
		Get the nutrition set at the given timestamp.

		:param timestamp: The timestamp of the nutrition set.
		:type timestamp: int

		:return: The nutrition set at the given timestamp.
		:rtype: mixed
		"""

		timestamp = int(timestamp)
		return self._nutrition_store.get(timestamp, None)

	def get_all_nutrition_sets(self):
		"""
		Get all the nutrition sets.

		:return: All the nutrition sets in the nutrition store.
		:rtype: dict
		"""

		return self._nutrition_store

	def get_recent_nutrition_sets(self, sets, timestamp=None):
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

		timestamp = int(timestamp) if timestamp is not None else timestamp
		keys = sorted(self._nutrition_store.keys())[::-1] # get the keys and sort them in descending order
		keys = [ key for key in keys if key < timestamp ] if timestamp is not None else keys # filter them by timestamp
		keys = keys[:sets] if sets is not None else keys # only retain a subset

		nutrition_sets = [ self._nutrition_store[key] for key in keys ] # compile the nutrition sets
		return nutrition_sets

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

		start = int(start) if start is not None else start
		end = int(end) if end is not None else end
		keys = [ key for key in self._nutrition_store.keys() if key >= start and key < end ] # filter the nutrition sets by timestamp

		return { timestamp: self._nutrition_store[timestamp] for timestamp in keys }

	def remove_old_nutrition_sets(self, timestamp):
		"""
		Remove nutrition sets that are older than the given timestamp.

		:param timestamp: The timestamp before which no nutrition sets may exist.
		:type timestamp: int
		"""

		timestamp = int(timestamp)
		keys = sorted(self._nutrition_store.keys())[::-1] # get the keys and sort them in descending order
		self._nutrition_store = { key: self._nutrition_store[key] for key in keys if key >= timestamp } # compile the nutrition sets, filtering keys by timestamp to retain only recent ones
