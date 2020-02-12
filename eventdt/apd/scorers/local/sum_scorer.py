"""
Summation scorers assign a score to candidates that is proportional to the number of times that they appear.
"""

import math

from ..scorer import Scorer

class SumScorer(Scorer):
	"""
	The basic summation scorer assigns a score to tokens based on the significance of their appearance.
	This scorer rescales the scores of each document to be between 0 and 1.
	"""

	def score(self, candidates, *args, **kwargs):
		"""
		Score the given candidates based on their relevance within the corpus.
		The score is normalized using the maximum score

		:param candidates: A list of candidates participants that were found earlier.
		:type candidates: list

		:return: A dictionary of participants and their associated scores.
		:rtype: dict
		"""

		scores = self._sum(candidates, *args, **kwargs)
		return self._normalize(scores)

	def _sum(self, candidates, *args, **kwargs):
		"""
		Score the given candidates based on the number of times they appear—a simple summation.

		:param candidates: A list of candidates participants that were found earlier.
		:type candidates: list

		:return: A dictionary of candidate participants and their scores.
		:rtype: dict
		"""

		scores = {}

		"""
		Go through each document, and then each of its candidate participants.
		For all of these instances, increment their score.
		"""
		for candidate_set in candidates:
			for candidate in list(set(candidate_set)):
				scores[candidate] = scores.get(candidate, 0) + 1

		return scores

	def _normalize(self, scores, *args, **kwargs):
		"""
		Normalize the scores.
		The function rescales them between 0 and 1, where 1 is the maximum score of the candidates.

		:param scores: The candidate participants and the number of times that they appeared.
		:type scores: dict

		:return: A dictionary of candidate participants and their associated, normalized scores.
		:rtype: dict
		"""

		max_score = max(scores.values()) if len(scores) > 0 else 1
		scores = { candidate: score / max_score for candidate, score in scores.items() }

		return scores

class LogSumScorer(SumScorer):
	"""
	The log scorer is based on normal summation.
	However, the logarithms of the scores are taken.
	In this way, the candidates are not overly-biased towards candidates that appear disproportionately.

	This scorer rescales the scores of each document to be between 0 and 1.
	"""

	def score(self, candidates, base=10, *args, **kwargs):
		"""
		Score the given candidates based on their relevance within the corpus.
		The score is normalized using the maximum score

		:param candidates: A list of candidates participants that were found earlier.
		:type candidates: list
		:param base: The base of the logarithm.
		:type base: int

		:return: A dictionary of participants and their associated scores.
		:rtype: dict
		"""

		scores = self._sum(candidates)
		scores = { candidate: math.log(score + 1, base) for candidate, score in scores.items() } # apply Laplace smoothing
		return self._normalize(scores)
