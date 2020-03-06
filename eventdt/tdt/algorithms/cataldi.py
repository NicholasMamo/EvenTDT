"""
Cataldi et al.'s algorithm was among the first to introduce the notion of nutrition and burst.
The feature-pivot TDT algorithm first calculates the worth of terms as nutrition.
Then, periodically, it calculates the burst of these terms.
Burst is a measure of how much a term is bursting.

The calculations for burst are based on time windows.
Therefore calls to :meth:`~tdt.algorithms.cataldi.Cataldi.draw` should give the timestamp of the time window with respect to which the burst is to be calculated.

This implementation calculates the burst of terms based on the given nutrition.

.. note::

	Implementation based on the algorithm presented in `Personalized Emerging Topic Detection Based on a Term Aging Model by Cataldi et al. (2014) <https://dl.acm.org/doi/abs/10.1145/2542182.2542189>`_.
"""

import math
import time

from .tdt import TDTAlgorithm

class Cataldi(TDTAlgorithm):
	"""
	Cataldi et al.'s algorithm is a feature-pivot TDT approach to detect topics.
	The algorithm uses nutrition to calculate burst.
	Burst is a measure of how much a term is bursting.

	:ivar store: The store contraining historical nutrition data.
				 The algorithm expects the nutrition values to represent term nutrition.
				 Therefore the values should be dictionaries with terms as keys, and nutrition as the respective values.
				 Furthermore, the algorithm expects time windows.
				 In other words, the timestamps should represent an entire time window, not just a particular second.
	:vartype store: :class:`~tdt.nutrition.store.NutritionStore`
	"""

	def __init__(self, store):
		"""
		:param store: The store contraining historical nutrition data.
					  The algorithm expects the nutrition values to represent term nutrition.
					  Therefore the values should be dictionaries with terms as keys, and nutrition as the respective values.
					  Furthermore, the algorithm expects time windows.
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
	def _compute_burst(self, term, nutrition, historic):
		"""
		Calculate the burst for the given term using the historical data.
		The equation used is:

		.. math::

			burst_k^t = \\sum_{x=t-s}^(t-1)(((nutr_k^t)^2 - (nutr_k^x)^2) \\cdot \\frac{1}{log(t - x + 1)})

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

