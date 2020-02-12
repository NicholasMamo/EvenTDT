"""
The scorer is the second step of the APD process.
It is responsible for assigning a score to each candidate that is provided.
Thus, it pairs up each participant with a score.

The input candidates should be the product of a :class:`apd.extractors.extractor.Extractor` process.
In other words, they should be a list, representing documents.
Each such list contains another list of candidates.

The functionality revolves around one method: the :meth:`apd.scorers.scorer.Scorer.score` method.
The function returns a dictionary of candidate participants and their scores.
"""

from abc import ABC, abstractmethod

class Scorer(ABC):
	"""
	The scorer returns a score for each candidate participant found in the corpus.
	"""

	@abstractmethod
	def score(self, candidates, *args, **kwargs):
		"""
		Score the candidate participants that were found in the corpus.

		:param candidates: A list of candidate praticipants separated by the document in which they appeared.
						   The input candidates should be the product of a :class:`apd.extractors.extractor.Extractor` process.
		:type candidates: list

		:return: A dictionary of participants and their associated scores.
		:rtype: dict
		"""

		pass
