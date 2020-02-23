"""
Queues are first in, first out (FIFO) data structures.
This implementation is based on lists.
Queue-specific functionality is introduced as functions.
"""

class Queue(object):
	"""
	The queue data structure is based on a list.
	In its simplest form, the queue only includes function to store and return data.
	"""

	def __init__(self, data=None):
		"""
		Create the queue with optional initial data.
		If no data is given, an empty list is initialized.

		:param data: The initial data in the queue.
		:type data: list
		"""

		self._q = data if data is not None else list()

	def enqueue(self, data):
		"""
		Add the given data - a list or a single value - to the queue.
		If a list is provided, add all elements sequentially.

		:param data: The data to enqueue.
		:type data: list
		"""

		if type(data) == list:
			"""
			If a list is provided, add each element to the queue.
			"""
			for element in data:
				self._q.append(element)
		else:
			self._q.append(data)

	def dequeue(self):
		"""
		Get the first element in the queue.

		:return: The oldest element in the queue.
		:rtype: :class:`object` or None
		"""

		return self._q.pop(0) if self.length() > 0 else None

	def dequeue_all(self):
		"""
		Dequeue all elements in the queue.

		:return: All the elements in the queue.
		:rtype: list
		"""

		elements = []
		for i in range(0, self.length()):
			elements.append(self.dequeue())
		return elements

	def empty(self):
		"""
		Empty the queue.
		"""

		self._q = []

	def length(self):
		"""
		Get the length of the queue.

		:return: The length of the queue.
		:rtype: int
		"""

		return len(self._q)

	def tail(self):
		"""
		Get the last element entered into the queue without removing it.

		:return: The newest element in the queue.
		:rtype: :class:`object` or None
		"""

		return self._q[self.length() - 1] if self.length() > 0 else None

	def head(self):
		"""
		Get the first element entered into the queue without removing it.

		:return: The oldest element in the queue.
		:rtype: :class:`object` or None
		"""

		return self._q[0] if self.length() > 0 else None
