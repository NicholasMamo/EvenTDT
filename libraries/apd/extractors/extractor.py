"""
An extractor looks for candidate participants in the corpus of documents.

The extractor returns all candidates, regardless of their significance.
No scoring or filtering takes place.

Candidates are separated according to the document in which they are found.
"""

from abc import ABC, abstractmethod

class Extractor(ABC):
	"""
	The extractor must return participants, if it finds any.
	Given a list of documents, it looks within the text or tokens.
	"""

	@abstractmethod
	def extract(self, corpus, token_attribute="tokens", *args, **kwargs):
		"""
		Extract all the potential participants from the corpus.
		The output is a list of lists.
		It should be noted that zipping together this list and the corpus should return a list of documents and associated candidates.

		:param corpus: The corpus of documents where to extract participants.
		:type corpus: list
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: A list of candidates separated by the document in which they were found.
		:rtype: list
		"""

		pass
