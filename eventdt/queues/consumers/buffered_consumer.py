"""
A buffered consumer processes content in batches.
"""

from abc import ABC, abstractmethod

import asyncio
import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from queues import Queue
from .consumer import Consumer

import twitter

class BufferedConsumer(Consumer):
	"""
	The buffered consumer adds the processing stage apart from the consumption.
	The :func:`~queues.consumers.buffered_consumer.BufferedConsumer._consume` function function waits until objects become available in the queue.
	The :func:`~queues.consumers.buffered_consumer.BufferedConsumer._process` function empties this buffer and processes it.
	The two functions communicate with each other using a common queue, called a buffer.

	:ivar periodicity: The time window in seconds of the buffered consumer, or how often it is invoked.
	:vartype periodicity: int
	:ivar buffer: The buffer of objects that have to be processed.
	:vartype buffer: :class:`~queues.queue.Queue`
	"""

	def __init__(self, queue, periodicity=60):
		"""
		Initialize the buffered consumer with its queue and periodicity.

		:param queue: The queue that is consumed.
		:type queue: :class:`~queues.queue.Queue`
		:param periodicity: The time window in seconds of the buffered consumer, or how often it is invoked.
		:type periodicity: int
		"""

		super(BufferedConsumer, self).__init__(queue)
		self.periodicity = periodicity
		self.buffer = Queue()

	async def run(self, wait=0, max_time=3600, max_inactivity=-1):
		"""
		Invokes the consume and process method.

		Any additional arguments and keyword arguments are passed on to the :class:`~queues.consumers.consumer.Consumer._consume` function.

		:param wait: The time in seconds to wait until starting to understand the event.
					 This is used when the file listener spends a lot of time skipping documents.
		:type wait: int
		:param max_time: The maximum time in seconds to spend consuming the queue.
						 It may be interrupted if the queue is inactive for a long time.
		:type max_time: int
		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, the consumer keeps waiting for input until the maximum time expires.
		:type max_inactivity: int

		:return: The output of the consume method.
		:rtype: any
		"""

		await asyncio.sleep(wait)
		self._started()
		results = await asyncio.gather(
			self._consume(*args, **kwargs, max_time=max_time, max_inactivity=max_inactivity),
			self._process(),
		)
		self._stopped()
		return results

	async def _consume(self, max_time, max_inactivity):
		"""
		Consume the queue.
		This function calls for processing in turn.

		:param max_time: The maximum time in seconds to spend consuming the queue.
						 It may be interrupted if the queue is inactive for a long time.
		:type max_time: int
		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, the consumer keeps waiting for input until the maximum time expires.
		:type max_inactivity: int
		"""

		"""
		The consumer should keep working until it is forcibly stopped or its time runs out.
		"""
		start = time.time()
		while self.active and (time.time() - start < max_time):
			"""
			If the queue is idle, stop waiting for input.
			"""
			inactive = await self._wait_for_input(max_inactivity=max_inactivity)
			if not inactive:
				break

			"""
			The consuming phase empties the queue and stores the elements in the buffer.
			The buffer is processed separately in the :func:`~queues.consumers.buffered_consumer.BufferedConsumer.process` function.
			"""
			elements = self.queue.dequeue_all()
			self.buffer.enqueue(*elements)

		"""
		Set the consumer to indicate that the buffered consumer has stopped working.
		"""
		self.stopped = True

	@abstractmethod
	async def _process():
		"""
		Process the buffered items.
		"""

		pass

	async def _sleep(self):
		"""
		Sleep until the window is over.
		At this point, the queue is emptied into a buffer for processing.
		The function periodically checks if the consumer has been asked to stop.
		"""

		for i in range(self.periodicity):
			await asyncio.sleep(1)
			if self.stopped:
				break

		"""
		If the periodicity is a float, sleep for the remaining milli-seconds.
		"""
		if not self.stopped:
			await asyncio.sleep(self.periodicity % 1)

class SimulatedBufferedConsumer(BufferedConsumer):
	"""
	The simulated buffered consumer is exactly like the buffered consumer, but its periodicity is not real-time.
	Instead, it gets the time from the incoming message.
	This class can be used in a simulated environment, such as when data has been collected.
	In this case, it allows the data to be consumed at the rate that it is read.
	"""

	def __init__(self, queue, periodicity):
		"""
		Initialize the simulated buffered consumer with its queue, periodicity and buffer.
		The timestamp parameter is the field that the sleep function checks to know when it should awake.

		:param queue: The queue that is consumed.
		:type queue: :class:`~queues.queue.Queue`
		:param periodicity: The time window in seconds of the buffered consumer, or how often it is invoked.
		:type periodicity: int
		"""

		super(SimulatedBufferedConsumer, self).__init__(queue, periodicity)

	async def _sleep(self):
		"""
		Sleep until the window is over.
		At this point, the queue is emptied into a buffer for processing.
		The function periodically checks if the consumer has been asked to stop.
		"""

		"""
		Wait until there's something in the queue, to get a reference point for when the sleep should end.
		"""
		while self.buffer.head() is None and not self.stopped:
			await asyncio.sleep(0.1)

		if not self.stopped:
			start = twitter.extract_timestamp(self.buffer.head())

		"""
		Check if the consumer should stop.
		The consumer should stop if:

			#. It has been shut down; or

			#. The buffer's periodicity has been reached.
		"""
		while True:
			if self.stopped or twitter.extract_timestamp(self.buffer.tail()) - start >= self.periodicity:
				break

			await asyncio.sleep(0.1)
