"""
The filter is the third step of the APD process.
It is responsible for removing candidates that it deems to be invalid.
The output is still a dictionary of candidate participants and their scores.

The input candidates should be the product of a :class:`apd.scorers.scorer.Scorer` process.
In other words, they should be a dictionary, with the keys being the candidates and the values being the score.

The functionality revolves around one method: the :meth:`apd.filters.filter.Filter.filter` method.
The function returns a dictionary of candidate participants and their scores.
"""

from abc import ABC, abstractmethod

class Filter(ABC):
	"""
	The filter goes through candidate participants and removes candidates that are not credible enough.
	"""

	@abstractmethod
	def filter(self, candidates, *args, **kwargs):
		"""
		Filter candidate participants that are not credible.

		:param candidates: A dictionary of candidate praticipants and their scores.
		 				   The keys are the candidate names, and the values are their scores.
						   The input candidates should be the product of a :class:`apd.scorers.scorer.Scorer` process.
		:type candidates: dict

		:return: A dictionary of filtered candidate participants and their associated scores.
		:rtype: dict
		"""

		pass
