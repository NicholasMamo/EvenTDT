"""
Test the functionality of the Zhao et al. consumer.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from queues import Queue
from queues.consumers import ZhaoConsumer

class TestZhaoConsumer(unittest.TestCase):
	"""
	Test the implementation of the Zhao et al. consumer.
	"""

	def test_create_consumer(self):
		"""
		Test that when creating a consumer, all the parameters are saved correctly.
		"""

		queue = Queue()
		consumer = ZhaoConsumer(queue, 60, timestamp='time')
		self.assertEqual(queue, consumer.queue)
		self.assertEqual(60, consumer.periodicity)
		self.assertEqual('time', consumer.timestamp)

	def test_create_consumer_default_timestamp(self):
		"""
		Test that when creating a consumer, the default timestamp attribute is 'timestamp'.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		self.assertEqual('timestamp', consumer.timestamp)

	def test_create_consumer_store(self):
		"""
		Test that when creating a consumer, an empty nutrition store is created.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		self.assertEqual({ }, consumer.store.all())
