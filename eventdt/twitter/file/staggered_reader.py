"""
The staggered file reader reads lines a few at a time.
This reader allows a steady stream of tweets to be read and processed.
"""

import json

import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from .reader import FileReader
from twitter import *

class StaggeredFileReader(FileReader):
	"""
	The staggered file reader reads lines a few at a time, then stops and waits.

	:ivar rate: The number of lines to read per second.
	:vartype rate: float
	:ivar skip_rate: The number of lines to skip for each line read.
	:vartype skip_rate: int
	"""

	def __init__(self, queue, f, max_lines=-1, max_time=-1, rate=1, skip_rate=0, skip_lines=0, skip_time=0):
		"""
		Create the listener.
		Simultaneously set the queue, the list of tweets and the number of processed tweets.
		By default, the FileReader skips no lines, though it can be overwritten to skip any number of lines for every one read.
		This makes it possible to sample the file.
		By default, the FileReader has no limit on the number of lines to read per second.

		.. note::

			The number of lines and seconds that are skipped depend on the largest number.

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
		:param rate: The number of lines to read per second.
		:type rate: float
		:param skip_rate: The number of lines to skip for each line read.
		:type skip_rate: int
		:param skip_lines: The number of lines to skip from the beginning of the file.

		:raises ValueError: When the rate is not an integer.
		:raises ValueError: When the rate is zero or negative.
		:raises ValueError: When the number of lines to skip is negative.
		:raises ValueError: When the number of seconds to skip is negative.
		:raises ValueError: When the number of lines to skip after each read is not an integer.
		:raises ValueError: When the number of lines to skip after each read is negative.
		"""

		super(StaggeredFileReader, self).__init__(queue, f, max_lines=max_lines, max_time=max_time)

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
