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

	def __init__(self, created_at=None, documents=None):
		"""
		Create the node.

		:param created_at: The timestamp when the node was created.
						   If the timestamp is not given, the current time is used.
		:type created_at: float
		:ivar documents: The list of documents in this node.
		:type documents: list of :class:`~nlp.document.Document`
		"""

		super(DocumentNode, self).__init__(created_at)
		self.documents = documents or [ ]

	def add(self, documents, *args, **kwargs):
		"""
		Add documents to the node.

		:param documents: A list of documents to add to the node.
		:type documents: list of :class:`~nlp.document.Document`
		"""

		self.documents.extend(documents)

	def get_all_documents(self, *args, **kwargs):
		"""
		Get all the documents in this node.

		:return: A list of documents in the node.
		:rtype: list of :class:`~nlp.document.Document`
		"""

		return self.documents

	def similarity(self, documents, *args, **kwargs):
		"""
		Compute the similarity between this node's documents and the centroid of the given documents.

		:param documents: The documents with which to compute similarity.
		:type documents: list of :class:`~nlp.document.Docunet`

		:return: The similarity between this node's documents and the given documents.
		:rtype: float
		"""

		centroid = Cluster(self.documents).centroid
		centroid.normalize()

		document_centroid = Cluster(documents).centroid
		document_centroid.normalize()

		return vector_math.cosine(centroid, document_centroid)

	def to_array(self):
		"""
		Export the document node as an associative array.

		:return: The document as an associative array.
		:rtype: dict
		"""

		return {
			'class': str(DocumentNode),
			'created_at': self.created_at,
			'documents': self.documents,
		}

	@staticmethod
	def from_array(array):
		"""
		Create an instance of the document node from the given associative array.

		:param array: The associative array with the attributes to create the document node.
		:type array: dict

		:return: A new instance of the document node with the same attributes stored in the object.
		:rtype: :class:`~summarization.timeline.nodes.document_node.DocumentNode`
		"""

		return DocumentNode(created_at=array.get('created_at'), documents=array.get('documents'))
