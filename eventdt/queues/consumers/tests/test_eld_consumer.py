"""
Test the functionality of the ELD consumer.
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
from queues.consumers import ELDConsumer
from nlp.document import Document
from nlp.term_weighting import TF
from vsm import vector_math
from vsm.clustering import Cluster
import twitter

class TestELDConsumer(unittest.TestCase):
	"""
	Test the implementation of the ELD consumer.
	"""

	def test_create_consumer(self):
		"""
		Test that when creating a consumer, all the parameters are saved correctly.
		"""

		queue = Queue()
		consumer = ELDConsumer(queue, 60, scheme=TF())
		self.assertEqual(queue, consumer.queue)
		self.assertEqual(0, consumer.queue.length())
		self.assertEqual(60, consumer.time_window)
		self.assertEqual(TF, type(consumer.scheme))

	def test_create_consumer_buffer_empty(self):
		"""
		Test that when creating a consumer, an empty buffer is created.
		"""

		queue = Queue()
		consumer = ELDConsumer(queue, 60, scheme=TF())
		self.assertEqual(Queue, type(consumer.buffer))
		self.assertEqual(0, consumer.buffer.length())
