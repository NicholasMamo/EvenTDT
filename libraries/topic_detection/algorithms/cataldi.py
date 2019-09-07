"""
Implementation of the algorithm by Cataldi et al. (2014).
"""

import math

def detect_topics(nutrition_store, # the store contraining historical data
	timestamp, # the timestamp of the time window being considered
	sets=None, # the number of sets to consider
	min_nutrition=0, # consider only nutrition having a minimal value
	max_breaking=10, # the maximum number of breaking terms
	min_breaking=0 # the minimum number of breaking terms
	):
	"""
	Detect topics using historical data from the given NutritionStore.

	:param nutrition_store: The store contraining historical data.
	:type NutritionStore: :class:`topic_detection.nutrition_store.nutrition_store.NutritionStore`
	:param timestamp: The current time window's timestamp (in seconds).
	:type timestamp: int
	:param sets: The number of time windows to consider.
	:type sets: int
	:param min_nutrition: The minimum nutrition of a term to be considered.
	:type min_nutrition: float
	:param max_breaking: The maximum number of breaking terms to return.
	:type max_breaking: int
	:param min_breaking: The minimum number of breaking terms to return.
	:type min_breaking: int

	:return: A list of breaking terms in the considered time window.
	:rtype: list
	"""

	term_nutrition = nutrition_store.get_nutrition_set(timestamp) # fetch the nutrition
	historical_data = nutrition_store.get_recent_nutrition_sets(sets, timestamp=(timestamp - 1)) # get the historical data

	term_nutrition = { term: value for term, value in term_nutrition.items() if value >= min_nutrition } # remove seldomly-used terms

	burstiness = { term: _get_burstiness(term, term_nutrition[term], historical_data) for term in term_nutrition } # calculate the burstiness for each term
	burstiness = sorted(burstiness.items(), key=lambda x: x[1])[::-1] # order the burstiness values in descending order based on the burstiness values

	burstiness_values = [ value for term, value in burstiness ] # isolate the burstiness values
	burstiness_drops = [burstiness_values[i - 1] - burstiness_values[i] for i in range(1, len(burstiness_values))]  # find the drops in burstiness values

	"""
	Find the critical drop index
	"""
	if len(burstiness_drops) > 0:
		critical_drop_index = _get_critical_drop_index(burstiness_drops)
		critical_drop_index = max(min(critical_drop_index, max_breaking), min_breaking)
	else:
		critical_drop_index = 0

	return [ term for term, _ in burstiness[:critical_drop_index] ]

def _get_burstiness(term, nutrition, historical_data):
	"""
	Calculate the burstiness for the given term using the historical data.

	:param term: The term whose burstiness is being calculated.
	:type term: str
	:param nutrition: The term's nutrition in the current time window.
	:type nutrition: float
	:param historical_data: The historical data to consider.
	:type historical_data: dict

	:return: The term's burstiness.
	:rtype: float
	"""
	windows = len(historical_data)
	return sum([(nutrition ** 2 - historical_data[i].get(term, 0) ** 2) / math.log(i + 2, 10) for i in range(0, windows)])

def _get_critical_drop_index(burstiness_drops):
	"""
	Find the critical drop index.

	:param burstiness_drops: A list of burstiness drops.
	:type burstiness_drops: list

	:return: The index where the critical drop appears.
	:rtype: int
	"""

	"""
	First find the maximum and average drops
	"""
	maximum_drop = max(burstiness_drops)
	maximum_drop_index = burstiness_drops.index(maximum_drop)
	average_drop = sum(burstiness_drops[0:maximum_drop_index])/maximum_drop_index if maximum_drop_index > 0 else 0 # get the average drop

	"""
	Then identify the critical index
	"""
	for i in range(1, len(burstiness_drops)):
		if (burstiness_drops[i - 1] >= average_drop):
			return i
