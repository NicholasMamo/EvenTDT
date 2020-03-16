"""
A simulated file listener reads data from a file.
It pretends that the event is ongoing, and adds data to the queue according to when they happened.
"""

from datetime import datetime

from .file_listener import FileListener
from .tweet_functions import *

import asyncio
import json
import os
import sys
import time

path = os.path.dirname(__file__)
path = os.path.join(path, '../../')
if path not in sys.path:
	sys.path.insert(1, path)

from logger import logger

class SimulatedFileListener(FileListener):
	"""
	The SimulatedFileListener class takes in a file
	It then proceeds to read it, adding data according to when it was originally received

	:ivar _speed: The reading speed, considered to be a function of time.
	:vartype _speed: int
	:ivar _max_time: The maximum time (in seconds) to spend reading the file.
		If the number is negative, it is ignored.
	:vartype _max_time: int
	:ivar _skip_time: The time (in seconds) to skip from the beginning of the file.
		The time is taken from tweets' `created_at` attribute.
	:vartype _skip_time: int
	"""

	def __init__(self, queue, f,
		max_lines=-1, max_time=3600,
		skip_time=0, speed=1):
		"""
		Create the listener.
		By default, the SimulatedFileListener reads for an hour.

		:param _queue: The queue to which to add incoming tweets.
		:vartype _queue: :class:`~queues.queue.Queue.Queue`
		:param f: The opened file from where to read the tweets.
		:type f: file
		:param max_lines: The maximum number of lines to read.
			If the number is negative, it is ignored.
		:type max_lines: int
		:param max_time: The maximum time (in seconds) to spend reading the file.
			If the number is negative, it is ignored.
		:type max_time: int
		:param skip_time: The time (in seconds) to skip from the beginning of the file.
			The time is taken from tweets' `created_at` attribute.
		:type skip_time: int
		:param speed: The reading speed, considered to be a function of time.
		:type speed: int
		"""

		super(SimulatedFileListener, self).__init__(queue, f, max_lines=max_lines)

		self._speed = speed
		self._max_time = max_time
		self._skip_time = skip_time

	async def read(self):
		"""
		Read the file.
		"""

		"""
		Load the first line and parse it
		At the same time, create the tracking variables
		"""
		sleep = 0.1
		self._file.readline()
		first_line = self._file.readline()
		data = json.loads(first_line)
		last_pos, skip = 0, 0 # the last starting byte read by the file, and the number of lines skipped
		original_start = extract_timestamp(data) # the publicationtime of the first tweet
		"""
		Keep reading lines until the first encountered tweet published after the given number of seconds
		"""
		while extract_timestamp(data) - original_start < self._skip_time :
			last_pos = self._file.tell() # record the file's position
			skip += 1 # a new line has been skipped
			"""
			Read another line
			"""
			line = self._file.readline()
			old_data = dict(data)
			try:
				data = json.loads(line)
			except ValueError as e:
				data = old_data
				continue

		logger.info("Skipped %d tweets" % skip)
		original_start = extract_timestamp(data) # the position is where the stream will start
		self._file.seek(last_pos) # reset the file pointer to the last line read

		start = datetime.now().timestamp() # start timing the procedure
		"""
		Go through each line and add it to the queue
		"""
		for line in self._file:
			"""
			Stop reading if the limit has been reached
			"""
			self._count += 1
			data = json.loads(line)
			if "created_at" not in data:
				continue

			data["time"] = extract_timestamp(data)

			"""
			If the line is 'in the future', stop reading for a bit
			"""
			while ((extract_timestamp(data) - original_start) / self._speed > int(datetime.now().timestamp() - start)):
				await asyncio.sleep(sleep)

			if ((self._max_lines > -1 and self._count > self._max_lines)
				or (int(datetime.now().timestamp() - start) > self._max_time)):
				break

			self._queue.enqueue(data)
