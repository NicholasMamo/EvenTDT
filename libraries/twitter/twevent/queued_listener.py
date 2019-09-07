"""
The QueuedListener class is based on Tweepy.
A queued listener does very little, if anything at all, with the data.
Instead, it adds tweets to a queue, allowing other consumers to do something with them.
"""

from datetime import datetime
from tweepy.streaming import StreamListener

import json

class QueuedListener(StreamListener):
	"""
	The QueuedListener is built from the ground up.
	The reason behind this is that the output is not flushed to a file, but to a queue.

	:cvar UPDATE_THRESHOLD: The number of tweets to accumulate before outputting an update to stdout.
	:vartype UPDATE_THRESHOLD: int

	:ivar _queue: The queue to which to add incoming tweets.
	:vartype _queue: :class:`queues.queue.queue.Queue`
	:ivar _count: The number of tweets read so far.
	:vartype _count: int
	:ivar _timestamp: The current timestamp.
	:vartype _timestamp: int
	:ivar _max_time: The maximum time (in seconds) to spend reading the file.
		If the number is negative, it is ignored.
	:vartype _max_time: int
	:ivar _start: The timestamp when the listener started waiting for tweets.
	:vartype _start: int
	:ivar _silent: A boolean indicating whether the listener should write updates to stdout.
	:vartype silent: bool
	"""

	UPDATE_THRESHOLD = 1000

	def __init__(self, queue, max_time=3600, silent=True):
		"""
		Create the listener.
		Simultaneously set the queue, the list of tweets and the number of processed tweets.
		By default, the stream continues processing for an hour.

		:param _queue: The queue to which to add incoming tweets.
		:vartype _queue: :class:`queues.queue.queue.Queue`
		:param max_time: The maximum time (in seconds) to spend reading the file.
			If the number is negative, it is ignored.
		:type max_time: int
		:param silent: A boolean indicating whether the listener should write updates to stdout.
		:type silent: bool
		"""

		self._queue = queue # copy the reference to the queue
		# self._tweets = []
		self._count = 0
		self._timestamp = datetime.now().timestamp()
		self._max_time = max_time
		self._start = datetime.now().timestamp()
		self._silent = silent

	def on_data(self, data):
		"""
		When new data is received, add it to the queue.

		:param data: The received data.
		:type data: dict
		"""

		# decode the data
		data = json.loads(data)
		self._queue.enqueue(data)
		self._count += 1

		if (self._count % self.UPDATE_THRESHOLD == 0 and not self._silent):
			time = datetime.now()
			print("%s:%s\twrote %d tweets\t%.2f tweets/second" % (("0" + str(time.time().hour))[-2:], ("0" + str(time.time().minute))[-2:], self._count, self.UPDATE_THRESHOLD / (time.timestamp() - self._timestamp)))
			self._timestamp = time.timestamp()

		# stop listening if the time limit has been exceeded
		current = datetime.now().timestamp()
		if (current - self._start < self._max_time):
			return True
		else:
			return False

	def on_error(self, status):
		"""
		Print any errors.

		:param status: The error status.
		:type status: str
		"""

		print(status)
