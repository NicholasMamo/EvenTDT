"""
The extractor is the first step in the APD process.
An extractor looks for candidate participants in the corpus of documents.
All extractors take the corpus as an input.

The extractor returns the candidates in each document.
The functionality revolves around one method: the :func:`~apd.extractors.extractor.Extractor.extract` method.
"""

from abc import ABC, abstractmethod

class Extractor(ABC):
	"""
	The extractor returns any participants that it finds.
	The functionality revolves around one method: the :func:`~apd.extractors.extractor.Extractor.extract` method.
	"""

	@abstractmethod
	def extract(self, corpus, *args, **kwargs):
		"""
		Extract all the potential participants from the given corpus.
		The output is a list of lists.
		Each outer list represents a document.
		Each inner list is the candidates in that document.

		:param corpus: The corpus of documents from where to extract candidate participants.
		:type corpus: list of :class:`~nlp.document.Document`

		:return: A list of candidates separated by the document in which they were found.
		:rtype: list of list of str
		"""

		pass
