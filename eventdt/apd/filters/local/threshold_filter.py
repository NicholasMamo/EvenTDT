"""
The threshold filter excludes candidate participants with a score that is lower than a specified threshold.
"""

import math

from ..filter import Filter

class ThresholdFilter(Filter):
	"""
	The threshold filter excludes candidate participants with a score that is lower than a specified threshold.
	"""

	def filter(self, candidates, threshold, *args, **kwargs):
		"""
		Filter candidate participants that are not credible.

		:param candidates: A dictionary of candidate praticipants and their scores.
		 				   The keys are the candidate names, and the values are their scores.
						   The input candidates should be the product of a :class:`apd.scorers.scorer.Scorer` process.
		:type candidates: dict
		:param threshold: The threshold below which candidate participants are removed.
						  The threshold is applied over the candidate participant scores.

		:return: A dictionary of filtered candidate participants and their associated scores.
		:rtype: dict
		"""

		return { candidate: score for candidate, score in candidates.items() if score >= threshold }
