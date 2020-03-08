"""
Implementation of the Maximal Marginal Relevance model by Carbonell and Goldstein (1998).

This implementation calculates the burst of terms based on the given nutrition.

.. note::

	Implementation based on the algorithm presented in `The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries by Carbonell and Goldstein (1998) <https://dl.acm.org/doi/abs/10.1145/290941.291025>`_.
"""

import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '../../')
if path not in sys.path:
	sys.path.insert(1, path)

from ..scorers import scorer
from ..summary import Summary

from logger import logger

from vector.cluster.cluster import Cluster
from vector.vector_math import cosine

def MMR(collection, query=None, similarity_measure=cosine, l=0.5, iterations=3, min_score=0, document_scorer=None, similarity_table=None, timestamp=None, *args, **kwargs):
	"""
	The Maximal Marginal Relevance model takes in a collection of documents and a query.
	In a number of iterations, it repeatedly chooses the document that is most relevant to the query.
	Simultaneously, it does not favor documents that are very similar to those that have already been chosen.

	The MMR uses the following formula: λ sim(di, q) - (1 - λ) max(sim(di, dj))

	:param collection: The collection of documents.
	:type collection: list of :class:`~vector.vector.Vector`
	:param query: The query terms, represented as a document.
		If no query is provided, it is constructed using a centroid model, as described by the authors.
	:type query: :class:`~vector.vector.Vector`
	:param similarity_measure: The similarity measure to use to compare documents with the query and among themselves.
	:type similarity_measure: function
	:param l: The lambda parameter controls the expressiveness of the chosen documents.
		A small lambda diversifies the chosen documents.
		A high lambda returns more accurate documents.
	:type l: float
	:param iterations: The number of iterations that the model makes.
		A higher number of iterations could increase repetition.
	:type iterations: int
	:param min_score: The minimmum score that is required to add a document to a summary.
		Since cosine similarity is used, this threshold is bounded between -1 and 1.
		Both cases are possible when λ is 0 and 1 respectively.
		A score of -1 (λ = 0) is the case where the document is identical to another one in the summary.
		A score of 1 (λ = 1) is the case where the document is identical to the query.
	:type min_score: float
	:param document_scorer: The type of scorer used to rank documents.
		By default, no scoring is employed.
	:type document_scorer: :class:`~summarization.scorers.scorer.Scorer`
	:param similarity_table: The two-dimensional similarity table.
		The first rows and columns correspond to the collection's intra-similarity.
		The last row and column is the similarity between documents and the query.
		Normally this is not given, and calculated by the function itself.
		If it is given - usually for testing purposes - it is not re-calculated.
	:type similarity_table: list
	:param timestamp: The timestamp when the summary was created.
	:type timestamp: int

	:return: A list of documents that summarize the MMR.
		These documents are chosen from the given collection and constitute a summary.
	:rtype: :class:`~summarization.summary.Summary`
	"""

	if query is None:
		query = Cluster(vectors=collection).get_centroid()

	# TODO: take out the scorer and extend MMR, maybe. Current implementation looks quite dirty.
	document_scorer = scorer.Scorer() if document_scorer is None else document_scorer

	if similarity_table is None:
		"""
		Firstly, create the similarity table among documents.
		The last column is the similarity between each document and the query.
		"""
		similarity_entities = collection + [query]
		similarity_table = [ [0 for i in range(0, len(similarity_entities))] for j in range(0, len(similarity_entities))]
		for i in range(0, len(similarity_entities)): # one row for each document/query
			for j in range(i, len(similarity_entities)): # one column for each document/query
				similarity = similarity_measure(similarity_entities[i], similarity_entities[j])
				similarity_table[i][j] = similarity
				similarity_table[j][i] = similarity

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
