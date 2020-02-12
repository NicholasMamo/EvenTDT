"""
The logarithmic document frequency scorer is based on the document frequency scorer.
The difference is that it applies a logarithm to decrease the difference between candidates that appear very often and those which do not.
"""

import math

class LogDFScorer(DFScorer):
	"""
	The log scorer is based on normal summation.
	However, the logarithms of the scores are taken.
	In this way, the candidates are not overly-biased towards candidates that appear disproportionately.

	This scorer rescales the scores of each document to be between 0 and 1.
	"""

	def score(self, candidates, base=10, normalize_scores=True, *args, **kwargs):
		"""
		Score the given candidates based on their relevance within the corpus.
		The score is normalized using the maximum score

		:param candidates: A list of candidates participants that were found earlier.
		:type candidates: list
		:param base: The base of the logarithm.
		:type base: int
		:param normalize_scores: A boolean indicating whether the scores should be normalized.
								 Here, normalization means rescaling between 0 and 1.
		:type normalize_scores: bool

		:return: A dictionary of participants and their associated scores.
		:rtype: dict
		"""

		scores = self._sum(candidates)
		scores = { candidate: math.log(score + 1, base) for candidate, score in scores.items() } # apply Laplace smoothing
		return self._normalize(scores) if normalize_scores else scores
