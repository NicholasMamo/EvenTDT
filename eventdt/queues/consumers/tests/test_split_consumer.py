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

from logger import logger
from queues import Queue
from queues.consumers import PrintConsumer
from queues.consumers.algorithms import ELDConsumer, ZhaoConsumer
from queues.consumers.split_consumer import DummySplitConsumer
from summarization.timeline import Timeline

logger.set_logging_level(logger.LogLevel.WARNING)

class TestSplitConsumer(unittest.TestCase):
	"""
	Test the implementation of the split consumer.
	"""

	def async_test(f):
		def wrapper(*args, **kwargs):
			coro = asyncio.coroutine(f)
			future = coro(*args, **kwargs)
			loop = asyncio.get_event_loop()
			loop.run_until_complete(future)
		return wrapper

	def test_init_list_splits(self):
		"""
		Test that the split consumer accepts a list of splits.
		"""

		splits = [ (0, 50), (50, 100) ]
		consumer = DummySplitConsumer(Queue(), splits, PrintConsumer)
		self.assertEqual(2, len(consumer.consumers))

	def test_init_tuple_splits(self):
		"""
		Test that the split consumer accepts a tuple of splits.
		"""

		splits = ( (0, 50), (50, 100) )
		consumer = DummySplitConsumer(Queue(), splits, PrintConsumer)
		self.assertEqual(2, len(consumer.consumers))

	def test_init_primitive_splits_raises_ValueError(self):
		"""
		Test that the split consumer raises a ValueError when it receives a primitive as a split.
		"""

		splits = 50
		self.assertRaises(ValueError, DummySplitConsumer, Queue(), splits, PrintConsumer)

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

	def test_init_consumers_arguments(self):
		"""
		Test that when passing on extra arguments to the split consumer, they are passed on to the consumer.
		"""

		splits = [ (0, 50), (50, 100) ]
		consumer = DummySplitConsumer(Queue(), splits, ZhaoConsumer)
		self.assertTrue(all( 5 == _consumer.periodicity for _consumer in consumer.consumers ))

		consumer = DummySplitConsumer(Queue(), splits, ZhaoConsumer, periodicity=10)
		self.assertTrue(all( 10 == _consumer.periodicity for _consumer in consumer.consumers ))

	@async_test
	async def test_run_starts_consumers(self):
		"""
		Test that when running the split consumer, it also runs its child consumers.
		"""

		splits = [ (0, 50), (50, 100) ]
		consumer = DummySplitConsumer(Queue(), splits, PrintConsumer)
		self.assertFalse(consumer.active)
		self.assertTrue(consumer.stopped)
		self.assertTrue(all( not _consumer.active for _consumer in consumer.consumers ))
		self.assertTrue(all( _consumer.stopped for _consumer in consumer.consumers ))

		"""
		Run the consumer.
		"""
		running = asyncio.ensure_future(consumer.run(max_inactivity=1))
		await asyncio.sleep(1)
		self.assertTrue(consumer.active)
		self.assertFalse(consumer.stopped)
		self.assertTrue(all( _consumer.active for _consumer in consumer.consumers ))
		self.assertTrue(all( not _consumer.stopped for _consumer in consumer.consumers ))

		"""
		Wait for the consumer to finish.
		"""
		result = await asyncio.gather(running)
		self.assertTrue(all( not _consumer.active for _consumer in consumer.consumers ))
		self.assertTrue(all( _consumer.stopped for _consumer in consumer.consumers ))

	@async_test
	async def test_run_returns_timelines(self):
		"""
		Test that when running the split consumer, it returns the timelines from its consumers.
		"""

		splits = [ (0, 50), (50, 100) ]
		consumer = DummySplitConsumer(Queue(), splits, ELDConsumer)
		self.assertFalse(consumer.active)
		self.assertTrue(consumer.stopped)
		self.assertTrue(all( not _consumer.active for _consumer in consumer.consumers ))
		self.assertTrue(all( _consumer.stopped for _consumer in consumer.consumers ))

		"""
		Run the consumer.
		"""
		running = asyncio.ensure_future(consumer.run(max_inactivity=1))
		await asyncio.sleep(1)
		self.assertTrue(consumer.active)
		self.assertFalse(consumer.stopped)
		self.assertTrue(all( _consumer.active for _consumer in consumer.consumers ))
		self.assertTrue(all( not _consumer.stopped for _consumer in consumer.consumers ))

		"""
		Wait for the consumer to finish.
		"""
		results = await asyncio.gather(running)
		self.assertTrue(all( type(result[0]) is Timeline for result in results[0][1:] ))
