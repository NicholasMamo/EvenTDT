"""
The staggered file reader reads lines a few at a time.
This reader allows a steady stream of tweets to be read and processed.
"""

from .reader import FileReader

class StaggeredFileReader(FileReader):
	"""
	The staggered file reader reads lines a few at a time, then stops and waits.

	:ivar rate: The number of lines to read per second.
	:vartype rate: float
	:ivar skip_lines: The number of lines to skip from the beginning of the file.
	:vartype skip_lines: int
	:ivar skip_time: The time in seconds to skip from the beginning of the file.
					  The time is taken from tweets' `created_at` attribute.
	:vartype skip_time: int
	:ivar skip_rate: The number of lines to skip for each line read.
	:vartype skip_rate: int
	"""

	def __init__(self, queue, f, max_lines=-1, max_time=-1, rate=1, skip_lines=0, skip_time=0, skip_rate=0):
		"""
		Create the listener.
		Simultaneously set the queue, the list of tweets and the number of processed tweets.
		By default, the FileReader skips no lines, though it can be overwritten to skip any number of lines for every one read.
		This makes it possible to sample the file.
		By default, the FileReader has no limit on the number of lines to read per second.

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
		:param skip_lines: The number of lines to skip from the beginning of the file.
		:type skip_lines: int
		:param skip_time: The time (in seconds) to skip from the beginning of the file.
						  The time is taken from tweets' `created_at` attribute.
		:type skip_time: int
		:param max_lines: The maximum number of lines to read.
						  If the number is negative, it is ignored.
		:type max_lines: int
		:param skip_rate: The number of lines to skip for each line read.
		:type skip_rate: int

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
		self.skip_lines = skip_lines
		self.skip_time = skip_time
		self.skip_rate = skip_rate

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
		while get_timestamp(data["created_at"]) - original_start < self.skip_time :
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
		for i in range(skip, self.skip_lines):
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
			for l in range(0, self.skip_rate):
				self._file.readline()

			"""
			If there is a limit on the number of lines to read per minute, sleep a bit
			"""
			if self.rate > 0:
				time.sleep(1/self.rate)
