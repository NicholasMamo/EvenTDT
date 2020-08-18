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
	The :class:`~twitter.file.FileReader` is a class that describes the general state of file readers.

	Generally speaking, any file reader should implement the :func:`~twitter.file.FileReader.read` function, which reads tweets and adds them to the :class:`~queues.queue.Queue`.
	This :class:`~queues.queue.Queue` is one of the variables that make up the :class:`~twitter.file.FileReader`'s state.
	Accompanying it is the ``file``, which is the pointer to an opened file.

	The :class:`~twitter.file.FileReader` also stores the maximum number of lines, ``max_lines``, and the maximum time, in seconds, ``max_time`` it should spend reading tweets from the corpora.
	These variables refer to the number of lines to read from the file, and the maximum time as represented in the corpus.
	For example, if the ``max_time`` is 60 seconds, the reader reads all the tweets from the corpus published within the first minute.
	It does not refer to the processing time it should spend reading the corpus.

	The other two variables in the :class:`~twitter.file.FileReader`'s state are the ``active`` and ``stopped`` flags:

	- The ``active`` flag indicates whether the reader is still reading data.
	  It is possible that the reader is in the process of reading data while the ``active`` flag is set to ``False``.

    - The ``stopped`` flag indicates whether the reader has finished processing and is idle.

	To stop reading data, call the :func:`~twitter.file.FileReader.stop` function.
	This function sets the ``active`` flag to ``False``.
	When the :func:`~twitter.file.FileReader.read` function actually finishes reading, it sets the ``stopped`` variable to ``True``.

	:ivar queue: The queue to which to add tweets.
	:vartype queue: :class:`~queues.queue.Queue`
	:ivar file: The opened file pointer from where to read the tweets.
	:vartype file: file
	:ivar max_lines: The maximum number of lines to read.
					 If the number is negative, it is ignored.
	:vartype max_lines: int
	:ivar max_time: The maximum time in seconds to spend reading from the file.
					The time is taken from tweets' timestamps.
					If the number is negative, it is ignored.
	:vartype max_time: int
	:ivar active: A boolean indicating whether the reader is still reading data.
	:vartype active: bool
	:ivar stopped: A boolean indicating whether the consumer has finished processing.
	:vartype stopped: bool
	"""

	def __init__(self, queue, f, max_lines=-1, max_time=-1):
		"""
		Create the file reader with the :class:`~queues.queue.Queue` where to add tweets and the file from where to read them.
		The ``max_lines`` and ``max_time`` parameters can be used to read only a part of the corpus.

		:param queue: The queue to which to add the tweets.
		:type queue: :class:`~queues.queue.Queue`
		:param f: The opened file from where to read the tweets.
		:type f: file
		:param max_lines: The maximum number of lines to read.
						  If the number is negative, it is ignored.
		:type max_lines: int
		:param max_time: The maximum time in seconds to spend reading from the file.
						 The time is taken from tweets' timestamps.
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

		This function should set the ``active`` flag to ``True`` and the ``stopped`` flag to ``False`` before starting to read tweets.
		After it finishes reading the tweets, it should set the ``active`` flag to ``False`` and the ``stopped`` flag to ``True``.
		"""

		# TODO: Set the `active` and `stopped` flags using a decorator.

		pass

	def stop(self):
		"""
		Set a flag to stop accepting new objects.

		.. note::
			Contrary to the name of the function, the function sets the ``active`` flag to ``False``, not the ``stopped`` flag.
			This function merely asks that the consumer stops accepting new objects for processing.
		"""

		self.active = False

from .simulated_reader import SimulatedFileReader
from .staggered_reader import StaggeredFileReader
