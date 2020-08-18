"""
The :class:`~summarization.timeline.nodes.topical_cluster_node.TopicalClusterNode` is based on the :class:`~summarization.timeline.nodes.cluster_node.ClusterNode`.
Like the :class:`~summarization.timeline.nodes.cluster_node.ClusterNode`, it revolves around :class:`~vsm.clustering.cluster.Cluster` instances.
However, it also associates with each :class:`~vsm.clustering.cluster.Cluster` a topic, represented as a :class:`~vsm.vector.Vector`.

The idea behind the :class:`~summarization.timeline.nodes.topical_cluster_node.TopicalClusterNode` is that the topics, which are generated by a :ref:`TDT algorithm <tdt_algorithms>`, represent more accurately what the :class:`~vsm.clustering.cluster.Cluster` is about.
Thereefore the :func:`~summarization.timeline.nodes.topical_cluster_node.TopicalClusterNode.similarity` function ignores the :class:`~vsm.clustering.cluster.Cluster` completely and focuses instead on the topics.
"""

from . import ClusterNode

import importlib
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from objects.exportable import Exportable
from summarization.timeline.nodes import Node
from vsm import vector_math

class TopicalClusterNode(ClusterNode):
	"""
	The :class:`~summarization.timeline.nodes.topical_cluster_node.TopicalClusterNode` class maintains in its state two lists:

	1. A list of :class:`~vsm.clustering.cluster.Cluster` instances, and
	2. An associated list of :class:`~vsm.vector.Vector` instances that represent topics.

	The :func:`~summarization.timeline.nodes.topical_cluster_node.TopicalClusterNode.similarity` function ignores the :class:`~vsm.clustering.cluster.Cluster` instances and focuses only on the topics.

	:ivar topics: The list of topics in this node.
				  Each topic is a vector and corresponds to a cluster.
	:type topics: list of :class:`~vsm.vector.Vector`
	"""

	def __init__(self, created_at, clusters=None, topics=None):
		"""
		Create the node with, optionally, an initial list of :class:`~vsm.clustering.cluster.Cluster` instances and topics.

		:param created_at: The timestamp when the node was created.
		:type created_at: float
		:param clusters: The initial list of clusters in this node.
		:type clusters: list of :class:`~vsm.clustering.cluster.Cluster`
		:param topics: The initial listo f topics in this node.
		:type topics: list of :class:`~vsm.vector.Vector`

		:raises ValueError: When an unequal number of :class:`~vsm.clustering.cluster.Cluster` instances and topics are provided.
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
		Add a new :class:`~vsm.clustering.cluster.Cluster` and its associated topic to the node.

		:param cluster: The cluster to add to the node.
		:type cluster: :class:`~vsm.clustering.cluster.Cluster`
		:param topic: The topical representation of the cluster.
		:type topic: :class:`~vsm.vector.Vector`
		"""

		super(TopicalClusterNode, self).add(cluster)
		self.topics.append(topic)

	def similarity(self, cluster, topic, *args, **kwargs):
		"""
		Compute the similarity between this node and the given topic.
		This function tries to match the new topic with any topic already in the node.
		The returned similarity is the highest pairwise similarity.

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
		Create :class:`~summarization.timeline.nodes.topical_cluster_node.TopicalClusterNode` from the given associative array.

		:param array: The associative array with the attributes to create the :class:`~summarization.timeline.nodes.topical_cluster_node.TopicalClusterNode`.
		:type array: dict

		:return: A new instance of the :class:`~summarization.timeline.nodes.topical_cluster_node.TopicalClusterNode` with the same attributes stored in the object.
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
