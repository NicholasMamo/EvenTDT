"""
The statistic consumer is a simple consumer that reports statistics about tweets periodically.
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
	The statistic consumer is a simple consumer that reports statistics about tweets periodically.
	The reporting is done based on the periodicity.
	"""

	async def _process(self):
		"""
		Count and report the number of tweets received in the last period.
		"""

		"""
		The process repeats until the consumer has been stopped.
		"""
		await self._sleep()
		while not self.stopped:
			logger.info(f"{ self.buffer.length() } tweets in {self.periodicity} seconds")
			self.buffer.empty()
			await self._sleep()

		if self.buffer.length():
			logger.info(self.buffer.length(), "tweets flushed")
			self.buffer.empty()
