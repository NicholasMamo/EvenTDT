"""
Test the functionality of the print consumer.
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

logger.set_logging_level(logger.LogLevel.WARNING)
logging.getLogger('asyncio').setLevel(logging.ERROR) # disable task length outputs

class TestPrintConsumer(unittest.IsolatedAsyncioTestCase):
    """
    Test the implementation of the print consumer.
    """

    async def test_run_returns_consumed_tweets(self):
        """
        Test that at the end, the print consumer returns the number of consumed tweets.
        """

        """
        Create an empty queue.
        Use it to create a buffered consumer and set it running.
        """
        queue = Queue()
        consumer = PrintConsumer(queue)
        running = asyncio.ensure_future(consumer.run(max_inactivity=3))
        await asyncio.sleep(0.5)

        """
        Load all tweets into the queue.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            tweets = [ json.loads(line) for line in f ]
            queue.enqueue(*tweets)

        consumed = await running
        self.assertEqual(dict, type(consumed))
        self.assertEqual(1, len(consumed))
        self.assertEqual(500, consumed['consumed'])
