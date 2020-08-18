"""
The :class:`~twitter.file.staggered_reader.StaggeredFileReader` is a file reader that reads a corpus at a constant pace.
This results in a steady and predictable stream of tweets.
Therefore the :class:`~twitter.file.staggered_reader.StaggeredFileReader` allows the application to receive as many tweets as it can handle, and handle them as well as it can.
For this reason, it is most opportune when the :ref:`consumer's <consumers>` performance under strain is not important, but its results are.
"""

import json

import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from twitter import *
from twitter.file import FileReader

class StaggeredFileReader(FileReader):
	"""
	The staggered file reader reads lines a few at a time, then stops and waits.

	:ivar rate: The number of lines to read per second.
	:vartype rate: float
	:ivar skip_rate: The number of lines to skip for each line read.
	:vartype skip_rate: int
	"""

	def __init__(self, queue, f, max_lines=-1, max_time=-1, skip_lines=0, skip_time=0, rate=1, skip_rate=0):
		"""
		Create the reader and skip any required lines or time from the file.
		By default, the file reader skips no lines or time.
		The skip rate can be set to sample the file.

		.. note::

			The number of lines and seconds that are skipped depend on the largest number.

		.. note::

			The maximum number of lines and seconds is exclusive.
			That means that if either are 0, no tweets are read.

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
		:param skip_lines: The number of lines to skip from the beginning of the file.
		:type skip_lines: int
		:param skip_time: The number of seconds to skip from the beginning of the file.
		:type skip_time: int
		:param rate: The number of lines to read per second.
		:type rate: float
		:param skip_rate: The number of lines to skip for each line read.
		:type skip_rate: int

		:raises ValueError: When the rate is not an integer.
		:raises ValueError: When the rate is zero or negative.
		:raises ValueError: When the number of lines to skip is not an integer.
		:raises ValueError: When the number of lines to skip is negative.
		:raises ValueError: When the number of seconds to skip is negative.
		:raises ValueError: When the number of lines to skip after each read is not an integer.
		:raises ValueError: When the number of lines to skip after each read is negative.
		"""

		super(StaggeredFileReader, self).__init__(queue, f, max_lines=max_lines, max_time=max_time,
														    skip_lines=skip_lines, skip_time=skip_time)

		"""
		Validate the inputs.
		"""
		if rate % 1:
			raise ValueError(f"The rate must be an integer; received {rate}")

		if rate <= 0:
			raise ValueError(f"The rate must be positive; received {rate}")

		if skip_lines % 1:
			raise ValueError(f"The number of lines to skip must be an integer; received {skip_lines}")

		if skip_lines < 0:
			raise ValueError(f"The number of lines to skip cannot be negative; received {skip_lines}")

		if skip_time < 0:
			raise ValueError(f"The number of seconds to skip cannot be negative; received {skip_time}")

		if skip_rate % 1:
			raise ValueError(f"The rate of lines to skip after each read must be an integer; received {skip_rate}")

		if skip_rate < 0:
			raise ValueError(f"The rate of lines to skip after each read cannot be negative; received {skip_rate}")

		self.rate = rate
		self.skip_rate = skip_rate

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
		Go through each line and add it to the queue
		Time how long it takes to read each tweet to avoid extra time skipping.
		"""
		for i, line in enumerate(file):
			start = time.time()

			"""
			If the maximum number of lines, or time, has been exceeded, stop reading.
			"""
			if self.max_lines >= 0 and i >= self.max_lines:
				break

			tweet = json.loads(line)
			if self.max_time >= 0 and extract_timestamp(tweet) - first >= self.max_time:
				break

			"""
			If the reader has been interrupted, stop reading.
			"""
			if not self.active:
				break

			self.queue.enqueue(tweet)

			"""
			Skip some lines if need be.
			"""
			for _ in range(self.skip_rate):
				file.readline()

			"""
			If there is a limit on the number of lines to read per minute, sleep a bit.
			The calculation considers how long reading the tweet took.
			"""
			elapsed = time.time() - start
			if self.rate > 0:
				sleep = 1/self.rate - elapsed
				if sleep > 0:
					time.sleep(sleep)
