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

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from .summarization import SummarizationAlgorithm
from summarization import Summary

from vsm import vector_math

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
