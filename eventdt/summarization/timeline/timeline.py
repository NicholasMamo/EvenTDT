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

	:ivar nodes: The list of nodes in the timeline.
	:vartype nodes: :class:`~summarization.timeline.nodes.node.Node`
	:ivar node_type: The type of nodes to create in the timeline.
	:vartype node_type: :class:`~summarization.timeline.nodes.node.Node`
	"""

	def __init__(self, node_type):
		"""
		Create the timeline with an empty set of nodes.

		:param node_type: The type of nodes to create in the timeline.
		:type node_type: :class:`~summarization.timeline.nodes.node.Node`
		"""

		self.nodes = [ ]
		self.node_type = node_type

	def _create(self, created_at=None, *args, **kwargs):
		"""
		Create a new node on the timeline.
		Any arguments and keyword arguments are passed on to the :func:`~summarization.timeline.nodes.node.Node.__init__` method.

		:param created_at: The timestamp when the node was created.
						   If the timestamp is not given, the current time is used.
		:type created_at: float
		"""

		self.nodes.append(self.node_type(created_at=created_at, *args, **kwargs))
