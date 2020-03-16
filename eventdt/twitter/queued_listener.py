"""
The queued listener is based on Tweepy.
All a queued listener does with the data is add it to a queue.
It is up to other consumers to process it.
"""

from datetime import datetime
from tweepy.streaming import StreamListener

import json
import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from .listener import TweetListener
from logger import logger

class QueuedListener(StreamListener):
	"""
	The queued listener diverges enough from the :class:`~twitter.listener.TweetListener` that it is built from the ground up.
	Incoming tweets are not added to a queue.

	:ivar queue: The queue to which to add incoming tweets.
	:vartype queue: :class:`~queues.queue.Queue`
	:ivar tweets: The list of read tweets that have not been written to file yet.
	:vartype tweets: list
	:ivar max_time: The maximum time in seconds to spend reading the file.
	:vartype max_time: int
	:ivar start: The timestamp when the listener started waiting for tweets.
	:vartype start: int
	:ivar attributes: The attributes to save from each tweet.
					  If `None` is given, the entire tweet objects are saved.
	:vartype attributes: list of str or None
	"""

	def __init__(self, queue, max_time=3600, attributes=None):
		"""
		Create the listener.
		Simultaneously set the queue, the list of tweets and the number of processed tweets.
		By default, the stream continues processing for an hour.

		:param queue: The queue to which to add incoming tweets.
		:vartype queue: :class:`~queues.queue.Queue`
		:param max_time: The maximum time in seconds to spend reading the file.
		:type max_time: int
		:param attributes: The attributes to save from each tweet.
						   If `None` is given, the entire tweet objects are saved.
		:type attributes: list of str or None
		"""

		self.queue = queue
		self.max_time = max_time
		self.start = time.time()
		self.attributes = attributes or [ ]

	def on_data(self, data):
		"""
		When tweets are received, add them to a list.
		If there are many tweets, save them to file and reset the list of tweets.
		The override flag indicates whether the function should skip checking if the tweet is valid.

		Data is added as a dictionary to the queue.

		:param data: The received data.
		:type data: str

		:return: A boolean indicating if the listener has finished reading tweets.
		:rtype: bool
		"""

		tweet = json.loads(data)
		if 'id' in tweet:
			tweet = self.filter(tweet)
			self.queue.enqueue(tweet)

			"""
			Stop listening if the time limit has been exceeded.
			To stop listening, the function returns `False`
			"""
			current = time.time()
			return current - self.start < self.max_time

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
