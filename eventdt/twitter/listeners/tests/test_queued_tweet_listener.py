"""
Test the functionality of the QueuedTweetListener.
"""

import json
import os
import sys
import time
import unittest

from datetime import datetime
from tweepy import OAuthHandler, Stream

paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..'),
 		  os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

from config import conf
from queues import Queue
from listeners import QueuedTweetListener

class TestQueuedTweetListener(unittest.TestCase):
	"""
	Test the functionality of the QueuedTweetListener.
	"""

	def authenticate(self):
		"""
		Create the authentication object.

		:return: The authentication object.
		:rtype: :class:`tweepy.OAuthHandler`
		"""

		auth = OAuthHandler(conf.ACCOUNTS[0]['CONSUMER_KEY'], conf.ACCOUNTS[0]['CONSUMER_SECRET'])
		auth.set_access_token(conf.ACCOUNTS[0]['ACCESS_TOKEN'], conf.ACCOUNTS[0]['ACCESS_TOKEN_SECRET'])
		return auth

	def test_collect(self):
		"""
		Test collecting data very simply.
		"""

		queue = Queue()
		listener = QueuedTweetListener(queue, max_time=2)
		stream = Stream(self.authenticate(), listener)
		stream.filter(track=[ 'is' ])

		tweets = queue.dequeue_all()
		self.assertTrue(tweets)
		for tweet in tweets:
			self.assertTrue('id' in tweet)

	def test_collect_filtered(self):
		"""
		Test collecting data with a few attributes.
		"""

		queue = Queue()
		listener = QueuedTweetListener(queue, max_time=2, attributes=[ 'id', 'text' ])
		stream = Stream(self.authenticate(), listener)
		stream.filter(track=[ 'is' ])

		tweets = queue.dequeue_all()
		self.assertTrue(tweets)
		for tweet in tweets:
			self.assertEqual(set([ 'id', 'text' ]), set(tweet))

	def test_collect_empty_attribute_list(self):
		"""
		Test that collecting data with an empty attribute list returns everything.
		"""

		queue = Queue()
		listener = QueuedTweetListener(queue, max_time=2, attributes=[ ])
		stream = Stream(self.authenticate(), listener)
		stream.filter(track=[ 'is' ])

		tweets = queue.dequeue_all()
		self.assertTrue(tweets)
		for tweet in tweets:
			self.assertLessEqual(10, len(tweet))

	def test_collect_none_attribute(self):
		"""
		Test that collecting data with `None` as the attributes returns everything.
		"""

		queue = Queue()
		listener = QueuedTweetListener(queue, max_time=2, attributes=None)
		stream = Stream(self.authenticate(), listener)
		stream.filter(track=[ 'is' ])

		tweets = queue.dequeue_all()
		self.assertTrue(tweets)
		for tweet in tweets:
			self.assertLessEqual(10, len(tweet))

	def test_collect_time(self):
		"""
		Test that when collecting data, the time limit is respected.
		"""

		start = time.time()
		listener = QueuedTweetListener(Queue(), max_time=3, attributes=[ ])
		stream = Stream(self.authenticate(), listener)
		stream.filter(track=[ 'is' ])
		self.assertEqual(3, round(time.time() - start))
