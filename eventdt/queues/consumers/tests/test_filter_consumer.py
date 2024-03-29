"""
Test the functionality of the filter consumer.
"""

import asyncio
import json
import logging
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
logging.getLogger('asyncio').setLevel(logging.ERROR) # disable task length outputs

class TestFilterConsumer(unittest.IsolatedAsyncioTestCase):
    """
    Test the implementation of the filter consumer.
    """

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

    async def test_run_returns_consumed(self):
        """
        Test that at the end, the filter consumer returns the number of consumed tweets.
        """

        """
        Create an empty queue.
        Use it to create a consumer and set it running.
        """
        queue = Queue()
        filters = [ (0, 50), (50, 100) ]
        consumer = DummyFilterConsumer(Queue(), filters, ELDConsumer)
        running = asyncio.ensure_future(consumer.run(max_inactivity=3))
        await asyncio.sleep(0.5)

        """
        Load all tweets into the queue.
        """
        with open(os.path.join(os.path.dirname(__file__), '../../../tests/corpora/CRYCHE-500.json')) as f:
            tweets = [ json.loads(line) for line in f ]
            queue.enqueue(*tweets)

        output = await running
        self.assertEqual(dict, type(output))
        self.assertTrue('consumed' in output)

    async def test_run_returns_consumed_after_filter(self):
        """
        Test that at the end, when the filter consumer returns the number of consumed tweets, the count includes only filtered tweets.
        """

        """
        Create an empty queue.
        Use it to create a consumer and set it running.
        """
        queue = Queue()
        filters = [ (0, 50), (50, 100) ]
        consumer = DummyFilterConsumer(queue, filters, ELDConsumer)
        running = asyncio.ensure_future(consumer.run(max_inactivity=3))
        await asyncio.sleep(0.5)

        """
        Load all tweets into the queue.
        """
        with open(os.path.join(os.path.dirname(__file__), '../../../tests/corpora/CRYCHE-500.json')) as f:
            tweets = [ json.loads(line) for line in f ]
            queue.enqueue(*tweets)

        output = await running
        self.assertEqual(dict, type(output))
        self.assertTrue('consumed' in output)
        self.assertEqual(500, output['consumed'])

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
        output = (await asyncio.gather(running))[0]
        self.assertEqual(dict, type(output))
        self.assertTrue('timeline' in output)
        self.assertEqual(Timeline, type(output['timeline']))

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
        self.assertFalse(consumer.consumer.active)
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
