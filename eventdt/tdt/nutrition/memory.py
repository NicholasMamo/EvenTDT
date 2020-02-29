"""
The memory nutrition store uses Python dictionaries as data structures to store nutrition data.
This store is a simple and efficient implementation because there is little overhead.
However, the accumulation of nutrition data necessitates that old data is cleared routinely.
"""

import os
import sys

path = os.path.dirname(__file__)
if path not in sys.path:
    sys.path.append(path)

from store import NutritionStore

class MemoryNutritionStore(NutritionStore):
	"""
	A nutrition store that keeps the data in a dictionary.
	The keys are the timestamps, with each timestamp storing another dictionary.
	The inner dictionary has the terms as keys and their nutrition as values.

	:ivar store: The nutrition store as a dictionary.
				 The keys are the timestamps, and the values are the nutrition data.
				 The nutrition data can be any value.
	:vartype store: dict
	"""

	def __init__(self):
		"""
		Create the nutrition store as a dictionary.
		"""

		self.store = { }

	def add(self, timestamp, nutrition):
		"""
		Add a nutrition data to the store at the given timestamp.

		.. warning::

			This function overwrites any data at the given timestamp.

		:param timestamp: The timestamp of the nutrition data.
		:type timestamp: float or int or str
		:param nutrition: The nutrition data to add.
				 		  The nutrition data can be any value.
		:type nutrition: any
		"""

		self.store[str(timestamp)] = nutrition

	def get(self, timestamp):
		"""
		Get the nutrition data at the given timestamp.

		.. note::

			The function allows :class:`~IndexError` to be raised because having missing nutrition data needs to be handled.

		:param timestamp: The timestamp whose nutrition is to be returned.
		:type timestamp: float or int or str

		:return: The nutrition at the given timestamp.
		:rtype: any

		:raises KeyError: When there is no nutrition data at the given timestamp.
		"""

		return self.store[str(timestamp)]

	def all(self):
		"""
		Get all the nutrition sets.

		:return: All the nutrition data in the nutrition store as a dictionary.
				 The keys are the timestamps, and the values are the nutrition data at those timestamps.
		:rtype: dict
		"""

		return self.store

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
		keys = [ key for key in self.store.keys() if key >= start and key < end ] # filter the nutrition sets by timestamp

		return { timestamp: self.store[timestamp] for timestamp in keys }

	def remove(self, timestamp):
		"""
		Remove nutrition sets that are older than the given timestamp.

		:param timestamp: The timestamp before which no nutrition sets may exist.
		:type timestamp: int
		"""

		timestamp = int(timestamp)
		keys = sorted(self.store.keys())[::-1] # get the keys and sort them in descending order
		self.store = { key: self.store[key] for key in keys if key >= timestamp } # compile the nutrition sets, filtering keys by timestamp to retain only recent ones
