"""
Test the functionality of the FUEGO consumer.
"""

import asyncio
import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
	sys.path.append(path)

from logger import logger
from nlp.document import Document
from nlp.weighting import TF
from objects.exportable import Exportable
from queues import Queue
from queues.consumers.algorithms import FUEGOConsumer
from vsm import vector_math

logger.set_logging_level(logger.LogLevel.WARNING)

class TestFUEGOConsumer(unittest.TestCase):
	"""
	Test the implementation of the FUEGO consumer.
	"""

	def async_test(f):
		def wrapper(*args, **kwargs):
			coro = asyncio.coroutine(f)
			future = coro(*args, **kwargs)
			loop = asyncio.get_event_loop()
			loop.run_until_complete(future)
		return wrapper

	def test_init_name(self):
		"""
		Test that the ELD consumer passes on the name to the base class.
		"""

		name = 'Test Consumer'
		consumer = FUEGOConsumer(Queue(), name=name)
		self.assertEqual(name, str(consumer))

	def test_init_queue(self):
		"""
		Test that when creating a consumer, the class saves the queue.
		"""

		queue = Queue()
		consumer = FUEGOConsumer(queue)
		self.assertEqual(queue, consumer.queue)
		self.assertEqual(0, consumer.queue.length())

	def test_init_with_tokenizer(self):
		"""
		Test that when creating a consumer, the class creates a tokenizer.
		"""

		consumer = FUEGOConsumer(Queue())
		self.assertTrue(consumer.tokenizer)
		self.assertTrue(consumer.tokenizer.stopwords)
		self.assertTrue(consumer.tokenizer.stem)

	def test_init_scheme(self):
		"""
		Test that when creating a consumer, the class saves the scheme.
		"""

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'idf.json'), 'r') as f:
			data = json.loads(f.readline())
			scheme = Exportable.decode(data)['tfidf']
			consumer = FUEGOConsumer(Queue(), scheme=scheme)
			self.assertEqual(scheme, consumer.scheme)

	def test_init_default_scheme(self):
		"""
		Test that when creating a consumer without a scheme, the classes uses TF.
		"""

		consumer = FUEGOConsumer(Queue())
		self.assertTrue(consumer.scheme)
		self.assertEqual(TF, type(consumer.scheme))

	@async_test
	async def test_construct_idf_documents(self):
		"""
		Test that when constructing the IDF, it uses all documents.
		"""

		queue = Queue()
		consumer = FUEGOConsumer(queue)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			queue.enqueue(*tweets)
			consumer._started()
			scheme = await consumer._construct_idf(1)
			self.assertEqual(len(lines), scheme.global_scheme.documents)

	@async_test
	async def test_construct_idf_terms(self):
		"""
		Test that when constructing the IDF, the correct terms are registered.
		"""

		queue = Queue()
		consumer = FUEGOConsumer(queue)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			queue.enqueue(*tweets)
			consumer._started()
			scheme = await consumer._construct_idf(1)

			documents = consumer._to_documents(tweets)
			terms = set([ term for document in documents
							   for term in document.dimensions ])

			self.assertEqual(terms, set(scheme.global_scheme.idf))

	@async_test
	async def test_construct_idf_counts(self):
		"""
		Test that when constructing the IDF, the correct term counts are registered.
		"""

		queue = Queue()
		consumer = FUEGOConsumer(queue)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			queue.enqueue(*tweets)
			consumer._started()
			scheme = await consumer._construct_idf(1)

			documents = consumer._to_documents(tweets)
			terms = set([ term for document in documents
							   for term in document.dimensions ])

			for term in terms:
				count = len([ document for document in documents if term in document.dimensions ])
				self.assertEqual(count, scheme.global_scheme.idf[term])

	def test_filter_tweets_empty(self):
		"""
		Test that when filtering a list of empty tweets, another empty list is returned.
		"""

		consumer = FUEGOConsumer(Queue())
		self.assertEqual([ ], consumer._filter_tweets([ ]))

	def test_filter_tweets_english(self):
		"""
		Test that when filtering a list of tweets, only English tweets are returned.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
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

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
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

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
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

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
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

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
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

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
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

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
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

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			filtered = consumer._filter_tweets(tweets)
			self.assertTrue(all(tweet in tweets for tweet in filtered))

	def test_filter_tweets_document(self):
		"""
		Test that when filtering a list of documents, the function looks for the tweet in the attributes.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = [ Document('', attributes={ 'tweet': tweet }) for tweet in tweets ]

			tweets = consumer._filter_tweets(tweets)
			documents = consumer._filter_tweets(documents)
			self.assertEqual(len(tweets), len(documents))
			self.assertTrue(all( document.attributes['tweet'] in tweets for document in documents ))

	def test_to_documents_tweet(self):
		"""
		Test that when creating a document from a tweet, the tweet is saved as an attribute.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			tweet = json.loads(f.readline())
			document = consumer._to_documents([ tweet ])[0]
			self.assertEqual(tweet['id'], document.attributes['id'])

	def test_to_documents_ellipsis(self):
		"""
		Test that when the text has an ellipsis, the full text is used.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				if '…' in tweet['text']:
					document = consumer._to_documents([ tweet ])[0]
					self.assertFalse(document.text.endswith('…'))

	def test_to_documents_quoted(self):
		"""
		Test that when the tweet is a quote, the text is used, not the quoted tweet's text.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
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

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
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

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
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

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				document = consumer._to_documents([ tweet ])[0]
				self.assertTrue(round(vector_math.magnitude(document), 10) in [ 0, 1 ])

	def test_to_documents_documents(self):
		"""
		Test that when converting a list of documents to documents, they are retained.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			self.assertEqual(documents, consumer._to_documents(documents))

	def test_to_documents_documents_with_attributes(self):
		"""
		Test that when converting a list of documents to documents, their attributes are updated.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = [ Document('', attributes={ 'tweet': tweet}) for tweet in tweets ]
			documents = consumer._to_documents(tweets)
			self.assertTrue(all( 'timestamp' in document.attributes for document in documents ))

	def test_to_documents_with_scheme(self):
		"""
		Test that when converting a list of tweets to documents, the term-weighting scheme is used to create the documents.
		"""

		trivial = True

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'idf.json'), 'r') as f:
			data = json.loads(f.readline())
			scheme = Exportable.decode(data)['tfidf']
			consumer = FUEGOConsumer(Queue(), scheme=scheme)

		"""
		Check that when there are two tokens in the same document, and one of them is rarer than the other, it has a higher TF-IDF score.
		"""
		terms = [ 'chelsea', 'goal' ]
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = [ Document('', attributes={ 'tweet': tweet}) for tweet in tweets ]
			documents = consumer._to_documents(tweets)

			for document in documents:
				if all( term in document.dimensions for term in terms ):
					trivial = False
					self.assertGreater(document.dimensions[terms[0]], document.dimensions[terms[1]])

		if trivial:
			logger.warning("Trivial test")
