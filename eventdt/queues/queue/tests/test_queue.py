"""
Test the functionality of the Wikipedia extrapolator.
"""

import os
import random
import re
import string
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from queues import Queue

class TestQueue(unittest.TestCase):
	"""
	Test the implementation of the Queue.
	"""

	def test_empty_init(self):
		"""
		Test that when creating a queue without any data, an empty list is generated instead.
		"""

		queue = Queue()
		self.assertEqual([ ], queue.queue)

	def test_init_with_data(self):
		"""
		Test that when a queue is created with data, all of it is saved.
		"""

		queue = Queue(1)
		self.assertEqual([ 1 ], queue.queue)

	def test_init_with_multiple_data(self):
		"""
		Test that when a queue is created with data, all of it is saved.
		"""

		queue = Queue(1, True, 'a')
		self.assertEqual([ 1, True, 'a' ], queue.queue)

	def test_init_with_list_data(self):
		"""
		Test that when creating a queue with a list, the list is saved as a single element.
		"""

		queue = Queue([ 1, True, 'a' ])
		self.assertEqual([[ 1, True, 'a' ]], queue.queue)

	def test_enqueue_no_data(self):
		"""
		Test that when enqueuing no data, the queue remains as it was in the beginning.
		"""

		data = list(range(0, 10))
		queue = Queue(*data)
		self.assertEqual(data, queue.queue)
		self.assertRaises(ValueError, queue.enqueue)

	def test_enqueue_data(self):
		"""
		Test that when enqueuing a single element, it is enqueued as an element.
		"""

		data = list(range(0, 10))
		queue = Queue(*data)
		self.assertEqual(data, queue.queue)
		queue.enqueue(11)
		self.assertEqual(data + [ 11 ], queue.queue)

	def test_enqueue_multiple_data(self):
		"""
		Test that when enqueuing multiple elements, all of them are enqueued.
		"""

		data = list(range(0, 10))
		queue = Queue(*data)
		self.assertEqual(data, queue.queue)
		queue.enqueue(*list(range(10, 12)))
		self.assertEqual(data + list(range(10, 12)), queue.queue)

	def test_enqueue_list(self):
		"""
		Test that when enqueuing a list, the list itself is enqueued.
		"""

		data = list(range(0, 10))
		queue = Queue(*data)
		self.assertEqual(data, queue.queue)
		queue.enqueue(list(range(10, 12)))
		self.assertEqual(data + [list(range(10, 12))], queue.queue)
