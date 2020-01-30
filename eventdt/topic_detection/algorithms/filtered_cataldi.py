"""
A custom implementation of a filtered version of the algorithm by Cataldi et al. (2014).
"""

from scipy.stats import expon, norm, skewnorm

from . import cataldi

def detect_topics(nutrition_store, # the store contraining historical data
	timestamp, # the timestamp of the time window being considered
	sets=None, # the number of sets to consider
	p=1e-4, # the necessary probability of a breaking term's nutrition being that high
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
	:param p: The minimum required probability of a term being emergent for it to be retained.
	:type p: float
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
	historical_data = nutrition_store.get_recent_nutrition_sets(sets, timestamp=timestamp) # get the historical data

	term_nutrition = { term: value for term, value in term_nutrition.items() if value >= min_nutrition } # remove seldomly-used terms

	burstiness = { term: cataldi._get_burstiness(term, term_nutrition[term], historical_data) for term in term_nutrition } # calculate the burstiness for each term
	burstiness = sorted(burstiness.items(), key=lambda x: x[1])[::-1] # order the burstiness values in descending order based on the burstiness values

	burstiness_values = [ value for term, value in burstiness ] # isolate the burstiness values
	burstiness_drops = [burstiness_values[i - 1] - burstiness_values[i] for i in range(1, len(burstiness_values))]  # find the drops in burstiness values

	"""
	Find the critical drop index
	"""
	if len(burstiness_drops) > 0:
		critical_drop_index = cataldi._get_critical_drop_index(burstiness_drops)
		critical_drop_index = max(min(critical_drop_index, max_breaking), min_breaking)
	else:
		critical_drop_index = 0

	skew, mu, std = skewnorm.fit(burstiness_values) # fit a skewed normal distribution over all burstiness values
	return [ term for term, value in burstiness[:critical_drop_index] if (1 - skewnorm.cdf(value, skew, mu, std)) < p ]
