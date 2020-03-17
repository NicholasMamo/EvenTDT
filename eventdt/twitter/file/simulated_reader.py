"""
A simulated file listener reads data from a file and adds it to a queue.
It pretends that the event is ongoing, and adds data to the queue according to when they happened.
Therefore high-volume periods enqueue a lot of tweets to the queue.
Low-volume periods enqueue fewer tweets to the queue.
"""

import asyncio
import json
import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from twitter import *
from .reader import FileReader

class SimulatedFileReader(FileReader):
	"""
	The simulated file listener reads data from a file and adds it to a queue.
	This works like a simulation, as if the event was happening at the same time.

	:ivar speed: The reading speed as a function of time.
				 If it is set to 0.5, for example, the event progresses at half the speed.
				 If it is set to 2, the event progresses at double the speed.
	:vartype speed: int
	"""

	def __init__(self, queue, f, max_lines=-1, max_time=-1, speed=1, skip_lines=0, skip_time=0):
		"""
		Create the reader and skip any required lines or time from the file.
		By default, the file reader skips no lines or time.
		The skip rate can be set to sample the file.

		.. note::

			The number of lines and seconds that are skipped depend on the largest number.

		.. note::

			The maximum number of lines and seconds is exclusive.
			That means that if either are 0, no tweets are read.

		:param queue: The queue to which to add incoming tweets.
		:vartype queue: :class:`~queues.queue.Queue`
		:param f: The opened file from where to read the tweets.
		:type f: file
		:param max_lines: The maximum number of lines to read.
						  If the number is negative, it is ignored.
		:type max_lines: int
		:param max_time: The maximum time in seconds to spend reading from the file.
						 The time is taken from tweets' `created_at` attribute.
						 If the number is negative, it is ignored.
		:type max_time: int
		:param speed: The reading speed, considered to be a function of time.
					  If it is set to 0.5, for example, the event progresses at half the speed.
   				 	  If it is set to 2, the event progresses at double the speed.
		:type speed: int
		:param skip_lines: The number of lines to skip from the beginning of the file.
		:type skip_lines: int
		:param skip_time: The number of seconds to skip from the beginning of the file.
		:type skip_time: int

		:raises ValueError: When the speed is zero or negative.
		:raises ValueError: When the number of lines to skip is negative.
		:raises ValueError: When the number of seconds to skip is negative.
		:raises ValueError: When the number of lines to skip after each read is not an integer.
		:raises ValueError: When the number of lines to skip after each read is negative.
		"""

		super(SimulatedFileReader, self).__init__(queue, f, max_lines=max_lines, max_time=max_time)

		"""
		Validate the inputs.
		"""
		if speed <= 0:
			raise ValueError(f"The speed must be positive; received {speed}")

		if skip_lines % 1:
			raise ValueError(f"The number of lines to skip must be an integer; received {skip_lines}")

		if skip_lines < 0:
			raise ValueError(f"The number of lines to skip cannot be negative; received {skip_lines}")

		if skip_time < 0:
			raise ValueError(f"The number of seconds to skip cannot be negative; received {skip_time}")

		self.speed = speed

		self.skip(skip_lines, skip_time)

	def skip(self, lines, time):
		"""
		Skip a number of lines from the file.
		This virtually just reads lines without storing them.

		.. note::

			The number of lines and seconds that are skipped depend on the largest number.

		:param lines: The number of lines to skip.
		:type lines: int
		:param time: The number of seconds to skip from the beginning of the file.
					 The time is taken from tweets' `created_at` attribute.
		:type time: int
		"""

		file = self.file

		"""
		Extract the timestamp from the first tweet, then reset the file pointer.
		"""
		line = file.readline()
		if not line:
			return
		start = extract_timestamp(json.loads(line))
		file.seek(0)

		"""
		Skip a number of lines first.
		"""
		if lines >= 0:
			for i in range(int(lines)):
				file.readline()

		"""
		Skip a number of seconds from the file.
		Once a line that should not be skipped is skipped, the read is rolled back.
		"""
		pos = file.tell()
		line = file.readline()
		if not line:
			return
		next = json.loads(line)
		while extract_timestamp(next) - start < time:
			pos = file.tell()
			line = file.readline()
			if not line:
				break
			next = json.loads(line)

		file.seek(pos)

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
			while ((extract_timestamp(data) - original_start) / self.speed > int(datetime.now().timestamp() - start)):
				await asyncio.sleep(sleep)

			if ((self._max_lines > -1 and self._count > self._max_lines)
				or (int(datetime.now().timestamp() - start) > self._max_time)):
				break

			self.queue.enqueue(data)
