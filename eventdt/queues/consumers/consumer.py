"""
All consumers follow a simple workflow.
After initialization with a queue, the consumer can be run using the :func:`~queues.consumer.`
"""

from ..queue.queue import Queue

from abc import ABC, abstractmethod

import asyncio

class Consumer(ABC):
	"""
	The abstract Consumer class outlines some necessary functions of a consumer.

	:ivar _queue: The queue that is to be consumed.
	:vartype _queue: :class:`~queues.queue.queue.Queue`
	:ivar _stopped: A boolean indicating whether the consumer has been stopped.
	:vartype _stopped: bool
	"""

	def __init__(self, queue):
		"""
		Initialize the Consumer with its queue.

		:param queue: The queue that will be consumed.
		:vartype _queue: :class:`~queues.queue.queue.Queue`
		"""

		self._queue = queue
		self._stopped = False

	async def run(self, initial_wait=0, max_time=3600, max_inactivity=-1):
		"""
		Invokes the consume method.
		Since some listeners have a small delay, the consumer waits a bit before starting to consume input.

		:param initial_wait: The time (in seconds) to wait until starting to understand the event.
			This is used when the file listener spends a lot of time skipping documents.
		:type initial_wait: int
		:param max_time: The maximum time (in seconds) to spend understanding the event.
			It may be interrupted if the queue is inactive for a long time.
		:type max_time: int
		:param max_inactivity: The maximum time (in seconds) to wait idly without input before stopping.
			If it is negative, it is ignored.
		:type max_inactivity: int
		"""

		await asyncio.sleep(initial_wait)
		self._active = True
		self._stopped = False
		await self._consume(max_time=max_time, max_inactivity=max_inactivity)

	async def _wait_for_input(self, max_inactivity=-1):
		"""
		Wait for input from the queue.
		When input is received, the function returns True.
		If no input is found for the given number of seconds, the function returns False.
		If the maximum inactivity is negative or zero, it is disregarded.

		:param max_inactivity: The maximum time (in seconds) to wait idly without input before stopping.
			If it is negative, it is ignored.
		:type max_inactivity: int

		:return: A boolean indicating whether the consumer should continue, or whether it has been idle for far too long.
		:rtype: bool
		"""

		"""
		If the queue is empty, it could be an indication of downtime
		Therefore the consumer should yield for a bit
		However, if it yields for too long, it is assumed that the queue is dead
		"""

		inactive = 0
		sleep = 0.25
		while self._queue.length() == 0 and (max_inactivity < 0 or inactive < max_inactivity):
			await asyncio.sleep(sleep)
			inactive += sleep

		if self._queue.length() > 0:
			return True

		"""
		Stop trying to consume if the consumer has been inactive for far too long
		"""
		if inactive >= max_inactivity and max_inactivity > 0:
			return False

		return True

	def stop(self):
		"""
		Set a flag to stop consuming.
		"""

		self._active = False

	def is_stopped(self):
		"""
		Get a boolean indicating whether the consumer has shut down or not.

		:return: A flag indicating whether the consumer has been stopped.
		:rtype: bool
		"""

		return self._stopped

	@abstractmethod
	async def _consume(self, max_time, max_inactivity):
		"""
		Consume the next element from the queue.

		:param max_time: The maximum time (in seconds) to spend understanding the event.
			It may be interrupted if the queue is inactive for a long time.
		:type max_time: int
		:param max_inactivity: The maximum time (in seconds) to wait idly without input before stopping.
			If it is negative, it is ignored.
		:type max_inactivity: int
		"""

		pass
