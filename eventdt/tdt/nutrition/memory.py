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
		Get the nutrition data between the given timestamps.

		.. note::

			The start timestamp is inclusive, the end timestamp is exclusive.

		:param start: The first timestamp that should be included in the returned nutrition data.
					  If no time window with the given timestamp exists, all returned time windows succeed it.
		:type start: float or int or str
		:param end: All the nutrition data from the beginning until the given timestamp.
					Any nutrition data at the end timestamp is not returned.
		:type end: float or int or str

		:return: All the nutrition data between the given timestamps.
				 The start timestamp is inclusive, the end timestamp is exclusive.
		:rtype: dict

		:raises ValueError: When the start timestamp is on or after the end timestamp.
		"""

		if float(start) >= float(end):
			raise ValueError(f"The start timestamp must be before the end timestamp: {start} >= {end}")

		return { timestamp: self.get(timestamp) for timestamp in self.store if float(start) <= float(timestamp) < float(end) }

	def remove(self, *args):
		"""
		Remove nutrition data from the given list of timestamps.
		The timestamps should be given as arguments.
		"""

		timestamps = [ str(timestamp) for timestamp in args ]
		self.store = { timestamp: self.store.get(timestamp) for timestamp in self.store if timestamp not in timestamps }
