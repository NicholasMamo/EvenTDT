"""
A cluster node stores clusters instead of documents.
"""

from .node import Node

import importlib
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from objects.exportable import Exportable
from vsm import vector_math
from vsm.clustering import Cluster

class ClusterNode(Node):
	"""
	A cluster node stores clusters instead of documents.
	Comparisons are made with each cluster's centroid.

	:ivar clusters: The list of clusters in this node.
	:vartype clusters: list of :class:`~vsm.clustering.cluster.Cluster`
	"""

	def __init__(self, created_at=None, clusters=[ ]):
		"""
		Create the node.

		:param created_at: The timestamp when the node was created.
						   If the timestamp is not given, the current time is used.
		:type created_at: float
		:param clusters: The initial list of clusters in this node.
		:type clusters: list of :class:`~vsm.clustering.cluster.Cluster`
		"""

		super(ClusterNode, self).__init__(created_at)
		self.clusters = clusters or [ ]

	def add(self, cluster, *args, **kwargs):
		"""
		Add documents to the node.

		:param cluster: The cluster to add to the node.
		:type cluster: :class:`~vsm.clustering.cluster.Cluster`
		"""

		self.clusters.append(cluster)

	def get_all_documents(self, *args, **kwargs):
		"""
		Get all the documents in this node.

		:return: A list of documents in the node.
		:rtype: list of :class:`~nlp.document.Document`
		"""

		return [ document for cluster in self.clusters for document in cluster.vectors ]

	def similarity(self, cluster, *args, **kwargs):
		"""
		Compute the similarity between this node and a given cluster.
		The returned similarity is the maximum similarity between the given cluster and any cluster in the node.

		:param cluster: The cluster with which to compute similarity.
		:type cluster: :class:`~vsm.clustering.cluster.Cluster`

		:return: The similarity between this node and the given cluster.
		:rtype: float
		"""

		if self.clusters:
			return max(vector_math.cosine(cluster.centroid, other.centroid) for other in self.clusters)

		return 0

	def to_array(self):
		"""
		Export the cluster node as an associative array.

		:return: The cluster node as an associative array.
		:rtype: dict
		"""

		return {
			'class': str(ClusterNode),
			'created_at': self.created_at,
			'clusters': [ cluster.to_array() for cluster in self.clusters ],
		}

	@staticmethod
	def from_array(array):
		"""
		Create an instance of the cluster node from the given associative array.

		:param array: The associative array with the attributes to create the cluster node.
		:type array: dict

		:return: A new instance of the cluster node with the same attributes stored in the object.
		:rtype: :class:`~summarization.timeline.nodes.cluster_node.ClusterNode`
		"""

		clusters = [ ]
		for cluster in array.get('clusters'):
			module = importlib.import_module(Exportable.get_module(cluster.get('class')))
			cls = getattr(module, Exportable.get_class(cluster.get('class')))
			clusters.append(cls.from_array(cluster))

		return ClusterNode(created_at=array.get('created_at'), clusters=clusters)
