"""
A scorer that scores the candidates using an IDF table.
"""

import math

from ..scorer import Scorer

class IDFScorer(Scorer):
	"""
	A scorer that assigns a score to tokens based on the significance of their apperance.
	This is relative to general discourse.
	"""

	def score(self, candidates, scorer_idf, *args, **kwargs):
		"""
		Score the given candidates based on their relevance within the corpus.

		:param candidates: A list of candidate praticipants separated by document that were found in them earlier.
		:type candidates: list
		:param idf: The IDF table, represented as a dictionary.
			It is assumed that the number of documents is stored in the key 'DOCUMENTS.'
		:type idf: dict

		:return: A dictionary of participants and their associated scores.
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
				idf_score = candidate_set.count(candidate) * math.log(max(scorer_idf.get("DOCUMENTS"), 1) / scorer_idf.get(candidate, 1), 10)
				candidate_scores[candidate] = candidate_scores.get(candidate, 0) + idf_score

		"""
		Normalize the scores.
		"""
		max_score = max(candidate_scores.values())
		candidate_scores = { candidate: score/max_score for candidate, score in candidate_scores.items() }

		return candidate_scores
