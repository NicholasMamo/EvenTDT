"""
Run unit tests on the Queue class
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.append(path)

from libraries.queues.queue.queue import Queue

class TestQueue(unittest.TestCase):
	"""
	Test the Queue class
	"""

	def test_init(self):
		"""
		Test the Queue constructor
		"""

		q = Queue()
		self.assertEqual(q.length(), 0)

		q = Queue([1, 2, 3])
		self.assertEqual(q.length(), 3)

		q = Queue(["abc"])
		self.assertEqual(q.length(), 1)

	def test_queue_functions(self):
		"""
		Test the Queue functionalities
		"""

		q = Queue()
		q.enqueue(1)
		self.assertEqual(q.length(), 1)

		q.enqueue(2)
		self.assertEqual(q.dequeue(), 1)
		self.assertEqual(q.dequeue(), 2)

		self.assertEqual(q.dequeue(), None)

		q.enqueue(1)
		q.enqueue(2)
		q.enqueue(3)
		self.assertEqual(q.length(), 3)
		q.empty()
		self.assertEqual(q.length(), 0)

		q.enqueue(3)
		q.enqueue(1)
		q.enqueue(2)
		self.assertEqual(q.length(), 3)
		self.assertEqual(q.dequeue_all(), [3, 1, 2])
		self.assertEqual(q.length(), 0)
