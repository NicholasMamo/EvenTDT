"""
A topical cluster node stores clusters and vectorial representations of topics.
"""

from . import ClusterNode

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from vsm import vector_math

class TopicalClusterNode(ClusterNode):
	"""
	A cluster node stores clusters instead of documents.
	Comparisons are made with topics, not the clusters.
	The clusters are only used to store documents.

	:ivar topics: The list of topics in this node.
				  Each topic is a vector and corresponds to a cluster.
	:type clusters: list of :class:`~vsm.vector.Vector`
	"""

	def __init__(self, created_at=None):
		"""
		Create the node.

		:param created_at: The timestamp when the node was created.
						   If the timestamp is not given, the current time is used.
		:type created_at: float
		"""

		super(TopicalClusterNode, self).__init__(created_at)
		self.topics = [ ]

	
