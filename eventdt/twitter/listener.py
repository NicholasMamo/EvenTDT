"""
The TweetListener class is based on Tweepy.
It is used to listen to tweets, processing them as need be when they arrive, until the event ends.
The behavior of this class collects tweets in bulk, then writes them to an always-open file.
Every number of tweets, an update is shown.
"""

from datetime import datetime
from tweepy.streaming import StreamListener

import json

class TweetListener(StreamListener):
	"""
	The listener that handles the collected tweets.

	:cvar THRESHOLD: The number of tweets to accumulate before writing them to file.
	:vartype THRESHOLD: int
	:cvar UPDATE_THRESHOLD: The number of tweets to accumulate before outputting an update to stdout.
	:vartype UPDATE_THRESHOLD: int

	:ivar _file: The opened file pointer to which to write the tweets.
	:vartype _file: file
	:ivar _tweets: The list of read tweets, and which have not been written to file yet.
	:vartype _tweets: list
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

	THRESHOLD = 200
	UPDATE_THRESHOLD = 1000

	def __init__(self, f, max_time=3600, silent=True):
		"""
		Create the listener.
		Simultaneously set the file, the list of tweets and the number of processed tweets.
		By default, the stream continues processing for an hour.

		:param f: The opened file pointer to which to write the tweets.
		:type f: file
		:param max_time: The maximum time (in seconds) to spend reading the file.
			If the number is negative, it is ignored.
		:type max_time: int
		:param silent: A boolean indicating whether the listener should write updates to stdout.
		:type silent: bool
		"""

		self._file = f
		self._tweets = []
		self._count = 0
		self._timestamp = datetime.now().timestamp()
		self._max_time = max_time
		self._start = datetime.now().timestamp()
		self._silent = silent

	def flush(self):
		"""
		Flush the tweets to file.
		"""

		self._file.write("".join(self._tweets))
		self._tweets = []

	def on_data(self, data, override=False):
		"""
		When tweets are received, at them to a list.
		If there are many tweets, save them to file and reset the list of tweets.
		The override flag indicates whether the function should skip checking if the tweet is valid.

		:param data: The received data.
		:type data: dict
		:param override: A boolean that overrides checks for the validity of a tweet.
			This is used in case the tweet's content is filtered to remove the ID.
		:type override: bool
		"""

		data = json.loads(data)
		if override or "id" in data:
			self._tweets.append(json.dumps(data) + "\n")
			self._count += 1

			if (len(self._tweets) >= self.THRESHOLD):
				# flush the tweets
				self.flush()

			if (self._count % self.UPDATE_THRESHOLD == 0 and not self._silent):
				time = datetime.now()
				print("%s:%s\twrote %d tweets\t%.2f tweets/second" % (("0" + str(time.time().hour))[-2:], ("0" + str(time.time().minute))[-2:], self._count, self.UPDATE_THRESHOLD / (time.timestamp() - self._timestamp)))
				self._timestamp = time.timestamp()

			# stop listening if the time limit has been exceeded
			current = datetime.now().timestamp()
			if (current - self._start < self._max_time):
				return True
			else:
				self.flush()
				return False

	def on_error(self, status):
		"""
		Print any errors.

		:param status: The error status.
		:type status: str
		"""

		print("Error:", status)

class FilteredTweetListener(TweetListener):
	"""
	This listener builds on the more simple one, but only retains the given attributes from tweets.
	"""

	def __init__(self, f, attributes, max_time=3600, silent=True):
		"""
		Initialize the listener, retaining only select attributes.

		:param f: The opened file pointer to which to write the tweets.
		:type f: file
		:param attributes: The list of attributes to retain from incoming tweets.
		:type attributes: list
		:param max_time: The maximum time (in seconds) to spend reading the file.
			If the number is negative, it is ignored.
		:type max_time: int
		:param silent: A boolean indicating whether the listener should write updates to stdout.
		:type silent: bool
		"""

		super(FilteredTweetListener, self).__init__(f, max_time, silent=silent)
		self._attributes = attributes

	def on_data(self, data):
		"""
		When tweets are received, first retain only the selected attributes
		The remaining content is then passed on to the parent class for processing.

		:param data: The received data.
		:type data: dict
		"""

		"""
		Filter the data, and do the same for the quoted tweet's data, if it is given.
		"""
		data = json.loads(data)
		if "id" in data:
			filtered_data = { attribute: data.get(attribute, None) for attribute in self._attributes }
			if "quoted_status" in data:
				filtered_quoted_data = { attribute: data["quoted_status"].get(attribute, None) for attribute in self._attributes }
				filtered_data["quoted_status"] = filtered_quoted_data

			return super(FilteredTweetListener, self).on_data(json.dumps(filtered_data) + "\n", override=True)
