"""
A document node stores documents as a list.
"""

from .node import Node

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from vsm import vector_math
from vsm.clustering import Cluster

class DocumentNode(Node):
	"""
	A document node stores documents as a list.
	Comparisons are made with the centroid of these documents.

	:ivar documents: The list of documents in this node.
	:type documents: list of :class:`~nlp.document.Document`
	"""

	def __init__(self, created_at=None):
		"""
		Create the node.

		:param created_at: The timestamp when the node was created.
						   If the timestamp is not given, the current time is used.
		:type created_at: float
		"""

		super(DocumentNode, self).__init__(created_at)
		self.documents = [ ]

	def add(self, documents, *args, **kwargs):
		"""
		Add documents to the node.

		:param documents: A list of documents to add to the node.
		:type documents: list of :class:`~nlp.document.Document`
		"""

		self.documents.extend(documents)

	def similarity(self, document, *args, **kwargs):
		"""
		Compute the similarity between this node's documents and the given document.

		:param document: The document with which to compute similarity.
		:type document: :class:`~vsm.vector.Vector`

		:return: The similarity between this node's documents and the given document.
		:rtype: float
		"""

		centroid = Cluster(self.documents).centroid
		centroid.normalize()
		return vector_math.cosine(centroid, document)
