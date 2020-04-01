"""
Test the functionality of the Zhao et al. consumer.
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
from queues.consumers import ZhaoConsumer

class TestZhaoConsumer(unittest.TestCase):
	"""
	Test the implementation of the Zhao et al. consumer.
	"""

	def async_test(f):
		def wrapper(*args, **kwargs):
			coro = asyncio.coroutine(f)
			future = coro(*args, **kwargs)
			loop = asyncio.get_event_loop()
			loop.run_until_complete(future)
		return wrapper

	def test_create_consumer(self):
		"""
		Test that when creating a consumer, all the parameters are saved correctly.
		"""

		queue = Queue()
		consumer = ZhaoConsumer(queue, 60, timestamp='time')
		self.assertEqual(queue, consumer.queue)
		self.assertEqual(60, consumer.periodicity)
		self.assertEqual('time', consumer.timestamp)

	def test_create_consumer_default_timestamp(self):
		"""
		Test that when creating a consumer, the default timestamp attribute is 'timestamp'.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		self.assertEqual('timestamp', consumer.timestamp)

	def test_create_consumer_store(self):
		"""
		Test that when creating a consumer, an empty nutrition store is created.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		self.assertEqual({ }, consumer.store.all())

	def test_to_documents_tweet(self):
		"""
		Test that when creating a document from a tweet, the tweet is saved as an attribute.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			tweet = json.loads(f.readline())
			document = consumer._to_documents([ tweet ])[0]
			self.assertEqual(tweet, document.attributes['tweet'])

	def test_to_documents_ellipsis(self):
		"""
		Test that when the text has an ellipsis, the full text is used.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
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

		consumer = ZhaoConsumer(Queue(), 60)
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

		consumer = ZhaoConsumer(Queue(), 60)
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

		consumer = ZhaoConsumer(Queue(), 60)
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

	def test_latest_timestamp_empty(self):
		"""
		Test that when getting the timestamp from an empty set, a ValueError is raised.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		self.assertRaises(ValueError, consumer._latest_timestamp, [ ])

	def test_latest_timestamp(self):
		"""
		Test getting the latest timestamp from a corpus of documents.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			self.assertEqual(documents[-1].attributes['timestamp'], consumer._latest_timestamp(documents))

	def test_latest_timestamp_reversed(self):
		"""
		Test that when getting the latest timestamp from a corpus of reversed documents, the actual latest timestamp is given.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)[::-1]
			self.assertEqual(documents[0].attributes['timestamp'], consumer._latest_timestamp(documents))

	def test_add_documents(self):
		"""
		Test adding documents to the historical data.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		self.assertEqual({ }, consumer.documents)

		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer._add_documents(documents)
			self.assertEqual(set(document.attributes['timestamp'] for document in documents), set(consumer.documents.keys()))

	def test_add_documents_empty(self):
		"""
		Test that when adding no documents to the historical data, it remains unchanged.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		self.assertEqual({ }, consumer.documents)

		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer._add_documents(documents)
			self.assertEqual(set(document.attributes['timestamp'] for document in documents), set(consumer.documents.keys()))
			consumer._add_documents([ ])
			self.assertEqual(set(document.attributes['timestamp'] for document in documents), set(consumer.documents.keys()))

	def test_add_documents_multiple(self):
		"""
		Test that when adding documents to the historical data, each timestamp can have multiple documents.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		self.assertEqual({ }, consumer.documents)

		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer._add_documents(documents)
			self.assertTrue(all( len(documents) > 1 for documents in consumer.documents.values() ))

	def test_create_checkpoint_empty(self):
		"""
		Test that when creating the first checkpoint, the nutrition is created from scratch.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				documents = consumer._to_documents([ tweet ])
				consumer._create_checkpoint(documents)
				self.assertEqual([ 1 ], list(consumer.store.all().values()))
				break

	def test_create_checkpoint_multiple_empty(self):
		"""
		Test that when creating the first checkpoint with multiple tweets, the nutrition is created from scratch.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()[:10]
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer._create_checkpoint(documents)
			self.assertEqual([ 10 ], list(consumer.store.all().values()))

	def test_create_checkpoint_increment(self):
		"""
		Test that when creating checkpoints, the nutrition increments.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()[:10]
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			for i, document in enumerate(documents):
				consumer._create_checkpoint([ document ])
				self.assertEqual([ i + 1 ], list(consumer.store.all().values()))

	def test_create_checkpoint_timestamp(self):
		"""
		Test that when creating checkpoints, the correct timestamp is recorded.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()[:10]
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			for i, document in enumerate(documents):
				consumer._create_checkpoint([ document ])
				self.assertEqual(i + 1, consumer.store.get(document.attributes['timestamp']))

	def test_create_checkpoint_range(self):
		"""
		Test that when creating checkpoints, the correct range of timestamps is created.
		"""

		consumer = ZhaoConsumer(Queue(), 60)
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer._create_checkpoint(documents)
			self.assertEqual(documents[0].attributes['timestamp'], min(consumer.store.all()))
			self.assertEqual(documents[-1].attributes['timestamp'], max(consumer.store.all()))
