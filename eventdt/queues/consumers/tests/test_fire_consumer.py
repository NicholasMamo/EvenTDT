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
from nlp.document import Document
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

	def test_to_documents_tweet(self):
		"""
		Test that when creating a document from a tweet, the tweet is saved as an attribute.
		"""

		consumer = FIREConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			tweet = json.loads(f.readline())
			document = consumer._to_documents([ tweet ])[0]
			self.assertEqual(tweet, document.attributes['tweet'])

	def test_to_documents_ellipsis(self):
		"""
		Test that when the text has an ellipsis, the full text is used.
		"""

		consumer = FIREConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				if '…' in tweet['text']:
					document = consumer._to_documents([ tweet ])[0]

					"""
					Make an exception for a special case.
					"""
					if not ('retweeted_status' in tweet and tweet['retweeted_status']['id_str'] == '1238513167573147648'):
						self.assertFalse(document.text.endswith('…'))

	def test_to_documents_quoted(self):
		"""
		Test that when the tweet is a quote, the text is used, not the quoted tweet's text.
		"""

		consumer = FIREConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				if 'retweeted_status' in tweet:
					timestamp = tweet['timestamp_ms']
					tweet = tweet['retweeted_status']
					tweet['timestamp_ms'] = timestamp

				if 'quoted_status' in tweet:
					document = consumer._to_documents([ tweet ])[0]

					if 'extended_tweet' in tweet:
						self.assertEqual(tweet["extended_tweet"].get("full_text", tweet.get("text", "")), document.text)
					else:
						self.assertEqual(tweet.get('text'), document.text)

	def test_to_documents_retweeted(self):
		"""
		Test that when the tweet is a quote, the retweet's text is used.
		"""

		consumer = FIREConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				if 'retweeted_status' in tweet:
					document = consumer._to_documents([ tweet ])[0]

					retweet = tweet['retweeted_status']
					if 'extended_tweet' in retweet:
						self.assertEqual(retweet["extended_tweet"].get("full_text", retweet.get("text", "")), document.text)
					else:
						self.assertEqual(retweet.get('text'), document.text)

					"""
					Tweets shouldn't start with 'RT'.
					"""
					self.assertFalse(document.text.startswith('RT'))

	def test_to_documents_normal(self):
		"""
		Test that when the tweet is not a quote or retweet, the full text is used.
		"""

		consumer = FIREConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				if not 'retweeted_status' in tweet and not 'quoted_status' in tweet:
					document = consumer._to_documents([ tweet ])[0]

					if 'extended_tweet' in tweet:
						self.assertEqual(tweet["extended_tweet"].get("full_text", tweet.get("text", "")), document.text)
					else:
						self.assertEqual(tweet.get('text'), document.text)

					"""
					There should be no ellipsis in the text now.
					"""
					self.assertFalse(document.text.endswith('…'))

	def test_filter_documents_empty(self):
		"""
		Test that when filtering a list of empty documents, another empty list is returned.
		"""

		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		self.assertEqual([ ], consumer._filter_documents([ ]))

	def test_filter_documents_empty(self):
		"""
		Test that when filtering an empty document, an empty list is returned.
		"""

		document = Document('')
		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		self.assertEqual([ ], consumer._filter_documents([ document ]))

	def test_filter_documents_stopwords(self):
		"""
		Test that when filtering a document with only stopwords, an empty list is returned.
		"""

		document = Document('is the')
		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		self.assertEqual([ ], consumer._filter_documents([ document ]))

	def test_filter_documents_excludes_stopwords(self):
		"""
		Test that when filtering a document, stopwords are not considered in the calculation.
		"""

		document = Document('a cigar is not a pipe, and a table is not a chair')
		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		self.assertEqual([ document ], consumer._filter_documents([ document ]))

	def test_filter_documents_repetition(self):
		"""
		Test that when filtering documents that have repetition, they are rejected if their score is low.
		"""

		document = Document('a cigar is not a pipe, and a pipe is not a cigar')
		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		self.assertEqual([ ], consumer._filter_documents([ document ]))

	def test_filter_documents_repeat(self):
		"""
		Test that when filtering documents twice, the second time has no effect.
		"""

		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			"""
			The first time, the number of documents should decrease.
			"""
			count = len(documents)
			documents = consumer._filter_documents(documents)
			self.assertGreater(count, len(documents))

			"""
			The second time, the number of documents should remain the same.
			"""
			count = len(documents)
			documents = consumer._filter_documents(documents)
			self.assertEqual(count, len(documents))

	def test_filter_documents_unchanged(self):
		"""
		Test that when filtering documents, the document data does not change.
		"""

		consumer = FIREConsumer(Queue(), 60, scheme=TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			filtered = consumer._filter_documents(documents)
			self.assertTrue(all(document in documents for document in filtered))
