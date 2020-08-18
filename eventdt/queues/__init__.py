"""
EvenTDT collects tweets and processes them.
In-between collecting and processing, the tweets go into a queue data structure.
Later on, a :ref:`consumer <consumers>` picks this data and processes it in the same order as it was received.
This functionality is implemented in a special class: the :class:`~queues.Queue`.

The Queue Class
===============

The :class:`~queues.Queue` is a first in, first out (FIFO) data structure.
In EvenTDT, this implementation is based on lists and queue-specific functionality is introduced as functions.
"""

class Queue(object):
	"""
	The :class:`~queues.Queue` data structure encapsulates a list with additional functions that mimick the workings of a queue.
	The :class:`~queues.Queue` can take in any kind of data, including other :class:`~queues.Queue` instances.
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
		"""

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
		Unlike the :func:`~queues.Queue.empty` function, this function returns all of the queue's elements.

		:return: All the elements in the queue.
		:rtype: list
		"""

		elements = list(self.queue)
		self.empty()
		return elements

	def empty(self):
		"""
		Empty the queue.
		Unlike the :func:`~queues.Queue.dequeue_all` function, this function returns nothing.
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
