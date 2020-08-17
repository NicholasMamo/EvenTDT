"""
Cataldi et al.'s algorithm was among the first to introduce the notion of nutrition and burst.
The feature-pivot TDT algorithm first calculates the worth of terms as nutrition.
Then, periodically, it calculates the burst of these terms.
Burst is a measure of how much a term is bursting.

The calculations for burst are based on time windows.
Therefore calls to :func:`~tdt.algorithms.cataldi.Cataldi.detect` should give the timestamp of the time window with respect to which the burst is to be calculated.

This implementation calculates the burst of terms based on the given nutrition.

.. note::

	Implementation based on the algorithm presented in `Personalized Emerging Topic Detection Based on a Term Aging Model by Cataldi et al. (2014) <https://dl.acm.org/doi/abs/10.1145/2542182.2542189>`_.
"""

import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from algorithms import TDTAlgorithm

class Cataldi(TDTAlgorithm):
	"""
	Cataldi et al.'s algorithm is a feature-pivot TDT approach to detect topics.
	The algorithm uses nutrition to calculate burst.
	Burst is a measure of how much a term is bursting.

	:ivar store: The store contraining historical nutrition data.
				 The algorithm expects the timestamps to represent time windows.
				 Therefore the nutrition store should have dictionaries with timestamps as keys, and the nutrition of terms in a dictionary as values.
				 In other words, the timestamps should represent an entire time window, not just a particular second.
	:vartype store: :class:`~tdt.nutrition.store.NutritionStore`
	"""

	def __init__(self, store):
		"""
		:param store: The store contraining historical nutrition data.
					  The algorithm expects the timestamps to represent time windows.
					  Therefore the nutrition store should have dictionaries with timestamps as keys, and the nutrition of terms in a dictionary as values.
					  In other words, the timestamps should represent an entire time window, not just a particular second.
		:type store: :class:`~tdt.nutrition.store.NutritionStore`
		"""

		self.store = store

	def detect(self, timestamp, since=None):
		"""
		Detect topics using historical data from the given nutrition store.

		:param timestamp: The timestamp at which to try to identify emerging topics.
						  This value is exclusive.
		:type timestamp: float
		:param since: The timestamp since when nutrition should be considered.
					  If it is not given, all of the nutrition that is available is used.
		:type since: float or None

		:return: A list of breaking terms in the considered time window in descending order of their burst.
		:rtype: list of str
		"""

		"""
		If no timestamp to begin with is provided, all nutrition from the earliest possible timestamp is used.
		"""
		since = since or 0

		"""
		Load the nutrition that will be used to compute burst.
		Also load the historic nutrition data.
		The timestamp being evaluated is not used.
		"""
		nutrition = self.store.get(timestamp) or { }
		historic = self.store.between(since, timestamp)

		"""
		Compute the burst and the drops between drops.
		This is used to find the critical index, and then the bursty terms.
		"""
		burst = { term: self._compute_burst(term, nutrition, historic) for term in nutrition }
		drops = self._compute_burst_drops(burst)
		critical_index = self._get_critical_drop_index(drops)

		return self._get_bursty_terms(burst, critical_index)

	def _compute_burst(self, term, nutrition, historic):
		"""
		Calculate the burst for the given term using the historical data.
		The equation used is:

		.. math::

			burst_k^t = \\sum_{x=t-s}^{t-1}(((nutr_k^t)^2 - (nutr_k^x)^2) \\cdot \\frac{1}{log(t - x + 1)})

		where :math:`t` is the current time window and :math:`s` is the number of time windows to consider.

		.. note::

			The most recent time window is :math:`x = t-1`.
			The logarithm's denominator would thus be 2.
			At :math:`x = t-2`, the denominator would be 3.
			Thus, the older time windows get less importance.

		:param term: The term whose burst is being calculated.
		:type term: str
		:param nutrition: The nutrition in the current time window.
						  The keys are the terms and the values are their nutritions.
		:type nutrition: dict
		:param historic: The historic data.
						 The keys are the timestamps of each time window.
						 The values are the nutritions of the time window—another dictionary.
						 The keys in the inner dictionary are the terms and the values are their nutritions.
		:type historic: dict

		:return: The term's burst.
		:rtype: float
		"""

		"""
		Reverse the time windows in descending order.
		The algorithm computes burst by comparing the nutrition of the term with the historic windows.
		Far away windows have less of an impact than recent windows.

		.. note::

			Note the :math:`i + 1 + 1`.
			:math:`i` is the distance between the current time window and the old time window.
			Since the `enumerate` function starts from 0, the distance has to be incremented.
			The other 1 is added in the algorithm.
		"""
		return sum([(nutrition.get(term, 0) ** 2 - historic[window].get(term, 0) ** 2) / math.log(i + 1 + 1, 10)
					for i, window in enumerate(sorted(historic, reverse=True))])

	def _compute_burst_drops(self, burst):
		"""
		Compute the drops in burst among terms.
		The function sorts the burst values in descending order and computes the drops between them.

		:param burst: A dictionary with burst values.
					  The keys are the terms and the values are the corresponding burst values.
		:type burst: dict

		:return: A list of burst drops.
		:rtype: list of str
		"""

		burst = sorted(burst.values(), reverse=True)
		return [ burst[i] - burst[i + 1] for i in range(len(burst) - 1) ]

	def _get_critical_drop_index(self, drops):
		"""
		Find the critical drop index.
		The function isolates all drops that appear before the highest drop.
		The critical drop is the first drop in this selection that is bigger than the average drop.

		:param drops: A list of burst drops.
		:type drops: list of float

		:return: The index of the critical drop.
		:rtype: int
		"""

		"""
		Return immediately if there are no drops.
		"""
		if not drops:
			return 0

		"""
		If all drops have a value of 0, the number of drops + 1 is returned.
		This is equivalent to all terms (there are n-1 drops for n terms).
		"""
		if all(drop == 0 for drop in drops):
			return len(drops) + 1

		"""
		Find the maximum drop and isolate the burst values that appear before it.
		"""
		maximum_drop = max(drops)
		index = len(drops) - drops[::-1].index(maximum_drop)
		drops = drops[:index]

		"""
		Calculate the average drop and use it to find the critical index.

		.. note::

			The index is incremented because anything *before* the drop is bursty.
		"""
		if drops:
			average = sum(drops)/len(drops)

			for i, drop in enumerate(drops):
				if drop >= average:
					return i + 1

			return i + 1

		return 0

	def _get_bursty_terms(self, burst, critical_drop_index):
		"""
		Get the bursty terms.
		These terms are defined as those that appear before the critical drop index.

		:param burst: A dictionary with burst values.
					  The keys are the terms and the values are the corresponding burst values.
		:type burst: dict
		:param critical_drop_index: The critical drop index.
		:type critical_drop_index: int

		:return: The list of bursty terms, sorted in descending order of their burst.
		:rtype: str

		:raise ValueError: When the critical drop index is larger than the available terms.
						   This indicates that something wrong happened when calculating the critical drop index.
		"""

		if critical_drop_index > len(burst):
			raise ValueError(f"The critical drop index cannot be larger than the number of terms: {critical_drop_index} > {len(burst)}")

		burst = sorted(burst.items(), key=lambda term: term[1], reverse=True)
		return [ term for term, burst in burst[:critical_drop_index] ]
