"""
The :class:`~queues.consumers.Consumer` is designed to operate in real-time.
The :class:`~queues.consumers.buffered_consumer.BufferedConsumer` builds on it, but it buffers input before processing.
Essentially, this buffering step transforms the :class:`~queues.consumers.Consumer` into a windowed approach.

The two :class:`~queues.Queue` instances in the :class:`~queues.consumers.buffered_consumer.BufferedConsumer` have these roles:

- Queue: The normal queue receives input from the :class:`~twitter.file.FileReader` or :class:`~twitter.listener.TweetListener`.

- Buffer: The :class:`~queues.consumers.buffered_consumer.BufferedConsumer` constantly empties the normal queue into the buffer.
  After every window, the algorithm processes the tweets collected so far in it.
  While processing, the buffer continuesreceiving new tweets, which will be processed in the next time window.

This package provides two types of buffered consumers:

- The :class:`~queues.consumers.buffered_consumer.BufferedConsumer` bases its periodicity on the machine's time.
  Therefore it is opportune when running in a live environment.

- The :class:`~queues.consumers.buffered_consumer.SimulatedBufferedConsumer` bases its periodicity on the tweets it is receiving.
  It can be used both in a live environment, but especially when loading tweets from the :class:`~twitter.file.FileReader`.
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
from queues.consumers import Consumer

import twitter

class BufferedConsumer(Consumer):
	"""
	When calling the :func:`~queues.consumers.buffered_consumer.BufferedConsumer.run` function, the :class:`~queues.consumers.buffered_consumer.BufferedConsumer` splits into two processes:

	1. The consumption simply moves tweets from the :class:`~queues.Queue` into the the buffer, another :class:`~queues.Queue`.

	2. The processing wakes up every time window to process the tweets collectd in the buffer so far.
	   While processing, the buffer receives new tweets, but these are only processed in the next time window.

	Apart from maintaining the buffer as a :class:`~queues.Queue`, the state also includes the periodicity, or the length of the time window, in seconds.
	This affects how often the buffer is processed.

	:ivar periodicity: The time window, in seconds, of the buffered consumer, or how often the consumer processes the buffer's contents.
	:vartype periodicity: int
	:ivar buffer: The buffer of objects that have to be processed.
	:vartype buffer: :class:`~queues.Queue`
	"""

	def __init__(self, queue, periodicity=60):
		"""
		Initialize the buffered consumer with its queue and periodicity.

		:param queue: The queue that is consumed.
		:type queue: :class:`~queues.Queue`
		:param periodicity: The time window, in seconds, of the buffered consumer, or how often the consumer processes the buffer's contents.
		:type periodicity: int
		"""

		super(BufferedConsumer, self).__init__(queue)
		self.periodicity = periodicity
		self.buffer = Queue()

	async def run(self, wait=0, max_inactivity=-1, *args, **kwargs):
		"""
		Update the flags to indicate that the consumer is running and start the buffered consumer's two roles:

		1. The consumption simply moves tweets from the :class:`~queues.Queue` into the the buffer, another :class:`~queues.Queue`.

		2. The processing wakes up every time window to process the tweets collectd in the buffer so far.
		   While processing, the buffer receives new tweets, but these are only processed in the next time window.

		Similarly to the :class:`~queues.consumers.Consumer`, the buffered consumer also accepts the ``wait`` and ``max_inactivity`` parameters.

		:param wait: The time in seconds to wait until starting to understand the event.
					 This is used when the file listener spends a lot of time skipping documents.
		:type wait: int
		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, the consumer keeps waiting for input until the maximum time expires.
		:type max_inactivity: int

		:return: The output of the consumption process.
		:rtype: any
		"""

		await asyncio.sleep(wait)
		self._started()
		results = await asyncio.gather(
			self._consume(*args, max_inactivity=max_inactivity, **kwargs),
			self._process(*args, **kwargs),
		)
		self._stopped()
		return results[1]

	async def _consume(self, max_inactivity):
		"""
		Consume the queue.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, the consumer keeps waiting for input until the maximum time expires.
		:type max_inactivity: int
		"""

		"""
		The consumer should keep working until it is stopped.
		"""
		while self.active:
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

	@abstractmethod
	async def _process():
		"""
		Process the buffered items.
		"""

		pass

	async def _sleep(self):
		"""
		Sleep until the window is over.
		The function periodically checks if the consumer has been asked to stop.
		"""

		for i in range(self.periodicity):
			await asyncio.sleep(1)
			if not self.active:
				break

		"""
		If the periodicity is a float, sleep for the remaining milliseconds.
		"""
		if self.active:
			await asyncio.sleep(self.periodicity % 1)

class SimulatedBufferedConsumer(BufferedConsumer):
	"""
	The :class:`~queues.consumers.buffered_consumer.SimulatedBufferedConsumer` is exactly like the :class:`~queues.consumers.buffered_consumer.BufferedConsumer`, but its periodicity is not real-time.
	Whereas the :class:`~queues.consumers.buffered_consumer.BufferedConsumer`'s time window is based on the machine's time, the :class:`~queues.consumers.buffered_consumer.SimulatedBufferedConsumer` looks at the tweet's timestamps.
	This makes the :class:`~queues.consumers.buffered_consumer.SimulatedBufferedConsumer` ideal in situations where it is necessary to simulate the live environment, for example when using a :class:`~twitter.file.FileReader`.
	"""

	def __init__(self, queue, periodicity):
		"""
		Initialize the buffered consumer with its queue and periodicity.

		:param queue: The queue that is consumed.
		:type queue: :class:`~queues.Queue`
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
		while self.buffer.head() is None and self.active:
			await asyncio.sleep(0.1)

		if self.active:
			start = twitter.extract_timestamp(self.buffer.head())

		"""
		Check if the consumer should stop.
		The consumer should stop if:

			#. It has been shut down; or

			#. The buffer's periodicity has been reached.
		"""
		while True:
			if not self.active or twitter.extract_timestamp(self.buffer.tail()) - start >= self.periodicity:
				break

			await asyncio.sleep(0.1)
