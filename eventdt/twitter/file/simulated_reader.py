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
from twitter.file import FileReader

class SimulatedFileReader(FileReader):
	"""
	The simulated file listener reads data from a file and adds it to a queue.
	This works like a simulation, as if the event was happening at the same time.

	:ivar speed: The reading speed as a function of time.
				 If it is set to 0.5, for example, the event progresses at half the speed.
				 If it is set to 2, the event progresses at double the speed.
	:vartype speed: int
	"""

	def __init__(self, queue, f, max_lines=-1, max_time=-1, skip_lines=0, skip_time=0, speed=1):
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
						 The maximum time is understood to be i nterms of the corpus' time.
						 The time is taken from tweets' `created_at` attribute.
						 If the number is negative, it is ignored.
		:type max_time: int
		:param skip_lines: The number of lines to skip from the beginning of the file.
		:type skip_lines: int
		:param skip_time: The number of seconds to skip from the beginning of the file.
		:type skip_time: int
		:param speed: The reading speed, considered to be a function of time.
					  If it is set to 0.5, for example, the event progresses at half the speed.
   				 	  If it is set to 2, the event progresses at double the speed.
		:type speed: int

		:raises ValueError: When the speed is zero or negative.
		:raises ValueError: When the number of lines to skip is not an integer.
		:raises ValueError: When the number of lines to skip is negative.
		:raises ValueError: When the number of seconds to skip is negative.
		"""

		super(SimulatedFileReader, self).__init__(queue, f, max_lines=max_lines, max_time=max_time,
														    skip_lines=skip_lines, skip_time=skip_time)

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

	@FileReader.reading
	async def read(self):
		"""
		Read the file.
		Tweets are added as a dictionary to the queue.
		"""

		file = self.file

		"""
		Extract the timestamp from the first tweet, then reset the file pointer.
		"""
		pos = file.tell()
		line = file.readline()
		if not line:
			return
		first = extract_timestamp(json.loads(line))
		file.seek(pos)

		"""
		Go through each line and add it to the queue.
		"""
		start = time.time()
		for i, line in enumerate(file):
			tweet = json.loads(line)
			created_at = extract_timestamp(tweet)

			"""
			If the maximum number of lines, or the time, has been exceeded, stop reading.
			"""
			if self.max_lines >= 0 and i >= self.max_lines:
				break

			if self.max_time >= 0 and created_at - first >= self.max_time:
				break

			"""
			If the tweet is 'in the future', stop reading until the reader catches up.
			It is only after it catches up that the tweet is added to the queue.
			"""
			elapsed = time.time() - start
			if (created_at - first) / self.speed > elapsed:
				await asyncio.sleep((created_at - first) / self.speed - elapsed)

			"""
			If the reader has been interrupted, stop reading.
			"""
			if not self.active:
				break

			self.queue.enqueue(tweet)
