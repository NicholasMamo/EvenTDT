"""
A timeline is a succession of :class:`~summarization.timeline.nodes.node.Node`.
Each node stores information about what happened in that period of time.
The timeline groups these nodes together.
"""

class Timeline(object):
	"""
	The timeline stores a list of nodes and provides functionality to convert them into summaries.
	More importantly, the timeline provides functionality to construct the timeline.
	This includes redundancy management.

	:ivar nodes: The list of nodes in the timeline.
	:vartype nodes: :class:`~summarization.timeline.nodes.node.Node`
	"""

	def __init__(self):
		"""
		Create the timeline with an empty set of nodes.
		"""

		self.nodes = [ ]
