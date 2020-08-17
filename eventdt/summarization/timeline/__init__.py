"""
A timeline is a succession of :class:`~summarization.timeline.nodes.node.Node`.
Each node stores information about what happened in that period of time.
The timeline groups these nodes together.
"""

import importlib
import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from objects.exportable import Exportable

class Timeline(Exportable):
	"""
	The timeline stores a list of nodes and provides functionality to convert them into summaries.
	More importantly, the timeline provides functionality to construct the timeline.
	This includes redundancy management.

	Incoming documents are added automatically to the latest node if it has not expired.
	At any time, the timeline only ever has one non-expired, or active, node.
	If there are no active nodes, the incoming documents can either be absorbed by an expired node, or go into a new node.

	:ivar nodes: The list of nodes in the timeline.
	:vartype nodes: :class:`~summarization.timeline.nodes.node.Node`
	:ivar node_type: The type of nodes to create in the timeline.
	:vartype node_type: :class:`~summarization.timeline.nodes.node.Node`
	:ivar expiry: The time in seconds that it takes for a node to expire.
				  Expired nodes do not automatically absorb documents.
				  If the expiry is 0, new documents immediately join a new node unless they are absorbed.
	:vartype expiry: float
	:ivar min_similarity: The minimum similarity between incoming documents and a node to be absorbed by it.
						  This value is inclusive.
	:vartype similarity: float
	:ivar max_time: The maximum time in seconds to look back when deciding whether a node should absorb a new topic.
					The comparison is made with the node's `created_at` instance variable.
					This value is inclusive.
	:vartype max_time: float
	"""

	def __init__(self, node_type, expiry, min_similarity, max_time=600, nodes=None):
		"""
		Create the timeline with an empty set of nodes.

		:param node_type: The type of nodes to create in the timeline.
		:type node_type: :class:`~summarization.timeline.nodes.node.Node`
		:param expiry: The time in seconds that it takes for a node to expire.
					   Expired nodes do not automatically absorb documents.
					   If the expiry is 0, new documents immediately join a new node unless they are absorbed.
		:type expiry: float
		:param min_similarity: The minimum similarity between incoming documents and a node to be absorbed by it.
							   This value is inclusive.
		:type similarity: float
		:param max_time: The maximum time in seconds to look back when deciding whether a node should absorb a new topic.
						 The comparison is made with the node's `created_at` instance variable.
						 This value is inclusive.
		:type max_time: float
		:param nodes: The initial list of nodes in the timeline.
		:type nodes: :class:`~summarization.timeline.nodes.node.Node`

		:raises ValueError: When the expiry is negative.
		:raises ValueError: When the minimum similarity is not between 0 and 1.
		"""

		"""
		Validate the parameters.
		"""

		if expiry < 0:
			raise ValueError(f"The node expiry cannot be negative: received {expiry}")

		if not 0 <= min_similarity <= 1:
			raise ValueError(f"The minimum similarity must be between 0 and 1: received {min_similarity}")

		self.nodes = nodes or [ ]
		self.node_type = node_type
		self.expiry = expiry
		self.min_similarity = min_similarity
		self.max_time = max_time

	def add(self, timestamp=None, *args, **kwargs):
		"""
		Add documents to a node.
		This function first tries to identify if there is an active node.
		If there isn't, it tries to find a node that can absorb the documents.
		This process is performed in reverse.
		If it doesn't, a new node is created.

		All arguments and keyword arguments are passed on to the :func:`~summarization.timeline.nodes.node.Node.add` and :func:`~summarization.timeline.nodes.node.Node.similarity` methods.

		:param timestamp: The current timestamp.
						  If the timestamp is not given, the current time is used.
		:type timestamp: float
		"""

		timestamp = time.time() if timestamp is None else timestamp

		"""
		If there are nodes and the latest one is still active—it hasn't expired—add the documents to it.
		"""
		if self.nodes and not self.nodes[-1].expired(self.expiry, timestamp):
			self.nodes[-1].add(*args, **kwargs)
			return

		"""
		Go through the nodes backwards and see if any node absorbs the documents.
		"""
		for node in self.nodes[::-1]:
			if timestamp - node.created_at <= self.max_time and node.similarity(*args, **kwargs) >= self.min_similarity:
				node.add(*args, **kwargs)
				return

		"""
		If no node absorbs the documents, create a new node and add them to it.
		"""
		node = self._create(created_at=timestamp)
		node.add(*args, **kwargs)
		self.nodes.append(node)

	def _create(self, created_at, *args, **kwargs):
		"""
		Create a new node on the timeline.
		Any arguments and keyword arguments are passed on to the :func:`~summarization.timeline.nodes.node.Node.__init__` method.

		:param created_at: The timestamp when the node was created.
		:type created_at: float

		:return: The created node.
		:rtype: :class:`~summarization.timeline.nodes.node.Node`
		"""

		return self.node_type(created_at=created_at, *args, **kwargs)

	def to_array(self):
		"""
		Export the timeline as an associative array.

		:return: The timeline as an associative array.
		:rtype: dict
		"""

		return {
			'class': str(Timeline),
			'node_type': str(self.node_type),
			'expiry': self.expiry,
			'min_similarity': self.min_similarity,
			'nodes': [ node.to_array() for node in self.nodes ],
		}

	@staticmethod
	def from_array(array):
		"""
		Create an instance of the timeline from the given associative array.

		:param array: The associative array with the attributes to create the timeline.
		:type array: dict

		:return: A new instance of the timeline with the same attributes stored in the object.
		:rtype: :class:`~summarization.timeline.nodes.node_node.ClusterNode`
		"""

		nodes = [ ]
		for node in array.get('nodes'):
			module = importlib.import_module(Exportable.get_module(node.get('class')))
			cls = getattr(module, Exportable.get_class(node.get('class')))
			nodes.append(cls.from_array(node))

		module = importlib.import_module(Exportable.get_module(array.get('node_type')))
		node_type = getattr(module, Exportable.get_class(array.get('node_type')))

		return Timeline(node_type=node_type, expiry=array.get('expiry'),
						min_similarity=array.get('min_similarity'), nodes=nodes)
