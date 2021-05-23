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

    def test_preprocess_identical(self):
        """
        Test that the default pre-processing step does not change the tweet at all.
        """

        splits = [ (0, 50), (50, 100) ]
        consumer = DummyFilterConsumer(Queue(), splits, ELDConsumer)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(tweet, consumer._preprocess(tweet))
