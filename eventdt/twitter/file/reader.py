"""
A listener that reads input from file and adds it to a queue.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from .tweet_functions import *

import asyncio
import json
import time

class FileListener(ABC):
	"""
	The FileListener is built from the ground up.
	A file is given and it is read, outputting its contents to a Queue.

	:cvar UPDATE_THRESHOLD: The number of tweets to accumulate before outputting an update to stdout.
	:vartype UPDATE_THRESHOLD: int

	:ivar _queue: The queue to which to add tweets.
	:vartype _queue: :class:`~queues.queue.Queue`
	:ivar _count: The number of tweets read so far.
	:vartype _count: int
	:ivar _file: The opened file pointer which contains the tweets.
	:vartype _file: file
	:ivar _max_lines: The maximum number of lines to read.
		If the number is negative, it is ignored.
	:vartype _max_lines: int
	:ivar _max_time: The maximum time (in seconds) to spend reading the file.
		If the number is negative, it is ignored.
	:vartype _max_time: int
	"""

	UPDATE_THRESHOLD = 1000

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
		:param max_time: The maximum time (in seconds) to spend reading the file.
			If the number is negative, it is ignored.
		:type max_time: int
		"""

		self._queue = queue # copy the reference to the queue
		# self._tweets = []
		self._count = 0
		self._file = f
		self._max_lines = max_lines
		self._max_time = max_time

	@abstractmethod
	async def read(self):
		"""
		Read the file.
		"""
		pass
