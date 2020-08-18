"""
File readers emulate the Twitter stream by reading corpora and feeding them into a :class:`~queues.queue.Queue` so that they can be processed by :ref:`consumers <consumers>`.
These readers expect that the corpora were collected using a :ref:`listener <twitter_listeners>`.
The input files have one object on each line.

File readers are useful in evaluation or experimental settings.
By simulating the Twitter stream, the different file readers can be used to replicate the original, real-time setting of a stream.
"""

from abc import ABC, abstractmethod

from .. import *

import asyncio

class FileReader(ABC):
	"""
	The file reader reads tweets from a file and outputs its contents to a queue.

	:ivar queue: The queue to which to add tweets.
	:vartype queue: :class:`~queues.queue.Queue`
	:ivar file: The opened file pointer which contains the tweets.
	:vartype file: file
	:ivar max_lines: The maximum number of lines to read.
					 If the number is negative, it is ignored.
	:vartype max_lines: int
	:ivar max_time: The maximum time in seconds to spend reading from the file.
					The time is taken from tweets' `created_at` attribute.
					If the number is negative, it is ignored.
	:vartype max_time: int
	:ivar active: A boolean indicating whether the reader is still reading data.
	:vartype active: bool
	:ivar stopped: A boolean indicating whether the consumer has finished processing.
	:vartype stopped: bool
	"""

	def __init__(self, queue, f, max_lines=-1, max_time=-1):
		"""
		Create the listener.
		Simultaneously set the queue, the list of tweets and the number of processed tweets.

		:param queue: The queue to which to add the tweets.
		:type queue: :class:`~queues.queue.Queue`
		:param f: The opened file from where to read the tweets.
		:type f: file
		:param max_lines: The maximum number of lines to read.
						  If the number is negative, it is ignored.
		:type max_lines: int
		:param max_time: The maximum time in seconds to spend reading from the file.
						 The time is taken from tweets' `created_at` attribute.
						 If the number is negative, it is ignored.
		:type max_time: int
		"""

		self.queue = queue
		self.file = f
		self.max_lines = max_lines
		self.max_time = max_time
		self.active = False
		self.stopped = True

	@abstractmethod
	async def read(self):
		"""
		Read the file and add each line as a dictionary to the queue.
		"""

		pass

	def stop(self):
		"""
		Set a flag to stop accepting new objects.

		.. note::
			Contrary to the name of the function, the function sets the `active` flag, not the `stopped` flag.
			This function merely asks that the consumer stops accepting new objects for processing.
		"""

		self.active = False

from .simulated_reader import SimulatedFileReader
from .staggered_reader import StaggeredFileReader
