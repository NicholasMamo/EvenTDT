"""
Timelines are made up of nodes.
Each node stores documents that can be summarized.
Moreover, nodes provide functionality to facilitate timeline tasks.
"""

from abc import ABC, abstractmethod
import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from objects.exportable import Exportable

class Node(Exportable):
	"""
	Nodes are the basic component of a timeline.
	Timelines contain an ordered list of these nodes.

	Nodes can store documents in different ways.
	For example, they can be stored as simple documents.
	Alternatively, they can be stored as clusters.

	Nodes must offer certain functionality to facilitate the timeline construction.

	.. note::

		The inputs for the :func:`~summrization.timeline.nodes.node.Node.add` and :func:`~summrization.timeline.nodes.node.Node.similarity` function should be the same.
		This is necessary even if an input is used in :func:`~summrization.timeline.nodes.node.Node.add`, but not in :func:`~summrization.timeline.nodes.node.Node.similarity`.
		This is because the :func:`~summarization.timeline.timeline.Timeline.add` function passes all arguments and keyword arguments in the same way.

	:ivar created_at: The timestamp when the node was created.
	:vartype created_at: float
	"""

	def __init__(self, created_at):
		"""
		Create the node.

		:param created_at: The timestamp when the node was created.
		:type created_at: float
		"""

		self.created_at = created_at

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

	@abstractmethod
	def get_all_documents(self, *args, **kwargs):
		"""
		Get all the documents in this node.

		The implementation differs according to what the node stores.
		However, they must all have functionality to return a list of documents.

		:return: A list of documents in the node.
		:rtype: list of :class:`~nlp.document.Document`
		"""

		pass

	def expired(self, expiry, timestamp):
		"""
		Check whether the node has expired.
		A node has expired if a certain time has passed.
		A node can still absorb documents if it has expired.
		If a node has not expired, another one cannot be created.

		:param expiry: The lifetime of a node before it is said to expire.
					   It is measured in seconds.
		:type expiry: float
		:param timestamp: The current timestamp.
		:type timestamp: float

		:raises ValueError: When the expiry is negative.
		"""

		if expiry < 0:
			raise ValueError(f"The expiry cannot be negative: received {expiry}")

		return timestamp - self.created_at >= expiry
