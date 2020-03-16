"""
The TweetListener class is based on Tweepy.
It is used to listen to tweets, processing them as need be when they arrive, until the event ends.
The behavior of this class collects tweets in bulk, then writes them to an always-open file.
"""

from tweepy.streaming import StreamListener

import json
import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from logger import logger

class TweetListener(StreamListener):
	"""
	The listener that handles the collected tweets.

	:cvar THRESHOLD: The number of tweets to accumulate before writing them to file.
	:vartype THRESHOLD: int
	:cvar UPDATE_THRESHOLD: The number of tweets to accumulate before outputting an update to stdout.
	:vartype UPDATE_THRESHOLD: int

	:ivar file: The opened file pointer to which to write the tweets.
	:vartype file: file
	:ivar tweets: The list of read tweets that have not been written to file yet.
	:vartype tweets: list
	:ivar max_time: The maximum time in seconds to spend reading the file.
	:vartype max_time: int
	:ivar start: The timestamp when the listener started waiting for tweets.
	:vartype start: int
	:ivar silent: A boolean indicating whether the listener should write updates to stdout.
	:vartype silent: bool
	:ivar attributes: The attributes to save from each tweet.
					  If `None` is given, the entire tweet objects are saved.
	:vartype attributes: list of str or None
	"""

	THRESHOLD = 200

	def __init__(self, f, max_time=3600, silent=True, attributes=None):
		"""
		Create the listener.
		Simultaneously set the file, the list of tweets and the number of processed tweets.
		By default, the stream continues processing for an hour.

		:param f: The opened file pointer to which to write the tweets.
		:type f: file
		:param max_time: The maximum time in seconds to spend reading the file.
		:type max_time: int
		:param silent: A boolean indicating whether the listener should write updates to stdout.
		:type silent: bool
		:param attributes: The attributes to save from each tweet.
						   If `None` is given, the entire tweet objects are saved.
		:type attributes: list of str or None
		"""

		self.file = f
		self.tweets = []
		self.max_time = max_time
		self.start = time.time()
		self.silent = silent
		self.attributes = attributes or [ ]

	def flush(self):
		"""
		Flush the tweets to file.
		"""

		self.file.write(''.join(self.tweets))
		self.tweets = [ ]

	def on_data(self, data):
		"""
		When tweets are received, add them to a list.
		If there are many tweets, save them to file and reset the list of tweets.
		The override flag indicates whether the function should skip checking if the tweet is valid.

		:param data: The received data.
		:type data: dict

		:return: A boolean indicating if the listener has finished reading tweets.
		:rtype: bool
		"""

		data = json.loads(data)
		if 'id' in data:
			self.tweets.append(json.dumps(data) + "\n")

			"""
			If the tweets have exceeded the threshold of tweets, save them to the file.
			"""
			if len(self.tweets) >= self.THRESHOLD:
				self.flush()

			"""
			Stop listening if the time limit has been exceeded.
			To stop listening, the function returns `False`, but not before saving any pending tweets.
			"""
			current = time.time()
			if (current - self.start < self.max_time):
				return True
			else:
				self.flush()
				return False

	def filter(self, tweet):
		"""
		Filter the given tweet using the attributes.
		If no attributes are given, the tweet's attributes are all retained.

		:param tweet: The tweet attributes as a dictionary.
					  The keys are the attribute names and the values are the data.
		:type tweet: dict

		:return: The tweet as a dictionary with only the required attributes.
		:rtype: dict
		"""

		"""
		Return the tweet as it is if there are no attributes to filter.
		"""
		if not self.attributes:
			return tweet

		"""
		Otherwise, keep only the attributes in the list.
		"""
		return { attribute: tweet.get(attribute) for attribute in self.attributes }

	def on_error(self, status):
		"""
		Print any errors.

		:param status: The error status.
		:type status: str
		"""

		logger.error(str(status))
