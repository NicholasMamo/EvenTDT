"""
A finite queue is similar to a normal queue, but it may be shut down.
"""

from .queue import Queue

class FiniteQueue(Queue):
	"""
	The FiniteQueue builds on a normal queue, but it may be shut down.
	"""

	def __init__(self, data=[]):
		"""
		Create the Queue with optional initial data.
		"""
