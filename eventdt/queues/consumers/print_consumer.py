"""
The :class:`~queues.consumers.print_consumer.PrintConsumer` is a real-time consumer that performs no processing, expect to print the tweets as they arrive in the :class:`~queues.Queue`.
"""

import asyncio
import json
import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from logger import logger
from queues.consumers import Consumer

class PrintConsumer(Consumer):
	"""
	The :class:`~queues.consumers.print_consumer.PrintConsumer` maintains no special state.
	It works in real-time, reading and printing tweets from the :class:`~queues.Queue`, and discarding them immediately.
	"""

	async def _consume(self, max_inactivity=5):
		"""
		Consume the next elements from the queue.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, the consumer keeps waiting for input until the maximum time expires.
		:type max_inactivity: int
		"""

		"""
		The consumer keeps working until it is stopped.
		"""
		while self.active:
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
