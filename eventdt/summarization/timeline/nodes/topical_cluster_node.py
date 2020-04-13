"""
A topical cluster node stores clusters and vectorial representations of topics.
"""

from . import ClusterNode

import importlib
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from objects.exportable import Exportable
from vsm import vector_math

class TopicalClusterNode(ClusterNode):
	"""
	A cluster node stores clusters instead of documents.
	Comparisons are made with topics, not the clusters.
	The clusters are only used to store documents.

	:ivar topics: The list of topics in this node.
				  Each topic is a vector and corresponds to a cluster.
	:type topics: list of :class:`~vsm.vector.Vector`
	"""

	def __init__(self, created_at, clusters=None, topics=None):
		"""
		Create the node.

		:param created_at: The timestamp when the node was created.
		:type created_at: float
		:param clusters: The initial list of clusters in this node.
		:type clusters: list of :class:`~vsm.clustering.cluster.Cluster`
		:param topics: The initial listo f topics in this node.
		:type topics: list of :class:`~vsm.vector.Vector`

		:raises ValueError: When an unequal number of clusters are provided.
		"""

		"""
		The number of clusters and topics must be the same.
		If they aren't, or only the topics or only the clusters are given, raise a ValueError.
		"""
		if (clusters and topics and len(clusters) != len(topics) or
			(clusters and not topics) or (topics and not clusters)):
			clusters = clusters or [ ]
			topics = topics or [ ]
			raise ValueError(f"The number of clusters and topics must be the same, received { len(clusters) } and { len(topics) } respectively")

		super(TopicalClusterNode, self).__init__(created_at, clusters=clusters)
		self.topics = topics or [ ]

	def add(self, cluster, topic, *args, **kwargs):
		"""
		Add documents to the node.

		:param cluster: The cluster to add to the node.
		:type cluster: :class:`~vsm.clustering.cluster.Cluster`
		:param topic: The topical representation of the cluster.
		:type topic: :class:`~vsm.vector.Vector`
		"""

		super(TopicalClusterNode, self).add(cluster)
		self.topics.append(topic)

	def similarity(self, cluster, topic, *args, **kwargs):
		"""
		Compute the similarity between this node and a given topic.
		The returned similarity is the maximum similarity between the given topic and any topic in the node.

		:param cluster: The cluster to which the topic belongs.
		:type cluster: :class:`~vsm.clustering.cluster.Cluster`
		:param topic: The topic with which to compute similarity.
		:type topic: :class:`~vsm.vector.Vector`

		:return: The similarity between this node and the given topic.
		:rtype: float
		"""

		if self.topics:
			return max(vector_math.cosine(topic, other) for other in self.topics)

		return 0

	def to_array(self):
		"""
		Export the topical cluster node as an associative array.

		:return: The topical cluster node as an associative array.
		:rtype: dict
		"""

		return {
			'class': str(TopicalClusterNode),
			'created_at': self.created_at,
			'clusters': [ cluster.to_array() for cluster in self.clusters ],
			'topics': [ topic.to_array() for topic in self.topics ],
		}

	@staticmethod
	def from_array(array):
		"""
		Create an instance of the cluster node from the given associative array.

		:param array: The associative array with the attributes to create the topical cluster node.
		:type array: dict

		:return: A new instance of the topical cluster node with the same attributes stored in the object.
		:rtype: :class:`~summarization.timeline.nodes.topical_cluster_node.TopicalClusterNode`
		"""

		clusters = [ ]
		for cluster in array.get('clusters'):
			module = importlib.import_module(Exportable.get_module(cluster.get('class')))
			cls = getattr(module, Exportable.get_class(cluster.get('class')))
			clusters.append(cls.from_array(cluster))

		topics = [ ]
		for topic in array.get('topics'):
			module = importlib.import_module(Exportable.get_module(topic.get('class')))
			cls = getattr(module, Exportable.get_class(topic.get('class')))
			topics.append(cls.from_array(topic))

		return TopicalClusterNode(created_at=array.get('created_at'), clusters=clusters, topics=topics)
