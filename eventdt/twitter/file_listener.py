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
	:vartype _queue: :class:`~queues.queue.queue.Queue`
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
		:type queue: :class:`~queues.queue.queue.Queue`
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

class StaggeredFileListener(FileListener):
	"""
	The StaggeredFileListener reads a line, then stops and waits.

	:ivar _skip_lines: The number of lines to skip from the beginning of the file.
	:vartype _skip_lines: int
	:ivar _skip_time: The time (in seconds) to skip from the beginning of the file.
		The time is taken from tweets' `created_at` attribute.
	:vartype _skip_time: int
	:ivar _skip_rate: The number of lines to skip for each line read.
	:vartype _skip_rate: int
	:ivar _lines_per_second: The number of lines to read per second.
	:vartype lines_per_second: float
	"""

	def __init__(self, queue, f, skip_lines=0, skip_time=0, max_lines=-1, max_time=-1, skip_rate=0, lines_per_second=-1):
		"""
		Create the listener.
		Simultaneously set the queue, the list of tweets and the number of processed tweets.
		By default, the FileListener skips no lines, though it can be overwritten to skip any number of lines for every one read.
		This makes it possible to sample the file.
		By default, the FileListener has no limit on the number of lines to read per second.

		:param queue: The queue to which to add the tweets.
		:type queue: :class:`~queues.queue.queue.Queue`
		:param f: The opened file from where to read the tweets.
		:type f: file
		:param skip_lines: The number of lines to skip from the beginning of the file.
		:type skip_lines: int
		:param skip_time: The time (in seconds) to skip from the beginning of the file.
			The time is taken from tweets' `created_at` attribute.
		:type skip_time: int
		:param max_lines: The maximum number of lines to read.
			If the number is negative, it is ignored.
		:type max_lines: int
		:param max_time: The maximum time (in seconds) to spend reading the file.
			If the number is negative, it is ignored.
		:type max_time: int
		:param skip_rate: The number of lines to skip for each line read.
		:type skip_rate: int
		:param lines_per_second: The number of lines to read per second.
		:type lines_per_second: float
		"""

		super(StaggeredFileListener, self).__init__(queue, f, max_lines=max_lines, max_time=max_time)

		self._skip_lines = skip_lines
		self._skip_time = skip_time
		self._skip_rate = skip_rate
		self._lines_per_second = lines_per_second

	async def read(self):
		"""
		Read the file.
		"""

		"""
		Load the first line and parse it
		At the same time, create the tracking variables
		"""
		first_line = self._file.readline()
		data = json.loads(first_line)
		last_pos, skip = 0, 0 # the last starting byte read by the file, and the number of lines skipped
		original_start = get_timestamp(data["created_at"]) # the publicationtime of the first tweet
		"""
		Keep reading lines until the first encountered tweet published after the given number of seconds
		"""
		while get_timestamp(data["created_at"]) - original_start < self._skip_time :
			last_pos = self._file.tell() # record the file's position
			skip += 1 # a new line has been skipped
			"""
			Read another line
			"""
			line = self._file.readline()
			data = json.loads(line)

		original_start = get_timestamp(data["created_at"]) # the position is where the stream will start
		self._file.seek(last_pos) # reset the file pointer to the last line read

		"""
		Skip a number of lines
		"""
		for i in range(skip, self._skip_lines):
			self._file.readline()

		start = datetime.now().timestamp() # start timing the procedure

		"""
		Go through each line and add it to the queue
		"""
		for line in self._file:
			"""
			Stop reading if the limit has been reached
			"""
			self._count += 1
			if ((self._max_lines > -1 and self._count > self._max_lines)
				or (self._max_time > -1 and (datetime.now().timestamp() - start) > self._max_time)):
				break

			data = json.loads(line)
			data["time"] = get_timestamp(data["created_at"])
			self._queue.enqueue(data)

			"""
			Skip some lines if need be
			"""
			for l in range(0, self._skip_rate):
				self._file.readline()

			"""
			If there is a limit on the number of lines to read per minute, sleep a bit
			"""
			if self._lines_per_second > 0:
				time.sleep(1/self._lines_per_second)
