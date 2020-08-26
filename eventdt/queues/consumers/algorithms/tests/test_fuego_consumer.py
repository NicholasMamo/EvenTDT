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
import twitter
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

	def test_init_volume_store(self):
		"""
		Test that when creating a consumer, the class creates an empty volume nutrition store.
		"""

		consumer = FUEGOConsumer(Queue())
		self.assertTrue(consumer.volume)
		self.assertEqual({ }, consumer.volume.all())

	def test_init_nutrition_store(self):
		"""
		Test that when creating a consumer, the class creates an empty nutrition store.
		"""

		consumer = FUEGOConsumer(Queue())
		self.assertTrue(consumer.nutrition)
		self.assertEqual({ }, consumer.nutrition.all())

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

	def test_time_empty(self):
		"""
		Test that when trying to get the time from an empty list of documents, the function raises a ValueError.
		"""

		consumer = FUEGOConsumer(Queue())
		self.assertRaises(ValueError, consumer._time, [ ])

	def test_time_document(self):
		"""
		Test that when trying to get the time from one document, the function raises a ValueError.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-100.json'), 'r') as f:
			lines = [ f.readline() ]
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			self.assertRaises(ValueError, consumer._time, documents[0])

	def test_time_list_of_document(self):
		"""
		Test that when trying to get the time from a list of one document, the function returns its timestamp.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-100.json'), 'r') as f:
			lines = [ f.readline() ]
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			self.assertEqual(documents[0].attributes['timestamp'], consumer._time(documents))

	def test_time_list_of_documents(self):
		"""
		Test that when trying to get the time from a list of document, the function returns the most recent timestamp.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			self.assertEqual(documents[-1].attributes['timestamp'], consumer._time(documents))

	def test_time_mix_documents(self):
		"""
		Test that when trying to get the time from a mixed (unordered) list of document, the function returns the most recent timestamp.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			timestamp = documents[-1].attributes['timestamp']
			self.assertEqual(timestamp, consumer._time(documents[::-1]))

	def test_damp_lower_bound(self):
		"""
		Test that damping has a lower bound of 0.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			for document in documents:
				self.assertGreaterEqual(1, consumer._damp(document))

	def test_damp_upper_bound(self):
		"""
		Test that damping has an upper bound of 0.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			for document in documents:
				self.assertLessEqual(0, consumer._damp(document))

	def test_damp_normal_tweet(self):
		"""
		Test that the damping factor of a tweet that is not a retweet is 1.
		"""

		trivial = True

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			for document in documents:
				if not 'retweeted_status' in document.attributes['tweet']:
					self.assertEqual(1, consumer._damp(document))
					trivial = False

		if trivial:
			logger.warning("Trivial test")

	def test_damp_quoted_tweet(self):
		"""
		Test that the damping factor of a quoted tweet is 1.
		"""

		trivial = True

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			for document in documents:
				if 'quoted_status' in document.attributes['tweet'] and not 'retweeted_status' in document.attributes['tweet']:
					self.assertEqual(1, consumer._damp(document))
					trivial = False

		if trivial:
			logger.warning("Trivial test")

	def test_damp_immediate_retweet(self):
		"""
		Test that the damping factor of a retweet at the same time as the original tweet is 1.
		"""

		trivial = True

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			for document in documents:
				if 'retweeted_status' in document.attributes['tweet']:
					# copy the timestamp of the retweet to the timestamp of the original tweet (doesn't work the other way round because timestamp_ms gets priority)
					document.attributes['tweet']['retweeted_status']['timestamp_ms'] = document.attributes['tweet']['timestamp_ms']
					self.assertEqual(1, consumer._damp(document))
					trivial = False
					break

		if trivial:
			logger.warning("Trivial test")

	def test_damp_recency(self):
		"""
		Test that the damping factor of a recent retweet is higher than that of an older retweet.
		"""

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			tweets = { } # retweets where the keys are the delay in retweeting
			for document in documents:
				if 'retweeted_status' in document.attributes['tweet']:
					diff = twitter.extract_timestamp(document.attributes['tweet']) - twitter.extract_timestamp(document.attributes['tweet']['retweeted_status'])
					tweets[diff] = document

			trivial = True
			# sort the tweets in ascending order of difference
			tweets = sorted(tweets.items(), key=lambda tweet: tweet[0])
			tweets = [ tweet[1] for tweet in tweets ]
			self.assertTrue(len(tweets) > 2)
			for i in range(0, len(tweets) - 1):
				recent, older = consumer._damp(tweets[i]), consumer._damp(tweets[i + 1])
				self.assertGreaterEqual(recent, older)
				if recent > older:
					trivial = False

			if trivial:
				logger.warning("Trivial test")

	def test_damp_example(self):
		"""
		Test that the damping factor of a retweet with a custom delay.
		"""

		trivial = True

		consumer = FUEGOConsumer(Queue())
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			for document in documents:
				if 'retweeted_status' in document.attributes['tweet']:
					# copy the timestamp of the retweet to the timestamp of the original tweet (doesn't work the other way round because timestamp_ms gets priority)
					# set the delay to one minute
					document.attributes['tweet']['retweeted_status']['timestamp_ms'] = float(document.attributes['tweet']['timestamp_ms']) - 60
					self.assertEqual(round(0.6065307), round(consumer._damp(document), 7))
					trivial = False
					break

		if trivial:
			logger.warning("Trivial test")
