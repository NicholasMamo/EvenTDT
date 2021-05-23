"""
Test the functionality of the filter consumer.
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
from queues.consumers.filter_consumer import DummyFilterConsumer
from summarization.timeline import Timeline

logger.set_logging_level(logger.LogLevel.WARNING)

class TestFilterConsumer(unittest.TestCase):
    """
    Test the implementation of the filter consumer.
    """

    def async_test(f):
        def wrapper(*args, **kwargs):
            coro = asyncio.coroutine(f)
            future = coro(*args, **kwargs)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(future)
        return wrapper

    def test_init_list_filters(self):
        """
        Test that the filter consumer accepts a list of filters.
        """

        filters = [ (0, 50), (50, 100) ]
        consumer = DummyFilterConsumer(Queue(), filters, PrintConsumer)
        self.assertTrue(consumer)

    def test_init_tuple_filters(self):
        """
        Test that the filter consumer accepts a tuple of filters.
        """

        filters = ( (0, 50), (50, 100) )
        consumer = DummyFilterConsumer(Queue(), filters, PrintConsumer)
        self.assertTrue(consumer)

    def test_init_primitive_filters_raises_ValueError(self):
        """
        Test that the filter consumer raises a ValueError when it receives a primitive as a filter.
        """

        filters = 50
        self.assertRaises(ValueError, DummyFilterConsumer, Queue(), filters, PrintConsumer)

    def test_init_consumer(self):
        """
        Test that when creating the filter consumer, it also creates its own consumer.
        """

        filters = [ (0, 50), (50, 100) ]
        consumer = DummyFilterConsumer(Queue(), filters, PrintConsumer)
        self.assertEqual(PrintConsumer, type(consumer.consumer))

    def test_init_consumer_arguments(self):
        """
        Test that when passing on extra arguments to the filter consumer, they are passed on to the consumer.
        """

        filters = [ (0, 50), (50, 100) ]
        consumer = DummyFilterConsumer(Queue(), filters, ZhaoConsumer)
        self.assertEqual(5, consumer.consumer.periodicity)

        consumer = DummyFilterConsumer(Queue(), filters, ZhaoConsumer, periodicity=10)
        self.assertEqual(10, consumer.consumer.periodicity)

    @async_test
    async def test_run_starts_consumers(self):
        """
        Test that when running the filter consumer, it also runs its own consumer.
        """

        filters = [ (0, 50), (50, 100) ]
        consumer = DummyFilterConsumer(Queue(), filters, PrintConsumer)
        self.assertFalse(consumer.active)
        self.assertTrue(consumer.stopped)
        self.assertFalse(consumer.consumer.active)
        self.assertTrue(consumer.consumer.stopped)

        """
        Run the consumer.
        """
        running = asyncio.ensure_future(consumer.run(max_inactivity=1))
        await asyncio.sleep(1)
        self.assertTrue(consumer.active)
        self.assertFalse(consumer.stopped)
        self.assertTrue(consumer.consumer.active)
        self.assertFalse(consumer.consumer.stopped)

        """
        Wait for the consumer to finish.
        """
        result = await asyncio.gather(running)
        self.assertFalse(consumer.consumer.active)
        self.assertTrue(consumer.consumer.stopped)

    @async_test
    async def test_run_stops_consumers(self):
        """
        Test that it is only after the filter consumer finishes that running stops its consumer.
        """

        filters = [ (0, 50), (50, 100) ]
        consumer = DummyFilterConsumer(Queue(), filters, PrintConsumer)
        self.assertFalse(consumer.active)
        self.assertTrue(consumer.stopped)
        self.assertFalse(consumer.consumer.active)
        self.assertTrue(consumer.consumer.stopped)

        """
        Run the consumer.
        """
        running = asyncio.ensure_future(consumer.run(max_inactivity=5))
        await asyncio.sleep(1)
        self.assertTrue(consumer.active)
        self.assertFalse(consumer.stopped)
        self.assertTrue(consumer.consumer.active)
        self.assertFalse(consumer.consumer.stopped)

        """
        Wait for the consumer to finish.
        """
        result = await asyncio.gather(running)
        self.assertFalse(consumer.consumer.active)
        self.assertTrue(consumer.consumer.stopped)

    @async_test
    async def test_run_returns_timeline(self):
        """
        Test that when running the filter consumer, it returns the timeline from its own consumers.
        """

        filters = [ (0, 50), (50, 100) ]
        consumer = DummyFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertFalse(consumer.active)
        self.assertTrue(consumer.stopped)
        self.assertFalse(consumer.consumer.active)
        self.assertTrue(consumer.consumer.stopped)

        """
        Run the consumer.
        """
        running = asyncio.ensure_future(consumer.run(max_inactivity=1))
        await asyncio.sleep(1)
        self.assertTrue(consumer.active)
        self.assertFalse(consumer.stopped)
        self.assertTrue(consumer.consumer.active)
        self.assertFalse(consumer.consumer.stopped)

        """
        Wait for the consumer to finish.
        """
        timeline = (await asyncio.gather(running))[0]
        self.assertEqual(Timeline, type(timeline))

    @async_test
    async def test_stop_stops_consumers(self):
        """
        Test that when stopping the filter consumer, it also stops its child consumer.
        """

        filters = [ (0, 50), (50, 100) ]
        consumer = DummyFilterConsumer(Queue(), filters, ZhaoConsumer, periodicity=10)
        self.assertFalse(consumer.active)
        self.assertTrue(consumer.stopped)
        self.assertFalse(consumer.consumer.active)
        self.assertTrue(consumer.consumer.stopped)

        """
        Run the consumer.
        """
        running = asyncio.ensure_future(consumer.run(max_inactivity=60)) # set a high maximum inactivity so the consumer doesn't end on its own
        await asyncio.sleep(1)
        self.assertTrue(consumer.active)
        self.assertFalse(consumer.stopped)
        self.assertTrue(consumer.consumer.active)
        self.assertFalse(consumer.consumer.stopped)

        """
        Stop the consumer
        """
        consumer.stop()
        await asyncio.sleep(0.5)
        self.assertTrue(consumer.consumer.active)
        self.assertTrue(consumer.consumer.stopped)
        result = await asyncio.gather(running)

    def test_preprocess_identical(self):
        """
        Test that the default pre-processing step does not change the tweet at all.
        """

        filters = [ (0, 50), (50, 100) ]
        consumer = DummyFilterConsumer(Queue(), filters, ELDConsumer)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(tweet, consumer._preprocess(tweet))
