"""
The scorer is the second step of the APD process.
It is responsible for assigning a score to each candidate that is provided.
Thus, it pairs up each participant with a score.

The input candidates should be the product of a :class:`apd.extractors.extractor.Extractor` process.
In other words, they should be a list, representing documents.
Each such list contains another list of candidates.

The functionality revolves around one method: the :meth:`apd.scorers.scorer.Scorer.score` method.
The function returns a dictionary of candidate participants and their scores.
The scores may be normalized to make them comparable.
This can be a simple rescaling function.
"""

from abc import ABC, abstractmethod

class Scorer(ABC):
	"""
	The scorer returns a score for each candidate participant found in the corpus.
	"""

	@abstractmethod
	def score(self, candidates, normalize_scores=True, *args, **kwargs):
		"""
		Score the candidate participants that were found in the corpus.

		:param candidates: A list of candidate praticipants separated by the document in which they appeared.
						   The input candidates should be the product of a :class:`apd.extractors.extractor.Extractor` process.
		:type candidates: list
		:param normalize_scores: A boolean indicating whether the scores should be normalized.
								 Here, normalization means rescaling between 0 and 1.
		:type normalize_scores: bool

		:return: A dictionary of candidate participants and their associated scores.
		:rtype: dict
		"""

		pass

	def _normalize(self, scores, *args, **kwargs):
		"""
		Normalize the scores.
		The default function returns the scores as it founds them.

		:param scores: A list of candidate participants and their scores.
		:type scores: dict

		:return: A dictionary of candidate participants and their associated scores.
		:rtype: dict
		"""

		return scores
