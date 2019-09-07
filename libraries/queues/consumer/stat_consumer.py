"""
A simple consumer that observes the stream and outputs statistics about it.
"""

from .buffered_consumer import BufferedConsumer

from datetime import datetime

import asyncio

class StatConsumer(BufferedConsumer):
	"""
	The StatConsumer class' only job is to observe the stream and output the number of tweets per minute every minute.
	"""

	async def _process(self):
		"""
		Count the elements in the queue.
		"""

		while not self._stopped:
			if self._buffer.length() > 0:
				print(datetime.now().strftime("%H:%M:%S"), self._buffer.length(), "tweets every", self._periodicity, "seconds")
				self._buffer.empty() # empty the queue to start counting again

			await self._sleep()

		if self._buffer.length() > 0:
			print(datetime.now().strftime("%H:%M:%S"), self._buffer.length(), "tweets flushed")
			self._buffer.empty() # empty the queue to start counting again
