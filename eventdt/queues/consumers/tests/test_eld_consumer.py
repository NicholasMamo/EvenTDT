"""
Test the functionality of the ELD consumer.
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
from queues.consumers import ELDConsumer
from nlp.document import Document
from nlp.term_weighting import TF
from vsm import vector_math
from vsm.clustering import Cluster
import twitter

class TestELDConsumer(unittest.TestCase):
	"""
	Test the implementation of the ELD consumer.
	"""

	def test_create_consumer(self):
		"""
		Test that when creating a consumer, all the parameters are saved correctly.
		"""

		queue = Queue()
		consumer = ELDConsumer(queue, 60, TF())
		self.assertEqual(queue, consumer.queue)
		self.assertEqual(0, consumer.queue.length())
		self.assertEqual(60, consumer.time_window)
		self.assertEqual(TF, type(consumer.scheme))

	def test_create_consumer_buffer_empty(self):
		"""
		Test that when creating a consumer, an empty buffer is created.
		"""

		queue = Queue()
		consumer = ELDConsumer(queue, 60, TF())
		self.assertEqual(Queue, type(consumer.buffer))
		self.assertEqual(0, consumer.buffer.length())

	def test_filter_tweets_empty(self):
		"""
		Test that when filtering a list of empty tweets, another empty list is returned.
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
		self.assertEqual([ ], consumer._filter_tweets([ ]))

	def test_filter_tweets_english(self):
		"""
		Test that when filtering a list of tweets, only English tweets are returned.
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
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

		consumer = ELDConsumer(Queue(), 60, TF())
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

		consumer = ELDConsumer(Queue(), 60, TF())
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

		consumer = ELDConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			count = len(tweets)
			tweets = consumer._filter_tweets(tweets)
			self.assertTrue(all(tweet['user']['followers_count'] / tweet['user']['statuses_count'] >= 1./1000. for tweet in tweets))
			self.assertGreater(count, len(tweets))

	def test_filter_tweets_urls(self):
		"""
		Test that when filtering tweets, they can have no more than one URL.
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			count = len(tweets)
			tweets = consumer._filter_tweets(tweets)
			self.assertTrue(all(len(tweet['entities']['urls']) <= 1 for tweet in tweets))
			self.assertGreater(count, len(tweets))

	def test_filter_tweets_bio(self):
		"""
		Test that when filtering tweets, their authors must have a non-empty biography.
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			count = len(tweets)
			tweets = consumer._filter_tweets(tweets)
			self.assertTrue(all(tweet['user']['description'] for tweet in tweets))
			self.assertGreater(count, len(tweets))

	def test_filter_tweets_repeat(self):
		"""
		Test that when filtering tweets twice, the second time has no effect.
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
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

		consumer = ELDConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			filtered = consumer._filter_tweets(tweets)
			self.assertTrue(all(tweet in tweets for tweet in filtered))

	def test_to_documents_tweet(self):
		"""
		Test that when creating a document from a tweet, the tweet is saved as an attribute.
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			tweet = json.loads(f.readline())
			document = consumer._to_documents([ tweet ])[0]
			self.assertEqual(tweet, document.attributes['tweet'])

	def test_to_documents_ellipsis(self):
		"""
		Test that when the text has an ellipsis, the full text is used.
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
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

		consumer = ELDConsumer(Queue(), 60, TF())
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

		consumer = ELDConsumer(Queue(), 60, TF())
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

		consumer = ELDConsumer(Queue(), 60, TF())
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

	def test_to_documents_normalized(self):
		"""
		Test that the documents are returned normalized.
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				document = consumer._to_documents([ tweet ])[0]
				self.assertEqual(1, round(vector_math.magnitude(document), 10))

	def test_create_checkpoint_first(self):
		"""
		Test that when creating the first checkpoint, the nutrition is created from scratch.
		"""

		consumer = ELDConsumer(Queue(), 60, scheme=TF())
		self.assertEqual({ }, consumer.store.all())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			line = f.readline()
			tweet = json.loads(line)
			documents = consumer._to_documents([ tweet ])
			timestamp = twitter.extract_timestamp(tweet)
			consumer.buffer.enqueue(*documents)
			consumer._create_checkpoint(timestamp)
			self.assertTrue(consumer.store.get(timestamp))
			self.assertEqual(set(documents[0].dimensions), set(consumer.store.get(timestamp)))

	def test_create_checkpoint_empty(self):
		"""
		Test that when creating an empty checkpoint, it is still recorded.
		"""

		consumer = ELDConsumer(Queue(), 60, scheme=TF())
		self.assertEqual({ }, consumer.store.all())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			line = f.readline()
			tweet = json.loads(line)
			timestamp = twitter.extract_timestamp(tweet)
			consumer._create_checkpoint(timestamp)
			self.assertEqual({ }, consumer.store.get(timestamp))

	def test_create_checkpoint_timestamp(self):
		"""
		Test that when creating checkpoints, the correct timestamp is recorded.
		"""

		consumer = ELDConsumer(Queue(), 60, scheme=TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			line = f.readline()
			tweet = json.loads(line)
			documents = consumer._to_documents([ tweet ])
			timestamp = twitter.extract_timestamp(tweet)
			consumer.buffer.enqueue(*documents)
			consumer._create_checkpoint(timestamp)
			self.assertEqual([ timestamp ], list(consumer.store.all().keys()))

	def test_create_checkpoint_scale(self):
		"""
		Test that when creating checkpoints, they are rescaled correctly.
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			timestamp = twitter.extract_timestamp(tweets[-1])
			consumer.buffer.enqueue(*documents)
			consumer._create_checkpoint(timestamp)
			self.assertLessEqual(0, min(consumer.store.get(timestamp).values()))
			self.assertEqual(1, max(consumer.store.get(timestamp).values()))

	def test_create_checkpoint_filter_empty(self):
		"""
		Test that when creating a checkpoint with the timestamp before any published documents, it is empty.
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer.buffer.enqueue(*documents)
			timestamp = twitter.extract_timestamp(tweets[0])
			consumer._create_checkpoint(timestamp - 1)

	def test_create_checkpoint_filter_inclusive(self):
		"""
		Test that when creating a checkpoint, the timestamp filter is inclusive.
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer.buffer.enqueue(*documents)
			timestamp = twitter.extract_timestamp(tweets[0])
			consumer._create_checkpoint(timestamp)

			"""
			Work out which dimensions should be in the checkpoint.
			"""
			dimensions = [ dimension for document in documents
			 						 for dimension in document.dimensions
									 if document.attributes['timestamp'] <= timestamp ]
			self.assertEqual(set(dimensions), set(consumer.store.get(timestamp)))

	def test_create_checkpoint_removes_documents_from_buffer(self):
		"""
		Test that when creating a checkpoint, the documents are removed from the buffer..
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer.buffer.enqueue(*documents)
			timestamp = twitter.extract_timestamp(tweets[0])
			self.assertEqual(len(tweets), consumer.buffer.length())
			consumer._create_checkpoint(timestamp)
			self.assertEqual(len(tweets) - 100, consumer.buffer.length())

	def test_create_checkpoint_reorders_buffer(self):
		"""
		Test that when creating a checkpoint and the buffer has mixed-up documents, the buffer is re-ordered.
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer.buffer.enqueue(*documents[::-1])
			timestamp = twitter.extract_timestamp(tweets[0])
			consumer._create_checkpoint(timestamp)
			self.assertTrue(all(consumer.buffer.queue[i].attributes['timestamp'] <= consumer.buffer.queue[i + 1].attributes['timestamp'])
								for i in range(len(consumer.buffer.queue) - 1))

	def test_create_checkpoint_wrong_order(self):
		"""
		Test that when creating a checkpoint and the buffer has mixed-up documents, the correct documents are used.
		"""

		consumer = ELDConsumer(Queue(), 60, TF())
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer.buffer.enqueue(*documents[::-1])
			timestamp = twitter.extract_timestamp(tweets[0])
			consumer._create_checkpoint(timestamp)

			"""
			Work out which dimensions should be in the checkpoint.
			"""
			dimensions = [ dimension for document in documents
			 						 for dimension in document.dimensions
									 if document.attributes['timestamp'] <= timestamp ]
			self.assertEqual(set(dimensions), set(consumer.store.get(timestamp)))
