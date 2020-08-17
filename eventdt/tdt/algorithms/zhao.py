"""
Zhao et al.'s algorithm is a feature-pivot approach to TDT.
The algorithm identifies spikes in volume in the stream by halving the most recent time window.
If the second half has a marked increase in volume—a ratio taken to be 1.7—the algorithm identifies a topic.
If the increase is not significant, the time window is progressively increased.

The algorithm is suitable to run in real-time.

.. note::

	Implementation based on the algorithm presented in `Human as Real-Time Sensors of Social and Physical Events: A Case Study of Twitter and Sports Games by Zhao et al. (2011) <https://arxiv.org/abs/1106.4300>`_.
"""

import math
import os
import time
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from tdt.algorithms import TDTAlgorithm

class Zhao(TDTAlgorithm):
	"""
	Zhao et al.'s algorithm is a feature-pivot approach to TDT.
	The algorithm identifies spikes in volume in the stream by halving the most recent time window.
	If the second half has a marked increase in volume—a ratio taken to be 1.7—the algorithm identifies a topic.
	If the increase is not significant, the time window is progressively increased.

	:ivar store: The store contraining historical nutrition data.
				 The algorithm expects the nutrition values to represent the stream volume.
				 Therefore the values should be floats or integers.
	:vartype store: :class:`~tdt.nutrition.store.NutritionStore`
	:ivar post_rate: The minimum ratio between two time windows to represent a burst.
	:vartype post_rate: float
	"""

	def __init__(self, store, post_rate=1.7):
		"""
		:param store: The store contraining historical nutrition data.
					  The algorithm expects the nutrition values to represent the stream volume.
					  Therefore the values should be floats or integers.
		:type store: :class:`~tdt.nutrition.store.NutritionStore`
		:param post_rate: The minimum ratio between two time windows to represent a burst.
		:type post_rate: float
		"""

		self.store = store
		self.post_rate = post_rate

	def detect(self, timestamp=None):
		"""
		Detect topics using historical data from the nutrition store.

		:param timestamp: The timestamp at which to try to identify emerging topics.
						  If it is not given, the current timestamp is used.
						  This value is exclusive.
		:type timestamp: float or None

		:return: A tuple with the start and end timestamp of the time window when there was a burst.
				 If there was no burst, `False` is returned.
		:rtype: tuple or bool
		"""

		"""
		If no time was given, default to the current timestamp.
		"""
		timestamp = timestamp or time.time()

		"""
		Go through each time window and check whether there as a breaking development.
		"""
		time_windows = [ 10, 20, 30, 60 ]
		for window in time_windows:
			"""
			Split the time window in two and get the volume in both.
			"""
			half_window = window / 2.
			first_half = self.store.between(timestamp - window, timestamp - half_window)
			second_half = self.store.between(timestamp - half_window, timestamp)

			"""
			If the first half has no tweets, skip the time window.
			"""
			if sum(first_half.values()) == 0:
				continue

			"""
			Calculate the increase in post rate.
			If the ratio is greater than or equal to the post rate, the time window is breaking.
			Therefore return the emerging period: the second half of the time window.
			"""
			ratio = sum(second_half.values()) / sum(first_half.values())
			if ratio >= self.post_rate:
				return (float(min(second_half)), float(max(second_half)))

		"""
		Return `False` if none of the time windows were deemed to be emerging.
		"""
		return False
