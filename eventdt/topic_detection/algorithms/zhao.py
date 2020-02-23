"""
Implementation of the algorithm by Zhao et al. (2011).

The algorithm segments time windows into two parts and compares them together.
If the second part has a tweet volume that is higher than the first by at least a certain ratio, the time window represents a development.
Zhao et al. take this ratio to be 1.7.
"""

import math

def detect_topics(nutrition_store, # the store contraining historical data
		timestamp, # the timestamp of the time window being considered
		post_rate=1.7, # the minimum ratio to detect a development
		time_windows=[10, 20, 30, 60], # the lengths of the time window
	):
	"""
	Detect topics using historical data from the given NutritionStore.

	:param nutrition_store: The store contraining historical data.
	:type NutritionStore: :class:`~topic_detection.nutrition_store.nutrition_store.NutritionStore`
	:param timestamp: The current time window's timestamp (in seconds).
		This is taken to be the timestamp when the time window ended and is exclusive.
	:type timestamp: int
	:param post_rate: The minimum ratio of increasing volume to detect a development.
	:type post_rate: float
	:param time_window: The lengths of the time window to consider.
		This time window is split into two phases, the 'before' and 'after'.
		Starting from the first window, the process repeats until a development is found, or the time windows are exhausted.
		Zhao et al. discuss the effects of different lengths in their 2011 paper.

	:return: A tuple indicating how recent the development broke, if at all.
		The tuple is made up of a boolean, and the timw window length.
	:rtype: tuple
	"""

	for window in sorted(time_windows):
		"""
		Go through each time window and attempt to check whether there as a breaking development.
		"""

		half_window = window / 2.

		first_half = sum(nutrition_store.between(timestamp - window, timestamp - half_window).values())
		second_half = sum(nutrition_store.between(timestamp - half_window, timestamp).values())

		if first_half == 0:
			continue

		ratio = second_half / first_half
		if ratio > post_rate:
			return (True, window)

	"""
	If all else fails, then the time window was simply not breaking.
	"""
	return (False, 0)
