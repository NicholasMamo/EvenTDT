"""
Test the functionality of the stat consumer.
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
from queues.consumers import StatConsumer
logger.set_logging_level(logger.LogLevel.WARNING)

class TestStatConsumer(unittest.TestCase):
    """
    Test the implementation of the stat consumer.
    """

    def async_test(f):
        def wrapper(*args, **kwargs):
            coro = asyncio.coroutine(f)
            future = coro(*args, **kwargs)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(future)
        return wrapper

    @async_test
    async def test_run_returns_consumed_tweets(self):
        """
        Test that at the end, the stat consumer returns the number of consumed tweets.
        """

        """
        Create an empty queue.
        Use it to create a buffered consumer and set it running.
        """
        queue = Queue()
        consumer = StatConsumer(queue, periodicity=1)
        running = asyncio.ensure_future(consumer.run(max_inactivity=3))
        await asyncio.sleep(0.5)

        """
        Load all tweets into the queue.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            tweets = [ json.loads(line) for line in f ]
            queue.enqueue(*tweets)

        consumed = await running
        self.assertEqual(tuple, type(consumed))
        self.assertEqual(1, len(consumed)) # the second element is the processing's return value
        self.assertEqual(500, consumed[0])
