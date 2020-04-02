"""
The Maximal Marginal Relevance (MMR) algorithm takes in documents and a query and builds a summary.
This summary has the ideal property of being relevant to the query and non-redundant.
The algorithm follows a greedy approach.

.. note::

	Implementation based on the algorithm presented in `The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries by Carbonell and Goldstein (1998) <https://dl.acm.org/doi/abs/10.1145/290941.291025>`_.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from .summarization import SummarizationAlgorithm
from summarization import Summary

from vsm.clustering import Cluster
from vsm import vector_math

class MMR(SummarizationAlgorithm):
	"""
	The Maximal Marginal Relevance (MMR) algorithm accepts documents and a query and builds a summary.
	The algorithm looks to build a summary that is simultaneously similar to the query and non-redundant.

	:ivar l: The :math:`\\lambda` parameter, which must be between 0 and 1.
			 When :math:`\\lambda` is 1, only relevance to the query is considered.
			 When :math:`\\lambda` is 0, only non-redundancy is considered.
			 By default, the algorithm assigns equal weight to relevance and non-redundancy.
	:vartype l: float
	"""

	def __init__(self, l=0.5):
		"""
		Create the MMR summarization algorithm with the lambda value.

		:param l: The :math:`\\lambda` parameter, which must be between 0 and 1.
				  When :math:`\\lambda` is 1, only relevance to the query is considered.
				  When :math:`\\lambda` is 0, only non-redundancy is considered.
				  By default, the algorithm assigns equal weight to relevance and non-redundancy.
		:type l: float

		:raises ValueError: When lambda is not between 0 and 1.
		"""

		if not 0 <= l <= 1:
			raise ValueError(f"Invalid lambda value {l}")

		self.l = l

	def summarize(self, documents, length, query=None, *args, **kwargs):
		"""
		Summarize the given documents.

		.. note::

			The algorithm assumes that the documents are already unique sentences.
			Therefore the summary is a selection of the given documents.

		:param documents: The list of documents to summarize.
		:type documents: list of :class:`~nlp.document.Document`
		:param length: The maximum length of the summary in characters.
		:type length: float
		:param query: The query around which to build the summary.
					  If no query is given, the summary is built around the centroid of documents.
		:type query: :class:`~vsm.vector.Vector` or None

		:return: The summary of the documents.
		:rtype: :class:`~summarization.summary.Summary`

		:raises ValueError: When the summary length is not positive.
		"""

		summary = Summary()

		"""
		Validate the inputs.
		"""
		if length <= 0:
			raise ValueError(f"Invalid summary length {length}")

		"""
		Compute the query if need be, and construct the similarity matrix.
		"""
		query = query or self._compute_query(documents)
		matrix = self._compute_similarity_matrix(documents, query)

		"""
		The loop continues picking documents until one of two conditions is reached:

		 	#. No documents remain;

			#. Adding any of the remaining documents mean that the summary becomes too long.
		"""
		while True:
			"""
			Return if there are no remaining candidates for the summary.
			"""
			candidates = self._filter_documents(documents, summary, length - len(str(summary)))
			if not candidates:
				return summary

			"""
			Otherwise, get the next document for the summary.
			"""
			document = self._get_next_document(candidates, summary, query, matrix)
			summary.documents.append(document)

		return Summary([ collection[d] for d in summary ], timestamp)

	def _compute_query(self, documents):
		"""
		Create the query from the given documents.
		The query is equivalent to the centroid of the documents.

		:param documents: The list of documents to summarize.
		:type documents: list of :class:`~nlp.document.Document`

		:return: The centroid of the documents.
		:rtype: `~vsm.vector.Vector`
		"""

		return Cluster(vectors=documents).centroid

	def _compute_similarity_matrix(self, documents, query):
		"""
		Create the similarity matrix.
		This matrix contains the similarities between the documents themselves, and between the documents and the query.

		:param documents: The list of documents to summarize.
		:type documents: list of :class:`~nlp.document.Document`
		:param query: The query to which documents will be compared.
		:type query: :class:`~nlp.document.Document`

		:return: The similarity matrix as a dictionary.
				 The keys are the documents, and the values are their similarities.
				 These similarities are another dictionary.
				 The keys are the other document, and the value is the actual similarity.
		:rtype: dict
		"""

		documents = documents + [query]
		matrix = { document: { } for document in documents }
		for i, document in enumerate(documents):
			for other in documents[i:]:
				similarity = vector_math.cosine(document, other)
				matrix[document][other] = similarity
				matrix[other][document] = similarity

		return matrix

	def _filter_documents(self, documents, summary, length):
		"""
		Get the documents that can be added to the summary.
		These include:

			#. Documents that are not already in the summary;

			#. Documents that are shorter than the length.

		:param documents: The list of available documents.
		:type documents: list of :class:`~nlp.document.Document`
		:param summary: The summary constructed so far.
		:type summary: :class:`~summarization.summary.Summary`
		:param length: The maximum length of the document.
					   The length is inclusive.
		:type length: float

		:return: A list of documents that can be added to the summary.
		:rtype: list of :class:`~nlp.document.Document`
		"""

		documents = set(documents).difference(set(summary.documents))
		documents = [ document for document in documents if len(str(document)) <= length ]
		return documents

	def _get_next_document(self, documents, summary, query, matrix):
		"""
		Get the next document to add to the summary.

		:param documents: The list of available documents.
		:type documents: list of :class:`~nlp.document.Document`
		:param summary: The summary constructed so far.
		:type summary: :class:`~summarization.summary.Summary`
		:param query: The query used to select the documents.
		:type query: `~vsm.vector.Vector`
		:param matrix: The similarity matrix to use.
		:type matrix: dict

		:return: The next document to add to the summary, or `None` if there are no documents.
		:rtype: list of :class:`~nlp.document.Document` or None
		"""

		if not documents:
			return None

		scores = self._compute_scores(documents, summary, query, matrix)
		return max(scores.keys(), key=scores.get)

	def _compute_scores(self, documents, summary, query, matrix):
		"""
		Compute the scores of each candidate document.

		:param documents: The list of available documents.
		:type documents: list of :class:`~nlp.document.Document`
		:param summary: The summary constructed so far.
		:type summary: :class:`~summarization.summary.Summary`
		:param query: The query used to select the documents.
		:type query: `~vsm.vector.Vector`
		:param matrix: The similarity matrix to use.
		:type matrix: dict

		:return: The score of each document.
				 The key is the document itself and the value is the respective score.
		:rtype: dict
		"""

		query_scores = { document: matrix[document][query] for document in documents }

		"""
		If there are documents in the summary, calculate the redundancy scores.
		Otherwise, ignore the redundancy score.
		"""
		l  = self.l
		if summary.documents:
			redundancy_scores = { document: max(matrix[document][other] for other in summary.documents)
								  for document in documents }
		else:
			redundancy_scores = { document: 1 for document in documents }
			l = 1

		return { document: l * query_scores[document] - (1 - l) * redundancy_scores[document]
		 		   for document in documents }
