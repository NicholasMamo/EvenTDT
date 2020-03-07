"""
Event TimeLine Detection (ELD) is a feature-pivot TDT approach designed to create interpretable results.
The algorithm computes burst for each individual term.
The interpretation is in the form of a burst value that lies between -1 and 1.
-1 indicates that a term is losing popularity, and 1 that it is gaining popularity.
When the burst is 0, the term's popularity is unchanged.

The broader system routinely creates checkpoints that represent the importance of terms in a particular time window.
The implemented TDT algorithm compares the documents received in the last time window with the previous checkpoints.

ELD borrows the terminology from Cataldi et al.'s previous work and algorithm: :class:`~tdt.algorithms.cataldi.Cataldi`.
This algorithm computes burst based on the past nutritions stored in the checkpoints.

.. note::

	Implementation based on the algorithm outlined in `ELD: Event TimeLine Detection -- A Participant-Based Approach to Tracking Events by Mamo et al. (2019) <https://dl.acm.org/doi/abs/10.1145/3342220.3344921>`_.
	ELD is a combined document-pivot and feature-pivot TDT approach.
	The algorithm in this module is the feature-pivot technique.
"""

import math

from .tdt import TDTAlgorithm

class ELD(TDTAlgorithm):
	"""
	Mamo et al.'s ELD is a feature-pivot TDT algorithm to detect breaking terms.
	The algorithm returns not only terms, but also the degree to which they are breaking.

	:ivar store: The store contraining historical nutrition data.
				 The algorithm expects the timestamps to represent checkpoints, or time windows.
				 Therefore the nutrition store should have dictionaries with timestamps as keys, and the nutrition of terms in a dictionary as values.
				 In other words, the timestamps should represent an entire time window, not just a particular second.
	:vartype store: :class:`~tdt.nutrition.store.NutritionStore`
	:ivar decay_rate: The decay rate used by the algorithm.
					  The larger the decay rate, the less importance far-off windows have in the burst calculation.
	:vartype decay_rate: float
	"""

	def __init__(self, store, decay_rate=(1./2)):
		"""
		:param store: The store contraining historical nutrition data.
					  The algorithm expects the timestamps to represent checkpoints, or time windows.
					  Therefore the nutrition store should have dictionaries with timestamps as keys, and the nutrition of terms in a dictionary as values.
					  In other words, the timestamps should represent an entire time window, not just a particular second.
		:type store: :class:`~tdt.nutrition.store.NutritionStore`
		:param decay_rate: The decay rate used by the algorithm.
						   The larger the decay rate, the less importance far-off windows have in the burst calculation.
		:type decay_rate: float
		"""

		self.store = store
		self.decay_rate = decay_rate

	def detect(self, nutrition, since=None, until=None, min_burst=0):
		"""
		Detect topics using historical data from the given nutrition store.

		:param nutrition: The nutrition values from the current (sliding) time window.
						  The keys should be the terms, and the values the respective nutrition.
		:type nutrition: dict
		:param since: The timestamp since when nutrition should be considered.
					  If it is not given, all of the nutrition that is available until the `until` is used.
		:type since: float or None
		:param until: The timestamp until when nutrition should be considered.
					  If it is not given, all of the nutrition that is available since the `since` parameter is used.
					  If the algorithm is being used retrospectively, this parameter can represent the current timestamp to get only past nutrition.
		:type until: float or None
		:param min_burst: The minimum burst of a term to be considered emerging and returned.
						  This value is exclusive.
						  By default, only terms thet have a non-zero positive burst are returned.
						  These terms have seen their popularity increase.
		:type min_burst: float

		:return: The breaking terms and their burst as a dictionary.
				 The keys are the terms and the values are the respective burst values.
		:rtype: dict
		"""

		"""
		If no timestamp to begin with is provided, all nutrition from the earliest possible timestamp is used.
		If no end timestamp is provided, all nutrition is used.
		"""
		since = since or 0

		"""
		Load the historic nutrition data.
		The timestamp being evaluated is not used.
		"""
		if until:
			historic = self.store.between(since, until)
		else:
			historic = self.store.since(since)

		"""
		Compute the burst of all the terms.
		Filter those with a low burst.
		"""
		burst = { term: self._compute_burst(term, nutrition, historic) for term in nutrition }
		burst = { term: burst for term, burst in burst.items() if burst > min_burst }
		return burst

	def _compute_burst(self, term, nutrition, historic):
		"""
		Calculate the burst for the given term using the historical data.
		The equation used is:

		.. math::

			burst_k^t = \\frac{\\sum_{c=t-s}^{t-1}((nutr_{k,l} - nutr_{k,c}) \\cdot \\frac{1}{\\sqrt{e^{t - c}}})}{\\sum_{c=1}^s\\frac{1}{\\sqrt{e^c}}}

		where :math:`k` is the term for which burst is to be calculated.
		:math:`t` is the current time window and :math:`s` is the number of time windows to consider.
		:math:`nutr_{k,l}` is the nutrition of the term in the local context.
		This local context refers to a cluster since the broader ELD system combines document-pivot and feature-pivot techniques.
		:math:`nutr_{k,c}` is the nutrition of the term in the checkpoint :math:`c`.

		The denominator is the component that is responsible for binding the burst between 1 and -1.

		.. note::

			The time windows are between :math:`t-s` and :math:`t-1`
			The most recent time window is :math:`x = t-1`.
			The exponential decay's denominator would thus be 2.
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
		First calculate the numerator.
		The historic data is sorted in descending order.
		"""
		historic = sorted(historic.items(), key=lambda data: data[0], reverse=True)
		historic = [ nutrition for timestamp, nutrition in historic ]
		burst = [ (nutrition.get(term, 0) - historic[c].get(term, 0)) * self._compute_decay(c + 1)
				  for c in range(len(historic)) ]

		"""
		Calculate the denominator.
		"""
		coefficient = self._compute_coefficient(len(historic))
		return sum(burst) / coefficient

	def _compute_decay(self, c):
		"""
		Compute the decay with an exponential formula:

		.. math::

			x = \\frac{1}{(e^c)^d}

		where :math:`c` is the number of time windows being considered and :math:`d` is the decay rate.
		By default, the decay rate is :math:`\\frac{1}{2}`:

		.. math::

			x = \\frac{1}{\\sqrt{e^c}}

		:param c: The current time window.
		:type c: int

		:return: The exponential decay factor, or how much weight the burst of a term in a time window has.
		:rtype: float
		"""

		return(1 / math.exp(c) ** self.decay_rate)

	def _compute_coefficient(self, s):
		"""
		Get the denominator of the burst calculation.
		This denominator is used to rescale the function, for example with bounds between -1 and 1.

		:param s: The number of time windows being considered.
		:type s: int

		:return: The denominator of the burst calculation.
		:rtype: float

		:raises ValueError: When there is a negative number of time windows.
		"""

		if s < 0:
			raise ValueError(f"The number of time windows cannot be negative: received {s}")

		"""
		If there are no time windows, the co-efficient should be 1.
		"""
		if not s:
			return 1
		else:
			return sum([ self._compute_decay(s + 1) for s in range(s) ])
