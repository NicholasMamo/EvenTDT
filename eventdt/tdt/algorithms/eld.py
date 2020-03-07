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

		bursty_terms = []
		historical_data = nutrition_store.get_recent_nutrition_sets(sets, timestamp=timestamp) # get the historical data

		if (sets is None and len(historical_data) > 0) or (sets is not None and len(historical_data) == sets):
			term_nutrition = { term: value for term, value in data.items() if value >= min_nutrition } # remove seldomly-used terms

			burstiness = { term: _get_burstiness(term, term_nutrition[term], historical_data, decay_function=(_exponential_decay, decay_rate)) for term in term_nutrition } # calculate the burstiness for each term
			burstiness = sorted(burstiness.items(), key=lambda x: x[1])[::-1] # sort the burstiness values in descending order

			if term_only:
				bursty_terms = [ term for term, value in burstiness if value >= threshold ]
			else:
				bursty_terms = [ (term, value) for term, value in burstiness if value >= threshold ]

		return bursty_terms

	def _get_burstiness(self, term, nutrition, historical_data, decay_function=(_exponential_decay, None), laplace=False):
		"""
		Calculate the burstiness for the given term using the historical data.

		:param term: The term whose burstiness is being calculated.
		:type term: str
		:param nutrition: The term's nutrition in the current time window.
		:type nutrition: float
		:param historical_data: The historical data to consider.
		:type historical_data: dict
		:param decay_function: The tuple containing the decay function to use and the associated decay rate.
		:type decay_function: tuple(function, float)
		:param laplace: A boolean indicating whether Laplace smoothing should be applied.
		:type laplace: bool

		:return: The term's burstiness.
		:rtype: float
		"""

		decay_function, decay_rate = decay_function
		windows = len(historical_data)
		coefficient = _get_coefficient(windows, (decay_function, decay_rate))

		burstiness = [ (nutrition - historical_data[i].get(term, 0)) * decay_function(i + 1, decay_rate=decay_rate) for i in range(0, windows) ]
		return sum(burstiness) / coefficient

	def _exponential_decay(self, n, decay_rate=(1./2)):
		"""
		An exponential decay factor with the formula:
			x = 1 / (exp(n)^decay_rate)

		:param n: The number of time windows to consider.
		:type n: int
		:param decay_rate: The decay rate of the burstiness function.
			A smaller value gives more uniform weight to far-off nutrition sets.

		:return: The exponential decay factor, or how much a result should be weighted.
		:rtype: float
		"""

		return(1 / math.exp(n) ** decay_rate)

	def _get_coefficient(self, n, decay_function):
		"""
		Get the denominator of the burstiness calculation.
		This denominator is used to rescale the function, for example with bounds between -1 and 1.

		:param n: The number of time windows to consider.
		:type n: int
		:param decay_function: The tuple containing the decay function to use and the associated decay rate.
		:type decay_function: tuple(function, float)

		:return: The denominator of the burstiness calculation.
		:rtype: float
		"""

		decay_function, decay_rate = decay_function
		return sum([ decay_function(n + 1, decay_rate=decay_rate) for n in range(0, n) ])
