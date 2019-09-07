"""
A simple consumer that observes the stream and outputs statistics about it
"""

from .consumer import Consumer

from datetime import datetime

import asyncio

class StatConsumer(Consumer):
	"""
	The StatConsumer class' only job is to observe the stream and output the number of tweets per minute every minute
	"""

	async def _consume(self, max_time, max_inactivity=5):
		"""
		Consume the next elements from the queue
		"""

		start = datetime.now().timestamp() # start timing the procedure

		"""
		The consumer should keep working until it is forcibly stopped or its time runs out
		"""
		while True and self._active and (datetime.now().timestamp() - start < max_time):
			"""
			The StatConsumer's main job is to print statistics about the collected data
			"""
			if self._queue.length() > 0:
				print(datetime.now().strftime("%H:%M:%S"), self._queue.length(), "tweets/minute")
				self._queue.empty() # empty the queue to start counting again

			"""
			Sleep for one minute
			"""
			await asyncio.sleep(5)

		if self._queue.length() > 0:
			print(datetime.now().strftime("%H:%M:%S"), self._queue.length(), "tweets/minute")
			self._queue.empty() # empty the queue to start counting again

		self._stopped = True # set a boolean indicating that the consumer has successfully stopped working
