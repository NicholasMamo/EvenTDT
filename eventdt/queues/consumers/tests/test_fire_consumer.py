"""
Test the functionality of the FIRE consumer.
"""

import asyncio
import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
	sys.path.append(path)

from queues import Queue
from queues.consumers import FIREConsumer
from nlp.term_weighting import TF

class TestFIREConsumer(unittest.TestCase):
	"""
	Test the implementation of the FIRE consumer.
	"""

	def test_create_consumer(self):
		"""
		Test that when creating a consumer, all the parameters are saved correctly.
		"""

		queue = Queue()
		consumer = FIREConsumer(queue, 60, scheme=TF())
		self.assertEqual(queue, consumer.queue)
		self.assertEqual(60, consumer.periodicity)
		self.assertEqual(TF, type(consumer.scheme))

	def test_filter_tweets_empty(self):
		"""
		Test that when filtering a list of empty tweets, another empty list is returned.
		"""

		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		self.assertEqual([ ], consumer._filter_tweets([ ]))

	def test_filter_tweets_english(self):
		"""
		Test that when filtering a list of tweets, only English tweets are returned.
		"""

		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			count = len(tweets)
			tweets = consumer._filter_tweets(tweets)
			self.assertTrue(all(tweet['lang'] == 'en' for tweet in tweets))
			self.assertGreater(count, len(tweets))

	def test_filter_tweets_hashtags(self):
		"""
		Test that when filtering tweets, all returned tweets have no more than 2 hashtags.
		"""

		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			count = len(tweets)
			tweets = consumer._filter_tweets(tweets)
			self.assertTrue(all(len(tweet['entities']['hashtags']) <= 2 for tweet in tweets))
			self.assertGreater(count, len(tweets))

	def test_filter_tweets_no_favourites(self):
		"""
		Test that when filtering tweets, all returned tweets' authors have favourited at least one tweet.
		"""

		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			count = len(tweets)
			tweets = consumer._filter_tweets(tweets)
			self.assertTrue(all(tweet['user']['favourites_count'] > 0 for tweet in tweets))
			self.assertGreater(count, len(tweets))

	def test_filter_tweets_follower_ratio(self):
		"""
		Test that when filtering tweets, all users have at least one follower for every thousand tweets they've published.
		"""

		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			count = len(tweets)
			tweets = consumer._filter_tweets(tweets)
			self.assertTrue(all(tweet['user']['followers_count'] / tweet['user']['statuses_count'] >= 1./1000. for tweet in tweets))
			self.assertGreater(count, len(tweets))

	def test_filter_tweets_repeat(self):
		"""
		Test that when filtering tweets twice, the second time has no effect.
		"""

		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]

			"""
			The first time, the number of tweets should decrease.
			"""
			count = len(tweets)
			tweets = consumer._filter_tweets(tweets)
			self.assertGreater(count, len(tweets))

			"""
			The second time, the number of tweets should remain the same.
			"""
			count = len(tweets)
			tweets = consumer._filter_tweets(tweets)
			self.assertEqual(count, len(tweets))

	def test_filter_tweets_unchanged(self):
		"""
		Test that when filtering tweets, the tweet data does not change.
		"""

		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			filtered = consumer._filter_tweets(tweets)
			self.assertTrue(all(tweet in tweets for tweet in filtered))
