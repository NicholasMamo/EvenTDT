"""
The :class:`~queues.consumers.stat_consumer.StatConsumer` is a simple, windowed consumer that reports statistics about tweets periodically.
These statistics are very basic: the number of tweets received every minute.
"""

from .buffered_consumer import BufferedConsumer

import asyncio
import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from logger import logger

class StatConsumer(BufferedConsumer):
    """
    The :class:`~queues.consumers.stat_consumer.StatConsumer` maintains no special state.
    After every time window, it empties the buffer and prints the number of tweets in it.
    """

    async def _process(self):
        """
        Count and report the number of tweets received in the last period.
        """

        """
        The process repeats until the consumer has been stopped.
        """
        await self._sleep()
        while self.active:
            logger.info(f"{ self.buffer.length() } tweets in {self.periodicity} seconds", process=str(self))
            self.buffer.empty()
            await self._sleep()
