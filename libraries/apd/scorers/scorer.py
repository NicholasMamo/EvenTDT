"""
A scorer is responsible for assigning a score to each candidate that is provided.
Thus, it pairs up each participant with a score.

The input candidates should be the product of a :class:`apd.extractors.extractor.Extractor` process.
In other words, zipping the candidates with the corpus should give a list of documents and associated candidate participants.
"""

from abc import ABC, abstractmethod

class Scorer(ABC):
	"""
	Any scorer returns a score for each participant.
	"""

	@abstractmethod
	def score(self, candidates, corpus, token_attribute="tokens", *args, **kwargs):
		"""
		Score the participants that were found in the corpus.

		:param candidates: A list of candidate praticipants separated by document that were found in them earlier.
		:type candidates: list
		:param corpus: The corpus of documents, which helps to measure the membership of new candidates.
		:type corpus: list
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: A dictionary of participants and their associated scores.
		:rtype: dict
		"""

		pass
