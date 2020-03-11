"""
Timelines are made up of nodes.
Each node stores documents that can be summarized.
Moreover, nodes provide functionality to facilitate timeline tasks.
"""

from abc import ABC, abstractmethod
import time

class Node(ABC):
	"""
	Nodes are the basic component of a timeline.
	Timelines contain an ordered list of these nodes.

	Nodes can store documents in different ways.
	For example, they can be stored as simple documents.
	Alternatively, they can be stored as clusters.

	Nodes must offer certain functionality to facilitate the timeline construction.

	:ivar created_at: The timestamp when the node was created.
	:vartype created_at: float
	"""

	def __init__(self, created_at=None):
		"""
		Create the node.

		:param created_at: The timestamp when the node was created.
						   If the timestamp is not given, the current time is used.
		:type created_at: float
		"""

		self.created_at = created_at or time.time()

	@abstractmethod
	def add(self, *args, **kwargs):
		"""
		Add documents to the node.
		"""

		pass

	@abstractmethod
	def similarity(self, *args, **kwargs):
		"""
		Compute the similarity between this node and a given object.

		:return: The similarity between this node and the given object.
		:rtype: float
		"""

		pass

	def expired(self, expiry, timestamp=None):
		"""
		Check whether the node has expired.
		A node has expired if a certain time has passed.
		A node can still absorb documents if it has expired.
		If a node has not expired, another one cannot be created.

		:param expiry: The lifetime of a node before it is said to expire.
					   It is measured in timestamps.
		:type expiry: float
		:param timestamp: The current timestamp.
						  If the timestamp is not given, the current time is used.
		:type timestamp: float
		"""

		timestamp = timestamp or time.time()
		return timestamp - self.created_at >= expiry
