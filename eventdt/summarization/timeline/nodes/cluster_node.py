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
	A document node stores documents as a list.
	Comparisons are made with the centroid of these documents.
	"""

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
