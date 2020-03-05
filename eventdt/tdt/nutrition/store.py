"""
The concept of nutrition was used predominantly by `Cataldi et al. <https://dl.acm.org/doi/abs/10.1145/2542182.2542189>`_.
Later, it was adopted by Mamo and others in `FIRE <https://link.springer.com/chapter/10.1007/978-3-319-74497-1_3>`_ and `ELD <https://dl.acm.org/doi/abs/10.1145/3342220.3344921>`_.
Nutrition is a measure of the popularity of a term.
It is combined with another metric—burst—that measures the change in nutrition.

The nutrition store is an interface for data structures to store the nutrition.
The interface contains the methods that they all must implement.
For example, implementations can store data in a database or in memory.

The nutrition stores separate nutrition based on timestamps.
The timestamps can store nutrition data for that timestamp alone.
They can also store nutrition data for a period of time, represented by that timestamp.
"""

from abc import ABC, abstractmethod

class NutritionStore(ABC):
	"""
	The nutrition store needs to handle both the storage of nutrition, as well as retrieval.
	All nutrition stores must implement all of the following methods.
	Nutrition stores separate data based on timestamps.
	"""

	@abstractmethod
	def __init__(self):
		"""
		Create the nutrition store.
		"""

		pass

	@abstractmethod
	def add(self, timestamp, nutrition):
		"""
		Add a nutrition data to the store at the given timestamp.

		.. warning::

			This function overwrites any data at the given timestamp.

		:param timestamp: The timestamp of the nutrition data.
		:type timestamp: float or int
		:param nutrition: The nutrition data to add.
						  The nutrition data can be any value.
		:type nutrition: any
		"""

		pass

	@abstractmethod
	def get(self, timestmap):
		"""
		Get the nutrition data at the given timestamp.

		.. note::

			The function allows :class:`~IndexError` to be raised because having missing nutrition data needs to be handled.

		:param timestamp: The timestamp whose nutrition is to be returned.
		:type timestamp: float or int

		:return: The nutrition at the given timestamp.
		:rtype: any

		:raises KeyError: When there is no nutrition data at the given timestamp.
		"""

		pass

	@abstractmethod
	def all(self):
		"""
		Get all the nutrition data.

		:return: All the nutrition data in the nutrition store as a dictionary.
				 The keys are the timestamps, and the values are the nutrition data at those timestamps.
		:rtype: dict
		"""

		pass

	@abstractmethod
	def between(self, start, end):
		"""
		Get the nutrition data between the given timestamps.

		.. note::

			The start timestamp is inclusive, the end timestamp is exclusive.

		:param start: The first timestamp that should be included in the returned nutrition data.
					  If no time window with the given timestamp exists, all returned time windows succeed it.
		:type start: float or int
		:param end: All the nutrition data from the beginning until the given timestamp.
					Any nutrition data at the end timestamp is not returned.
		:type end: float or int

		:return: All the nutrition data between the given timestamps.
				 The start timestamp is inclusive, the end timestamp is exclusive.
		:rtype: dict
		"""

		pass

	def since(self, start):
		"""
		Get the nutrition data since the given timestamp.

		.. note::

			The start timestamp is inclusive.

		:param start: The first timestamp that should be included in the returned nutrition data.
					  If no time window with the given timestamp exists, all returned time windows succeed it.
		:type start: float or int

		:return: All the nutrition data from the given timestamp onward.
		:rtype: dict
		"""

		timestamps = [ float(timestamp) for timestamp in self.all().keys() ]
		last = max(timestamps)
		return self.between(start, float(last) + 1)

	def until(self, end):
		"""
		Get a list of nutrition sets that came before the given timestamp.

		.. note::

			The end timestamp is exclusive.

		:param end: The timestamp before which nutrition data should be returned.
		:type end: float or int

		:return: All the nutrition data from the beginning until the given timestamp.
				 Any nutrition data at the end timestamp is not returned.
		:rtype: dict
		"""

		timestamps = [ float(timestamp) for timestamp in self.all().keys() ]
		last = min(timestamps)
		return self.between(0, str(end))

	@abstractmethod
	def remove(self, *args):
		"""
		Remove nutrition data from the given list of timestamps.
		The timestamps should be given as arguments.
		"""

		pass
