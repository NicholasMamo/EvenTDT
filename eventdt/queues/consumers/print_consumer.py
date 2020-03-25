"""
The print consumer outputs the queue's elements as they arrive.
"""

from .consumer import Consumer

import asyncio
import json
import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from logger import logger

class PrintConsumer(Consumer):
	"""
	The print consumer prints queue messages and discards them.
	"""

	async def _consume(self, max_time=3600, max_inactivity=5):
		"""
		Consume the next elements from the queue.

		:param max_time: The maximum time in seconds to spend consuming the queue.
						 It may be interrupted if the queue is inactive for a long time.
		:type max_time: int
		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, the consumer keeps waiting for input until the maximum time expires.
		:type max_inactivity: int
		"""

		"""
		The consumer keeps working until it is forcibly stopped or its time runs out.
		"""
		start = time.time()
		while self.active and (time.time() - start < max_time):
			"""
			If the queue is idle, stop waiting for input
			"""
			active = await self._wait_for_input(max_inactivity=max_inactivity)
			if not active:
				break

			"""
			The print consumer prints the string representation of each object in the queue.
			"""
			while self.queue.length():
				tweet = self.queue.dequeue()
				logger.info(tweet.get('text'))

		"""
		Set a boolean indicating that the consumer has successfully stopped working.
		"""
		self.stopped = True
