"""
The Document Graph Summarizer (DGS) algorithm takes in documents and builds a summary.
The algorithm is not greedy and constructs a document graph, which it then splits into communities.
Considering each community to be a different facet, the algorithm picks documents from the largest communities.
In this way, the algorithm can maximize precision by minimizing redundancy.

.. note::

	Implementation based on the algorithm presented in `ELD: Event TimeLine Detection—A Participant-Based Approach to Tracking Events by Mamo et al. (2019) <https://dl.acm.org/doi/abs/10.1145/3342220.3344921>`_.
"""

import os
import sys

import networkx as nx

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from .summarization import SummarizationAlgorithm
from summarization import Summary

from vsm import vector_math
from vsm.clustering import Cluster

class DGS(SummarizationAlgorithm):
	"""
	The Document Graph Summarizer (DGS) is an algorithm that minimizes redundancy by splitting documents into communities.
	The algorithm receives documents and builds a summary from the largest communities to capture all facets.
	"""

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

		"""
		Validate the inputs.
		"""
		if length <= 0:
			raise ValueError(f"Invalid summary length {length}")

		"""
		Compute the query if need be.
		"""
		query = query or self._compute_query(documents)

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

	def _to_graph(self, documents):
		"""
		Convert the given documents to a networkx graph.
		The documents are converted to nodes.
		Weighted edges between them are created if their similarity exceeds 0.

		.. note::

			The weight of edges is `1 - similarity`.
			The higher the similarity, the less weight.
			Therefore more paths go through that edge.

		:param documents: The list of documents to convert into a graph.
		:type documents: list of :class:`~nlp.document.Document`

		:return: A graph with nodes representind documents and weighted edges between them.
		:rtype: :class:`~networkx.Graph`
		"""

		graph = nx.Graph()

		"""
		First add the nodes to the graph.
		"""
		for document in documents:
			graph.add_node(document, document=document)

		"""
		Add the weighted edges between the documents.
		"""
		for i, source in enumerate(documents):
			for target in documents[:i]:
				similarity = vector_math.cosine(source, target)
				if similarity > 0:
					graph.add_edge(source, target, weight=(1 - similarity))

		return graph
