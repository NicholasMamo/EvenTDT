"""
A scorer that scores the candidates based on the number of times that they appear.
"""

import math

from ..scorer import Scorer

class SumScorer(Scorer):
	"""
	A scorer that assigns a score to tokens based on the significance of their apperance.
	This is relative to general discourse.
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

		candidate_scores = self._sum(candidates, *args, **kwargs)

		return self._normalize(candidate_scores)

	def _sum(self, candidates, *args, **kwargs):
		"""
		Score the given candidates based on the number of times that they appear - a simple summation.

		:param candidates: A list of candidates participants that were found earlier.
		:type candidates: list

		:return: A dictionary of participants and the number of times that they appeared.
		:rtype: dict
		"""

		"""
		The score function assigns a score to each candidate.
		The scores are stored in a dictionary.
		"""
		candidate_scores = {}

		"""
		Go through each document, and then each of its candidates.
		For all of these instances, increment their score.
		"""
		for candidate_set in candidates:
			for candidate in list(set(candidate_set)):
				candidate_scores[candidate] = candidate_scores.get(candidate, 0) + 1

		return candidate_scores

	def _normalize(self, candidate_scores, *args, **kwargs):
		"""
		Normalize the scores.

		:param candidate_scores: The candidates and the number of times that they appeared.
		:type candidate_scores: dict

		:return: A dictionary of participants and their associated, normalized scores.
		:rtype: dict
		"""

		max_score = max(candidate_scores.values()) if len(candidate_scores) > 0 else 1
		candidate_scores = { candidate: score / max_score for candidate, score in candidate_scores.items() }

		return candidate_scores

class LogSumScorer(SumScorer):
	"""
	A scorer that is based on normal summation.
	However, the logarithms (base 10) of the scores are taken.
	In this way, the candidates are not biased towards candidates that appear disproportionately.
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

		candidate_scores = self._sum(candidates)
		candidate_scores = { candidate: math.log(score + 1, 10) for candidate, score in candidate_scores.items() } # apply Laplace smoothing
		return self._normalize(candidate_scores)
