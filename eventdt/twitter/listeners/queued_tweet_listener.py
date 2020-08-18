"""
Like the :class:`~twitter.listeners.tweet_listener.TweetListener`, the :class:`~twitter.listeners.queued_tweet_listener.QueuedTweetListener` is based on Tweepy and its :class:`tweepy.stream.StreamListener`.
However, it differs from the :class:`~twitter.listeners.tweet_listener.TweetListener` because it does not save tweets to a file, but it adds them to a :class:`~queues.queue.Queue`.
This listener is preferrable when there is no need to save tweets as they are processed as soon as they arrive.
Therefore the :class:`~twitter.listeners.queued_tweet_listener.QueuedTweetListener` is designed to work out of the box with :ref:`consumers <consumers>`.
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

from logger import logger

class QueuedTweetListener(StreamListener):
	"""
	The :class:`~twitter.listeners.queued_tweet_listener.QueuedTweetListener` handles the tweets that the stream sends.
	It does not configure the stream, but only processes the tweets it sends.

	The :class:`~twitter.listeners.queued_tweet_listener.QueuedTweetListener` differs from the :class:`~twitter.listeners.tweet_listener.TweetListener` because it adds these tweets to a :class:`~queues.queue.Queue` instead of saving them to a file
	Therefore the class maintains the :class:`~queues.queue.Queue` as part of its state.

	Although listeners do not control the stream's specifications, they can stop it.
	The :class:`~twitter.listeners.queued_tweet_listener.QueuedTweetListener` receives the ``max_time`` parameter which specifies, in seconds, the time to spend receiving tweets.
	The :func:`~twitter.listeners.queued_tweet_listener.QueuedTweetListener.on_data` function stops the stream when it receives a tweet after this time expires.

	Like the :class:`~twitter.listeners.tweet_listener.TweetListener`, the :class:`~twitter.listeners.queued_tweet_listener.QueuedTweetListener` can also filter tweets by removing certain attributes.
	The attributes that should be retained are specified using the ``attributes`` parameter and are saved as part of the class' state.

	:ivar queue: The queue to which to add incoming tweets.
	:vartype queue: :class:`~queues.queue.Queue`
	:ivar max_time: The maximum time in seconds to spend reading the file.
	:vartype max_time: int
	:ivar start: The timestamp when the listener started waiting for tweets.
	:vartype start: int
	:ivar attributes: The attributes to save from each tweet.
					  If ``None`` is given, the entire tweet objects are saved.
	:vartype attributes: list of str or None
	"""

	def __init__(self, queue, max_time=3600, attributes=None):
		"""
		Create the listener.
		Simultaneously set the queue.
		By default, the stream continues processing for an hour.

		:param queue: The queue to which to add incoming tweets.
		:vartype queue: :class:`~queues.queue.Queue`
		:param max_time: The maximum time in seconds to spend reading the file.
		:type max_time: int
		:param attributes: The attributes to save from each tweet.
						   If ``None`` is given, the entire tweet objects are saved.
		:type attributes: list of str or None
		"""

		self.queue = queue
		self.max_time = max_time
		self.start = time.time()
		self.attributes = attributes or [ ]

	def on_data(self, data):
		"""
		When the listener receives tweets, add them to the queue immediately after filtering out any attributes that are not required.
		When the function adds tweets to the list, they are dictionaries, ready to be processed by the consumer.

		This function also checks if the listener has been listening for tweets for a long time.
		If it exceeds the ``max_time``, the function returns ``False`` so that the stream ends.

		:param data: The received data.
		:type data: str

		:return: A boolean indicating if the listener has finished reading tweets.
				 It is set to ``True`` normally.
				 When the elapsed time exceeds the ``max_time`` parameter, the :class:`~twitter.listeners.tweet_listener.TweetListener` returns ``False``.
				 This instructs the stream to stop receiving tweets.
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
