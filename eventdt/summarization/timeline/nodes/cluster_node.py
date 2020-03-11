"""
A cluster node stores clusters instead of documents.
"""

from .node import Node

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from vsm import vector_math
from vsm.clustering import Cluster

class ClusterNode(Node):
	"""
	A cluster node stores clusters instead of documents.
	Comparisons are made with each cluster's centroid.

	:ivar clusters: The list of clusters in this node.
	:type clusters: list of :class:`~vsm.clustering.cluster.Cluster`
	"""

	def __init__(self, created_at=None):
		"""
		Create the node.

		:param created_at: The timestamp when the node was created.
						   If the timestamp is not given, the current time is used.
		:type created_at: float
		"""

		super(ClusterNode, self).__init__(created_at)
		self.clusters = [ ]

	def add(self, *args, **kwargs):
		"""
		Add documents to the node.
		"""

		pass

	def similarity(self, *args, **kwargs):
		"""
		Compute the similarity between this node and a given object.

		:return: The similarity between this node and the given object.
		:rtype: float
		"""

		pass
