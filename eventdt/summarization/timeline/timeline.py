"""
A timeline is a succession of :class:`~summarization.timeline.nodes.node.Node`.
Each node stores information about what happened in that period of time.
The timeline groups these nodes together.
"""

class Timeline():
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
	"""

	def __init__(self, node_type, expiry, min_similarity):
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

		self.nodes = [ ]
		self.node_type = node_type
		self.expiry = expiry
		self.min_similarity = min_similarity

	def _create(self, created_at=None, *args, **kwargs):
		"""
		Create a new node on the timeline.
		Any arguments and keyword arguments are passed on to the :func:`~summarization.timeline.nodes.node.Node.__init__` method.

		:param created_at: The timestamp when the node was created.
						   If the timestamp is not given, the current time is used.
		:type created_at: float
		"""

		self.nodes.append(self.node_type(created_at=created_at, *args, **kwargs))
