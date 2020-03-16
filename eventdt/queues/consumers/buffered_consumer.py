"""
A buffered consumer saves content and only actually processes it later.
It is built on the basic consumer.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from ..queue.queue import Queue
from .consumer import Consumer

import asyncio
import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '../../')
if path not in sys.path:
	sys.path.insert(1, path)

from logger import logger

class BufferedConsumer(Consumer):
	"""
	The BufferedConsumer is built on the basic Consumer.
	It adds an important function - the actual processing stage, which is different from the consuming phase.
	The consumer function stores the elements, whereas the process function empties this buffer and processes it.

	:ivar _buffer: A buffer of tweets that have been processed, but which are not part of a checkpoint yet.
	:vartype _buffer: :class:`~queues.queue.queue.Queue`
	:ivar _periodicity: The time window (in seconds) of the buffered consumer, or how often it is invoked.
	:vartype _periodicity: int
	"""

	def __init__(self, queue, periodicity):
		"""
		Initialize the BufferedConsumer with its queue, periodicity and buffer.

		:param queue: The queue that is consumed.
		:type queue: :class:`~queues.queue.queue.Queue`
		:param periodicity: The time window (in seconds) of the buffered consumer, or how often it is invoked.
		:type periodicity: int
		"""

		super(BufferedConsumer, self).__init__(queue)
		self._buffer = Queue()
		self._periodicity = periodicity

	async def run(self, initial_wait=0, max_time=3600, max_inactivity=-1):
		"""
		Invokes the consume and process method.

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
		results = await asyncio.gather(
			self._consume(max_time=max_time, max_inactivity=max_inactivity),
			self._process(),
		)
		return (results[1], )

	async def _consume(self, max_time=3600, max_inactivity=5):
		"""
		Consume the next elemenet from the queue and add it to the buffer.

		:param max_time: The maximum time (in seconds) to spend understanding the event.
			It may be interrupted if the queue is inactive for a long time.
		:type max_time: int
		:param max_inactivity: The maximum time (in seconds) to wait idly without input before stopping.
			If it is negative, it is ignored.
		:type max_inactivity: int
		"""

		"""
		The consumer should keep working until it is forcibly stopped or its time runs out
		"""
		start = datetime.now().timestamp()
		while True and self._active and (datetime.now().timestamp() - start < max_time):
			"""
			If the queue is idle, stop waiting for input
			"""
			inactive = await self._wait_for_input(max_inactivity=max_inactivity)
			if not inactive:
				break

			"""
			The consuming phase should empty the queue and store the elements in the buffer
			"""
			while self._queue.length() > 0:
				element = self._queue.dequeue()
				self._buffer.enqueue(element)

		self._stopped = True # set a boolean indicating that the consumer has successfully stopped working

	@abstractmethod
	async def _process():
		"""
		Process the buffered items.
		"""

		pass

	async def _sleep(self):
		"""
		Sleep until the window is over, but periodically check if the consumer should stop.
		"""

		sleep = 1

		for i in range(0, int(self._periodicity/sleep)):
			await asyncio.sleep(sleep)
			if self._stopped:
				break

		"""
		Before finishing the sleep cycle, check if the consumer should stop
		"""
		if not self._stopped:
			await asyncio.sleep(self._periodicity % sleep)

class PseudoBufferedConsumer(BufferedConsumer):
	"""
	The PseudoBufferedConsumer builds on the BufferedConsumer.
	However, its periodicity is not real-time.
	Instead, it gets the time from the incoming message.
	This class can be used in a simulated environment, such as when data has been collected.
	In this case, it allows the data to be consumed at the rate that it is read.
	"""

	def __init__(self, queue, periodicity, time="time"):
		"""
		Initialize the PseudoBufferedConsumer with its queue, periodicity and buffer.
		The time parameter is the field that the sleep function checks to know when it should awake.

		:param queue: The queue that is consumed.
		:type queue: :class:`~queues.queue.queue.Queue`
		:param periodicity: The time window (in seconds) of the buffered consumer, or how often it is invoked.
		:type periodicity: int
		:param time: The label of the timestamp.
		:type time: :class:`~object`
		"""

		super(PseudoBufferedConsumer, self).__init__(queue, periodicity)
		self._time = time

	async def _sleep(self):
		"""
		Sleep until the pseudo-window is over, but periodically check if the consumer should stop.
		"""

		"""
		Wait until there's something in the Queue, to get a reference point for when the sleep should end.
		"""
		sleep = 0.1
		while self._buffer.head() is None and not self._stopped:
			await asyncio.sleep(sleep)

		if not self._stopped:
			start = self._buffer.head()[self._time]

		while True:
			"""
			Check if the consumer should stop.
			The consumer should stop if:
				it has been shut down or
				the buffer's periodicity has been reached.
			"""
			if self._stopped or self._buffer.tail()[self._time] - start >= self._periodicity:
				break

			await asyncio.sleep(sleep)
