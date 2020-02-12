"""
The TF-IDF scorer assigns a score the candidate participants similarly to the :class:`nlp.term_weighting.tfidf.TFIDF` term-weighting scheme.
"""

import math

from ..scorer import Scorer

class TFIDFScorer(Scorer):
	"""
	The TF-IDF scorer assigns a score the candidate participants similarly to the :class:`nlp.term_weighting.tfidf.TFIDF` term-weighting scheme.
	Therefore the scorer depends on an IDF table, given as a dictionary.
	"""

	def score(self, candidates, idf, normalize_scores=True, *args, **kwargs):
		"""
		Score the given candidates based on their relevance within the corpus.

		:param candidates: A list of candidate praticipants separated by document that were found in them earlier.
		:type candidates: list
		:param idf: The IDF table, represented as a dictionary.
					The keys are the terms, and the corresponding values are the number of documents in which they appear.
		:type idf: dict
		:param documents: The number of documents in the IDF table.
		:type documents: int
		:param normalize_scores: A boolean indicating whether the scores should be normalized.
								 Here, normalization means rescaling between 0 and 1.
		:type normalize_scores: bool

		:return: A dictionary of participants and their associated scores.
		:rtype: dict

		:raises ValueError: When the document frequency of a term is higher than the number of the IDF documents.
		:raises ValueError: When the document frequency of a term is negative.
		:raises ValueError: When the number of documents is negative.
		"""

		if max(idf.values()) > documents:
			raise ValueError(f"The number of documents ({documents}) must be greater or equal to the most common term ({max(idf.values())})")

		if min(idf.values()) < 0:
			raise ValueError("The IDF values must be non-negative")

		if documents < 0:
			raise ValueError("The number of documents in the IDF must be non-negative")

		"""
		Go through each document, and then each of its candidates.
		For all of these candidates, increment their score by calculating the TF-IDF in that document.
		"""
		scores = {}
		for candidate_set in candidates:
			for candidate in list(set(candidate_set)):
				scores[candidate] = scores.get(candidate, 0) + candidate_set.count(candidate) * documents / idf.get(candidate, 1)

		return self._normalize(scores) if normalize_scores else scores

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
