"""
A reader does not collect tweets from Twitter, but reads them from a file.
The queue and file are given in the constructor.
Reading can be started asynchronously using the :func:`~twitter.file.reader.FileReader.read` function.
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
	"""

	def __init__(self, queue, f, max_lines=-1):
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
		"""

		self.queue = queue
		self.file = f
		self.max_lines = max_lines

	@abstractmethod
	async def read(self):
		"""
		Read the file and add each line as a dictionary to the queue.
		"""

		pass
