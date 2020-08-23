"""
Test the functionality of the split consumer.
"""

import asyncio
import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
	sys.path.append(path)

from queues import Queue
from queues.consumers import PrintConsumer
from queues.consumers.split_consumer import DummySplitConsumer

class TestSplitConsumer(unittest.TestCase):
	"""
	Test the implementation of the split consumer.
	"""

	def test_init_consumers_for_splits(self):
		"""
		Test that when creating the split consumer, it creates as many consumers as splits.
		"""

		splits = [ (0, 50), (50, 100) ]
		consumer = DummySplitConsumer(Queue(), splits, PrintConsumer)
		self.assertEqual(2, len(consumer.consumers))

	def test_init_consumers_separate_queues(self):
		"""
		Test that when creating the split consumer, its children consumers have separate queues.
		"""

		splits = [ (0, 50), (50, 100) ]
		consumer = DummySplitConsumer(Queue(), splits, PrintConsumer)
		queues = [ _consumer.queue for _consumer in consumer.consumers ]
		self.assertEqual(2, len(set(queues)))
