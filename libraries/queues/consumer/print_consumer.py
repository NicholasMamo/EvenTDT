"""
A simple consumer that simply outputs the queue's elements when they arrive.
"""

from .consumer import Consumer

from datetime import datetime

import asyncio

class PrintConsumer(Consumer):
	"""
	The PrintConsumer class' only job is to print queue messages and discard them.
	"""

	async def _consume(self, max_time=3600, max_inactivity=5):
		"""
		Consume the next elements from the queue.

		:param max_time: The maximum time (in seconds) to spend understanding the event.
			It may be interrupted if the queue is inactive for a long time.
		:type max_time: int
		:param max_inactivity: The maximum time (in seconds) to wait idly without input before stopping.
			If it is negative, it is ignored.
		:type max_inactivity: int
		"""

		"""
		The consumer should keep working until it is forcibly stopped or its time runs out.
		"""
		start = datetime.now().timestamp() # start timing the procedure
		while True and self._active and (datetime.now().timestamp() - start < max_time):
			"""
			If the queue is idle, stop waiting for input
			"""
			active = await self._wait_for_input(max_inactivity=max_inactivity)
			if not active:
				break

			"""
			The PrintConsumer's main job is to print the collected data.
			If there is a text field, it is printed.
			Otherwise, the object is printed.
			"""
			while self._queue.length() > 0:
				element = self._queue.dequeue()
				print(element.get("text", element)[:35], "...")

		self._stopped = True # set a boolean indicating that the consumer has successfully stopped working
