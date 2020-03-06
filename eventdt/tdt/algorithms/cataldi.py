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
