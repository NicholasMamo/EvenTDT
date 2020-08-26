"""
Test the functionality of the FUEGO consumer.
"""

import asyncio
import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
	sys.path.append(path)

from queues import Queue
from queues.consumers.algorithms import FUEGOConsumer
from nlp.document import Document
from nlp.weighting import TF
from vsm import vector_math
from vsm.clustering import Cluster
import twitter

class TestFUEGOConsumer(unittest.TestCase):
	"""
	Test the implementation of the FUEGO consumer.
	"""

	def async_test(f):
		def wrapper(*args, **kwargs):
			coro = asyncio.coroutine(f)
			future = coro(*args, **kwargs)
			loop = asyncio.get_event_loop()
			loop.run_until_complete(future)
		return wrapper

	def test_init_name(self):
		"""
		Test that the ELD consumer passes on the name to the base class.
		"""

		name = 'Test Consumer'
		consumer = FUEGOConsumer(Queue(), name=name)
		self.assertEqual(name, str(consumer))

	def test_init_queue(self):
		"""
		Test that when creating a consumer, the class saves the queue.
		"""

		queue = Queue()
		consumer = FUEGOConsumer(queue)
		self.assertEqual(queue, consumer.queue)
		self.assertEqual(0, consumer.queue.length())

	def test_init_with_tokenizer(self):
		"""
		Test that when creating a consumer, the class creates a tokenizer.
		"""

		consumer = FUEGOConsumer(Queue())
		self.assertTrue(consumer.tokenizer)
		self.assertTrue(consumer.tokenizer.stopwords)
		self.assertTrue(consumer.tokenizer.stem)

