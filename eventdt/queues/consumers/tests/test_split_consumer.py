"""
Test the functionality of the split consumer.
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
from queues.consumers.split_consumer import DummySplitConsumer
from summarization.timeline import Timeline

logger.set_logging_level(logger.LogLevel.WARNING)
logging.getLogger('asyncio').setLevel(logging.ERROR) # disable task length outputs

class TestSplitConsumer(unittest.IsolatedAsyncioTestCase):
    """
    Test the implementation of the split consumer.
    """

    def test_init_name(self):
        """
        Test that the split consumer passes on the name to the base class.
        """

        name = 'Test Consumer'
        splits = [ (0, 50), (50, 100) ]
        consumer = DummySplitConsumer(Queue(), splits, PrintConsumer, name=name)
        self.assertEqual(name, str(consumer))

    def test_init_list_splits(self):
        """
        Test that the split consumer accepts a list of splits.
        """

        splits = [ (0, 50), (50, 100) ]
        consumer = DummySplitConsumer(Queue(), splits, PrintConsumer)
        self.assertEqual(2, len(consumer.consumers))

    def test_init_tuple_splits(self):
        """
        Test that the split consumer accepts a tuple of splits but converts them to lists.
        """

        splits = ( (0, 50), (50, 100) )
        consumer = DummySplitConsumer(Queue(), splits, PrintConsumer)
        self.assertEqual(2, len(consumer.consumers))
        self.assertEqual(list, type(consumer.splits))

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

    def test_init_no_has_default(self):
        """
        Test that by default, only the given streams are created.
        """

        splits = [ (0, 50), (50, 100) ]
        consumer = DummySplitConsumer(Queue(), splits, PrintConsumer, has_default=False)
        self.assertEqual(splits, consumer.splits)
        self.assertEqual(len(splits), len(consumer.consumers))

    def test_init_has_default(self):
        """
        Test that if the consumer has a default stream, an extra split is created.
        """

        splits = [ (0, 50), (50, 100) ]
        consumer = DummySplitConsumer(Queue(), splits, PrintConsumer, has_default=True)
        self.assertEqual(splits + [ '*' ], consumer.splits)
        self.assertEqual(len(splits) + 1, len(consumer.consumers))

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

    async def test_run_stops_consumers(self):
        """
        Test that it is only after the split consumer finishes that running stops the consumers.
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
        running = asyncio.ensure_future(consumer.run(max_inactivity=5))
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

    async def test_run_returns_timelines(self):
        """
        Test that when running the split consumer, it returns the timelines and other data from its consumers.
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
        results = (await asyncio.gather(running))[0]
        self.assertEqual({ 'split.consumed', 'consumed', 'filtered', 'skipped', 'timeline' }, set(results.keys()))
        self.assertTrue(all( type(timeline) is Timeline for timeline in results['timeline'] ))

    async def test_run_consumed_(self):
        """
        Test that when running the split consumer, the returned document includes a ``consume`` key with one value for each split.
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
        results = (await asyncio.gather(running))[0]
        self.assertEqual({ 'split.consumed', 'consumed', 'filtered', 'skipped', 'timeline' }, set(results.keys()))
        self.assertTrue(all( len(splits) == len(results[key]) for key in results ))
        self.assertEqual(len(splits), len(results['consumed']))

    async def test_stop_stops_consumers(self):
        """
        Test that when stopping the split consumer, it also stops its child consumers.
        """

        splits = [ (0, 50), (50, 100) ]
        consumer = DummySplitConsumer(Queue(), splits, ZhaoConsumer, periodicity=10)
        self.assertFalse(consumer.active)
        self.assertTrue(consumer.stopped)
        self.assertTrue(all( not _consumer.active for _consumer in consumer.consumers ))
        self.assertTrue(all( _consumer.stopped for _consumer in consumer.consumers ))

        """
        Run the consumer.
        """
        running = asyncio.ensure_future(consumer.run(max_inactivity=60)) # set a high maximum inactivity so the consumer doesn't end on its own
        await asyncio.sleep(1)
        self.assertTrue(consumer.active)
        self.assertFalse(consumer.stopped)
        self.assertTrue(all( _consumer.active for _consumer in consumer.consumers ))
        self.assertTrue(all( not _consumer.stopped for _consumer in consumer.consumers ))

        """
        Stop the consumer
        """
        consumer.stop()
        await asyncio.sleep(0.5)
        self.assertTrue(all( not _consumer.active for _consumer in consumer.consumers ))
        self.assertTrue(all( _consumer.stopped for _consumer in consumer.consumers ))
        result = await asyncio.gather(running)

    def test_preprocess_identical(self):
        """
        Test that the default pre-processing step does not change the tweet at all.
        """

        splits = [ (0, 50), (50, 100) ]
        consumer = DummySplitConsumer(Queue(), splits, ELDConsumer)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(tweet, consumer._preprocess(tweet))
