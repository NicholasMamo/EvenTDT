"""
Queues are first in, first out (FIFO) data structures.
This implementation is based on lists.
Queue-specific functionality is introduced as functions.
"""

class Queue(object):
	"""
	The queue data structure is based on a list.
	The queue can take in any kind of data, including other queues.
	New elements are added to the queue at the end.

	:ivar queue: The queue data structure.
	:vartype queue: list
	"""

	def __init__(self, *args):
		"""
		Create the queue.
		The queue's data can be given as normal arguments.
		"""

		self.queue = [ *args ]

	def enqueue(self, *args):
		"""
		Add the given data to the queue.
		All arguments can be provided as arguments.

		:raises ValueError: When no data is given.
		"""

		if not (args):
			raise ValueError("No data given")

		self.queue.extend(args)

	def dequeue(self):
		"""
		Get the first element in the queue.
		If the queue is empty, `None` is returned instead

		:return: The first element in the queue.
		:rtype: object or None
		"""

		return self.queue.pop(0) if self.queue else None

	def dequeue_all(self):
		"""
		Dequeue all elements in the queue.
		Unlike the :func:`queues.queue.queue.Queue.empty` function, this function returns all of the queue's elements.

		:return: All the elements in the queue.
		:rtype: list
		"""

		elements = list(self.queue)
		self.empty()
		return elements

	def empty(self):
		"""
		Empty the queue.
		Unlike the :func:`queues.queue.queue.Queue.dequeue_all` function, this function returns nothing.
		"""

		self.queue = [ ]

	def length(self):
		"""
		Get the length of the queue.

		:return: The length of the queue.
		:rtype: int
		"""

		return len(self.queue)

	def head(self):
		"""
		Get the first element entered into the queue without removing it.
		If the queue is empty, `None` is returned instead

		:return: The oldest element in the queue.
		:rtype: object or None
		"""

		return self.queue[0] if self.queue else None

	def tail(self):
		"""
		Get the last element entered into the queue without removing it.
		If the queue is empty, `None` is returned instead

		:return: The newest element in the queue.
		:rtype: object or None
		"""

		return self.queue[-1] if self.queue else None
