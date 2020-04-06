"""
All consumers follow a simple workflow.
After initialization with a queue, the consumer can be run using the :func:`~queues.consumers.consumer.Consumer.run` function.
That function prepares to start consuming the queue and calls the :func:`~queues.consumers.consumer.Consumer._consume` function.

Consumers have two other state variables apart from the queue: the `active` and `stopped` variables.
The `active` variable indicates whether the consumer is still accepting objects.
The `stopped` variable indicates whether the consumer has finished consuming all objects.
Generally, consumers keep accepting objects until the `active` variable is disabled.
At that point, they process the last objects and set the `stopped` flag to `True`.
"""

from abc import ABC, abstractmethod

import asyncio
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from queue import Queue

class Consumer(ABC):
	"""
	The abstract Consumer class outlines the necessary functions of a consumer.
	It also defines the state of the consumer.

	:ivar queue: The queue that is to be consumed.
	:vartype queue: :class:`~queues.queue.Queue`
	:ivar active: A boolean indicating whether the consumer is still accepting data.
	:vartype active: bool
	:ivar stopped: A boolean indicating whether the consumer has finished processing.
	:vartype stopped: bool
	"""

	def __init__(self, queue):
		"""
		Initialize the Consumer with its queue.

		:param queue: The queue that will be consumed.
		:vartype queue: :class:`~queues.queue.Queue`
		"""

		self.queue = queue
		self.active = False
		self.stopped = True

	async def run(self, wait=0, max_inactivity=-1, *args, **kwargs):
		"""
		Invoke the consume method.
		Since some listeners have a small delay, the consumer may wait a bit before starting to consume input.

		Any additional arguments and keyword arguments are passed on to the :func:`~queues.consumers.consumer.Consumer._consume` function.

		:param wait: The time in seconds to wait until starting to consume the event.
					 This is used when the file listener spends a lot of time skipping tweets.
		:type wait: int
		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, the consumer keeps waiting for input until the maximum time expires.
		:type max_inactivity: int

		:return: The output of the consume method.
		:rtype: any
		"""

		await asyncio.sleep(wait)
		self._started()
		results = await asyncio.gather(
			self._consume(*args, max_inactivity=max_inactivity, **kwargs),
		)
		self._stopped()
		return results

	def stop(self):
		"""
		Set a flag to stop accepting new objects.

		.. note::
			Contrary to the name of the function, the function sets the `active` flag, not the `stopped` flag.
			This function merely asks that the consumer stops accepting new objects for processing.
		"""

		self.active = False

	@abstractmethod
	async def _consume(self, max_inactivity, *args, **kwargs):
		"""
		Consume the queue.
		This is the function where most processing occurs.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, the consumer keeps waiting for input until the maximum time expires.
		:type max_inactivity: int
		"""

		pass

	async def _wait_for_input(self, max_inactivity, sleep=0.25):
		"""
		Wait for input from the queue.
		When input is received, the function returns True.
		If no input is found for the given number of seconds, the function returns False.
		If the maximum inactivity is negative, it is disregarded.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, it is ignored.
		:type max_inactivity: int
		:param sleep: The number of seconds to sleep while waiting for input.
		:type sleep: float

		:return: A boolean indicating whether the consumer should continue, or whether it has been idle for far too long.
		:rtype: bool
		"""

		"""
		If the queue is empty, it could be an indication of downtime.
		Therefore the consumer should yield for a bit.
		"""
		inactive = 0
		while (self.active and not self.queue.length() and
			  (max_inactivity < 0 or inactive < max_inactivity)):
			await asyncio.sleep(sleep)
			inactive += sleep

		if not self.active:
			return False

		"""
		If there are objects in the queue after waiting, return `True`.
		"""
		if self.queue.length():
			return True

		"""
		If the queue is still empty, return `False` because the queue is idle.
		"""
		if inactive >= max_inactivity and max_inactivity >= 0:
			return False

		return True

	def _started(self):
		"""
		A function that sets the active and stopped flags to indicate that the consumer has started operating.
		"""

		self.active = True
		self.stopped = False

	def _stopped(self):
		"""
		A function that sets the active and stopped flags to indicate that the consumer has stopped operating.
		"""

		self.active = False
		self.stopped = True
