"""
Summarization algorithms take in documents and create a summary out of them.
Although the specifics vary from one algorithm to the other, the goal does not.
"""

from abc import ABC, abstractmethod

class SummarizationAlgorithm(ABC):
	"""
	Summarization algorithms vary greatly and thus there is no general functionality or state.
	All algorithms must, however, implement the :func:`~summarization.algorithms.summarization.SummarizationAlgorithm.summarize` method.
	"""

	@abstractmethod
	def summarize(self, documents, length, *args, **kwargs):
		"""
		Summarize the given documents.

		Summarization algorithms may accept more parameters, but they must accept, at least a list of documents and the length of the summary.
		They must also always return a summary object.

		.. note::

			The algorithm assumes that the documents are already unique sentences.
			Therefore the summary is a selection of the given documents.

		:param documents: The list of documents to summarize.
		:type documents: list of :class:`~nlp.document.Document`
		:param length: The maximum length of the summary in characters.
		:type length: float

		:return: The summary of the documents.
		:rtype: :class:`~summarization.summary.Summary`
		"""

		pass
