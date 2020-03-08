"""
The Maximal Marginal Relevance (MMR) algorithm takes in documents and a query and builds a summary.
This summary has the ideal property of being relevant to the query and non-redundant.

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
	"""

	def summarize(self, documents, length, query=None, l=0.5, *args, **kwargs):
		"""
		Summarize the given documents.

		.. note::

			The algorithm assumes that the documents are already unique sentences.
			Therefore the summary is a selection of the given documents.

		:param documents: The list of documents to summarize.
		:type documents: list of :class:`~nlp.document.Document`
		:param length: The maximum length of the summary.
		:type length: float
		:param query: The query around which to build the summary.
					  If no query is given, the summary is built around the centroid of documents.
		:type query: :class:`~vsm.vector.Vector` or None
		:param l: The :math:`\\lambda` parameter, which must be between 0 and 1.
				  When :math:`\\lambda` is 0, only relevance to the query is considered.
				  When :math:`\\lambda` is 1, only non-redundancy is considered.
				  By default, the algorithm assigns equal weight to relevance and non-redundancy.
		:type l: float

		:return: The summary of the documents.
		:rtype: :class:`~summarization.summary.Summary`

		:raises ValueError: When the summary length is not positive.
		:raises ValueError: When lambda is not between 0 and 1.
		"""

		"""
		Validate the inputs.
		"""

		if length <= 0:
			raise ValueError(f"Invalid summary length {length}")

		if not 0 <= l <= 1:
			raise ValueError(f"Invalid lambda value {l}")

		query = query or self._compute_query(documents)
		similarity_matrix = self._compute_similarity_matrix(documents, query)

		summary = [] # the list of chosen documents
		"""
		Repeatedly choose the most relevant document while minimizing redundancy.
		"""
		for i in range(0, iterations):
			"""
			In the first iteration, simply pick the most relevant document.
			Otherwise, a longer route has to be taken.
			"""
			if len(summary) == 0:
				candidate_documents = {}
				for d in [ d for d in range(0, len(collection)) ]:
					query_similarity = similarity_table[d][len(collection)]
					score = document_scorer.score(collection[d])
					candidate_documents[d] = query_similarity * score
				most_similar_index = max(candidate_documents.items(), key=lambda d: d[1])[0]
				# most_similar_index = max([document_scorer.score(collection[d]) for d in range(0, len(collection))], key=lambda d : similarity_table[d][len(collection)])
				summary.append(most_similar_index)
			else:
				"""
				The formula has two components.
				The first component finds the similarity between the document and the query.
				The second component finds the maximum similarity between the document and each document in the summary.

				To simplify the approach, this is enclosed in a loop.
				"""

				candidate_documents = {}
				for d in [ d for d in range(0, len(collection)) if d not in summary ]:
					query_similarity = similarity_table[d][len(collection)]
					summary_document = max([sd for sd in summary], key=lambda sd : similarity_table[d][sd])
					summary_document_similarity = similarity_table[d][summary_document]
					score = document_scorer.score(collection[d])
					candidate_documents[d] = l * query_similarity - (1 - l) * summary_document_similarity * score

				if len(candidate_documents) == 0:
					break

				"""
				Only add the document if its score is higher than the given threshold.
				Note that a summary will always have at least one document - this is in the 'else' part.
				"""
				document, max_score = max(candidate_documents.items(), key=lambda d: d[1])
				if max_score >= min_score:
					summary.append(document)
					# summary.append(max(candidate_documents.items(), key=lambda d: d[1])[0])
				else:
					break

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
