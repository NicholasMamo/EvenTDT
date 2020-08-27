"""
Test the functionality of the FUEGO consumer.
"""

import asyncio
import copy
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
from tdt.algorithms import SlidingELD
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

	def test_init_damping_negative(self):
		"""
		Test that when the damping is negative, the class raises a ValueError.
		"""

		self.assertRaises(ValueError, FUEGOConsumer, Queue(), damping=-0.1)

	def test_init_damping(self):
		"""
		Test that when the damping is 0, the class accepts it.
		"""

		self.assertTrue(FUEGOConsumer(Queue(), damping=0))

	def test_init_damping(self):
		"""
		Test that when creating a consumer, the class saves the damping.
		"""

		consumer = FUEGOConsumer(Queue(), damping=2)
		self.assertEqual(2, consumer.damping)

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

	def test_init_tdt(self):
		"""
		Test that when creating a consumer, the class creates the TDT algorithm.
		"""

		consumer = FUEGOConsumer(Queue(), window_size=120, windows=5)
		self.assertTrue(consumer.tdt)
		self.assertEqual(SlidingELD, type(consumer.tdt))
		self.assertEqual(120, consumer.tdt.window_size)
		self.assertEqual(5, consumer.tdt.windows)

	def test_init_burst_end_less_than_minus_one(self):
		"""
		Test that when creating a consumer with a burst that is less than -1, the consumer raises a ValueError.
		"""

		self.assertRaises(ValueError, FUEGOConsumer, Queue(), burst_end=-1.1)

	def test_init_burst_end_minus_one(self):
		"""
		Test that when creating a consumer with a burst of -1, the consumer accepts it.
		"""

		consumer = FUEGOConsumer(Queue(), burst_end=-1)
		self.assertTrue(consumer)
		self.assertEqual(-1, consumer.burst_end)

	def test_init_burst_end_intermediate(self):
		"""
		Test that when creating a consumer with a normal burst value, the consumer accepts it.
		"""

		consumer = FUEGOConsumer(Queue(), burst_end=0)
		self.assertTrue(consumer)
		self.assertEqual(0, consumer.burst_end)

	def test_init_burst_end_one(self):
		"""
		Test that when creating a consumer with a burst of 1, the consumer accepts it.
		"""

		consumer = FUEGOConsumer(Queue(), burst_end=1)
		self.assertTrue(consumer)
		self.assertEqual(1, consumer.burst_end)

	def test_init_burst_end_greater_than_one(self):
		"""
		Test that when creating a consumer with a burst that is greater than 1, the consumer raises a ValueError.
		"""

		self.assertRaises(ValueError, FUEGOConsumer, Queue(), burst_end=1.1)

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

	def test_update_volume_all_documents(self):
		"""
		Test that the volume function counts all the documents properly.
		This is tested by setting the damping to 0.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		self.assertEqual({ }, consumer.volume.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer._update_volume(documents)
			self.assertEqual(len(lines), sum(consumer.volume.all().values()))

	def test_update_volume_all_documents_gradual(self):
		"""
		Test that the volume function counts all the documents properly even when adding them gradually.
		This is tested by setting the damping to 0.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		self.assertEqual({ }, consumer.volume.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			for document in documents:
				consumer._update_volume([ document ])
			self.assertEqual(len(lines), sum(consumer.volume.all().values()))

	def test_update_volume_all_timestamps(self):
		"""
		Test that the volume function includes all recorded timestamps.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		self.assertEqual({ }, consumer.volume.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			timestamps = set( document.attributes['timestamp'] for document in documents )
			consumer._update_volume(documents)
			self.assertEqual(timestamps, set(consumer.volume.all()))

	def test_update_volume_update(self):
		"""
		Test that when there is a volume value set for a timestamp, adding a new document at that timestamp increments the value.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		self.assertEqual({ }, consumer.volume.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			document = documents[0]
			timestamp = document.attributes['timestamp']
			consumer.volume.add(timestamp, 1)
			self.assertEqual(1, consumer.volume.get(timestamp))
			consumer._update_volume([ document ])
			self.assertEqual(2, consumer.volume.get(timestamp))

	def test_update_volume_update_timestamp_only(self):
		"""
		Test that when updating the volume at a certain timestamp, the other timestamps are not changed.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		self.assertEqual({ }, consumer.volume.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			document = documents[0]
			timestamp = document.attributes['timestamp']
			consumer.volume.add(timestamp + 1, 1)
			self.assertEqual(1, consumer.volume.get(timestamp + 1))
			consumer._update_volume([ document ])
			self.assertEqual(1, consumer.volume.get(timestamp + 1))
			self.assertEqual(1, consumer.volume.get(timestamp))

	def test_update_volume_with_damping(self):
		"""
		Test that when adding the volume, it is damped.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0.5)
		self.assertEqual({ }, consumer.volume.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer._update_volume(documents)
			self.assertGreater(len(lines), sum(consumer.volume.all().values()))

	def test_update_volume_damping_sum(self):
		"""
		Test that when adding the volume, the volume sum is equivalent to the damping sum.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0.5)
		self.assertEqual({ }, consumer.volume.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			damping = sum( consumer._damp(document) for document in documents )
			consumer._update_volume(documents)
			self.assertEqual(round(damping, 10), round(sum(consumer.volume.all().values()), 10)) # floating point error

	def test_update_volume_binning(self):
		"""
		Test that when adding the volume, it is binned correctly.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0.5)
		self.assertEqual({ }, consumer.volume.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			"""
			Calculate the damping for each bin.
			"""
			damping = { }
			for document in documents:
				timestamp = document.attributes['timestamp']
				damping[timestamp] = damping.get(timestamp, 0) + consumer._damp(document)

			"""
			Create the volume bins.
			"""
			for document in documents: # to have an extra test with gradual adding
				consumer._update_volume([ document ])

			"""
			Check that the bins are correct.
			"""
			self.assertEqual(damping.keys(), consumer.volume.all().keys())
			for timestamp in damping:
				self.assertEqual(damping[timestamp], consumer.volume.get(timestamp))

	def test_update_volume_does_not_change_nutrition(self):
		"""
		Test that when updating the volume, it does not change the nutrition.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		self.assertEqual({ }, consumer.volume.all())
		self.assertEqual({ }, consumer.nutrition.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer._update_volume(documents)
			self.assertEqual(len(lines), sum(consumer.volume.all().values()))
			self.assertEqual({ }, consumer.nutrition.all())

	def test_update_volume_damping_same_timestamps(self):
		"""
		Test that when updating the volume, damping only affects the values, not the keys (timestamps).
		"""

		c0, c1 = FUEGOConsumer(Queue(), damping=0), FUEGOConsumer(Queue(), damping=0.5)
		self.assertEqual({ }, c1.volume.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = c1._to_documents(tweets)
			c0._update_volume(documents)
			c1._update_volume(documents)
			self.assertEqual(c0.volume.all().keys(), c1.volume.all().keys())

	def test_update_volume_damping_lowers_values(self):
		"""
		Test that when updating volume, damping can bring down the value.
		"""

		trivial = True

		c0, c1 = FUEGOConsumer(Queue(), damping=0), FUEGOConsumer(Queue(), damping=0.5)
		self.assertEqual({ }, c1.volume.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = c1._to_documents(tweets)
			c0._update_volume(documents)
			c1._update_volume(documents)
			self.assertEqual(c0.volume.all().keys(), c1.volume.all().keys())
			for timestamp in c0.volume.all():
				self.assertLessEqual(c1.volume.get(timestamp), c0.volume.get(timestamp))
				if c1.volume.get(timestamp) < c0.volume.get(timestamp):
					trivial = False

		if trivial:
			logger.info("Trivial test")

	def test_update_nutrition_all_timestamps(self):
		"""
		Test that the nutrition function includes all recorded timestamps.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		self.assertEqual({ }, consumer.nutrition.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			timestamps = set( document.attributes['timestamp'] for document in documents )
			consumer._update_nutrition(documents)
			self.assertEqual(timestamps, set(consumer.nutrition.all()))

	def test_update_nutrition_does_not_change_volume(self):
		"""
		Test that when updating the nutrition, it does not change the volume.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		self.assertEqual({ }, consumer.volume.all())
		self.assertEqual({ }, consumer.nutrition.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			consumer._update_nutrition(documents)
			self.assertEqual({ }, consumer.volume.all())

	def test_update_nutrition_all_terms(self):
		"""
		Test that when updating the nutrition, it includes all terms in the correct timestamps.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		self.assertEqual({ }, consumer.nutrition.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			"""
			Get the set of terms and separate them for each timestamp.
			"""
			terms = { }
			for document in documents:
				timestamp = document.attributes['timestamp']
				terms[timestamp] = terms.get(timestamp, set()).union(set(document.dimensions))

			"""
			Create the nutrition bins.
			"""
			for document in documents: # to have an extra test with gradual adding
				consumer._update_nutrition([ document ])

			"""
			Check that the bins are correct.
			"""
			self.assertEqual(terms.keys(), consumer.nutrition.all().keys())
			for timestamp in terms:
				self.assertEqual(terms[timestamp], set(consumer.nutrition.get(timestamp).keys()))

	def test_update_nutrition_sum(self):
		"""
		Test that when updating the nutrition, the correct term nutritions are recorded.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		self.assertEqual({ }, consumer.nutrition.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			"""
			Get the set of terms and separate them for each timestamp.
			"""
			terms = { }
			for document in documents:
				timestamp = document.attributes['timestamp']
				terms[timestamp] = terms.get(timestamp, { })
				for dimension, magnitude in document.dimensions.items():
					terms[timestamp][dimension] = terms[timestamp].get(dimension, 0) + magnitude

			"""
			Create the nutrition bins.
			"""
			consumer._update_nutrition(documents)

			"""
			Check that the bins are correct.
			"""
			self.assertEqual(terms.keys(), consumer.nutrition.all().keys())
			for timestamp in terms:
				self.assertEqual(terms[timestamp], consumer.nutrition.get(timestamp))

	def test_update_nutrition_sum_gradual(self):
		"""
		Test that when updating the nutrition gradually, the correct term nutritions are recorded.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		self.assertEqual({ }, consumer.nutrition.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			"""
			Get the set of terms and separate them for each timestamp.
			"""
			terms = { }
			for document in documents:
				timestamp = document.attributes['timestamp']
				terms[timestamp] = terms.get(timestamp, { })
				for dimension, magnitude in document.dimensions.items():
					terms[timestamp][dimension] = terms[timestamp].get(dimension, 0) + magnitude

			"""
			Create the nutrition bins.
			"""
			for document in documents:
				consumer._update_nutrition([ document ])

			"""
			Check that the bins are correct.
			"""
			self.assertEqual(terms.keys(), consumer.nutrition.all().keys())
			for timestamp in terms:
				self.assertEqual(terms[timestamp], consumer.nutrition.get(timestamp))

	def test_update_nutrition_sum_damping(self):
		"""
		Test that when updating the nutrition, the term weights are dampened.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0.5)
		self.assertEqual({ }, consumer.nutrition.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			"""
			Get the set of terms and separate them for each timestamp.
			"""
			terms = { }
			for document in documents:
				timestamp = document.attributes['timestamp']
				terms[timestamp] = terms.get(timestamp, { })
				damping = consumer._damp(document)
				for dimension, magnitude in document.dimensions.items():
					terms[timestamp][dimension] = terms[timestamp].get(dimension, 0) + magnitude * damping

			"""
			Create the nutrition bins.
			"""
			for document in documents:
				consumer._update_nutrition([ document ])

			"""
			Check that the bins are correct.
			"""
			self.assertEqual(terms.keys(), consumer.nutrition.all().keys())
			for timestamp in terms:
				self.assertEqual(terms[timestamp], consumer.nutrition.get(timestamp))

	def test_update_nutrition_damping_same_terms(self):
		"""
		Test that when updating the nutrition, damping only affects the values, not the keys (terms).
		"""

		c0, c1 = FUEGOConsumer(Queue(), damping=0), FUEGOConsumer(Queue(), damping=0.5)
		self.assertEqual({ }, c1.nutrition.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = c1._to_documents(tweets)
			c0._update_nutrition(documents)
			c1._update_nutrition(documents)
			self.assertEqual(c0.nutrition.all().keys(), c1.nutrition.all().keys())
			for timestamp in c0.nutrition.all():
				self.assertEqual(c0.nutrition.get(timestamp).keys(), c1.nutrition.get(timestamp).keys())

	def test_update_nutrition_damping_lowers_values(self):
		"""
		Test that when updating nutrition, damping can bring down the value.
		"""

		trivial = True

		c0, c1 = FUEGOConsumer(Queue(), damping=0), FUEGOConsumer(Queue(), damping=0.5)
		self.assertEqual({ }, c1.nutrition.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = c1._to_documents(tweets)
			c0._update_nutrition(documents)
			c1._update_nutrition(documents)
			self.assertEqual(c0.nutrition.all().keys(), c1.nutrition.all().keys())
			for timestamp in c0.nutrition.all():
				self.assertEqual(c0.nutrition.get(timestamp).keys(), c1.nutrition.get(timestamp).keys())
				for term in c0.nutrition.get(timestamp):
					self.assertLessEqual(c1.nutrition.get(timestamp)[term], c0.nutrition.get(timestamp)[term])
					if c1.nutrition.get(timestamp)[term] < c0.nutrition.get(timestamp)[term]:
						trivial = False

		if trivial:
			logger.info("Trivial test")

	def test_update_nutrition_update(self):
		"""
		Test that when there is a nutrition value set for a timestamp, adding a new document at that timestamp increments the values of the terms.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		self.assertEqual({ }, consumer.nutrition.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			document = documents[0]
			timestamp = document.attributes['timestamp']

			"""
			Apply nutrition updating twice.
			"""
			consumer._update_nutrition(documents)
			nutrition = copy.deepcopy(consumer.nutrition.all())
			consumer._update_nutrition(documents)
			for timestamp in nutrition:
				for term in nutrition[timestamp]:
					self.assertEqual(round(nutrition[timestamp][term] * 2, 10),
									 round(consumer.nutrition.get(timestamp)[term], 10)) # floating point error

	def test_update_nutrition_update_timestamp_only(self):
		"""
		Test that when updating the nutrition at a certain timestamp, the other timestamps are not changed.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		self.assertEqual({ }, consumer.nutrition.all())

		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)
			document = documents[0]
			timestamp = document.attributes['timestamp']
			consumer.nutrition.add(timestamp + 1, { 'a': 1 })
			self.assertEqual({ 'a': 1 }, consumer.nutrition.get(timestamp + 1))
			consumer._update_nutrition([ document ])
			self.assertEqual({ 'a': 1 }, consumer.nutrition.get(timestamp + 1))
			self.assertEqual(document.dimensions, consumer.nutrition.get(timestamp))

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
		Test the damping factor of a retweet with a custom delay.
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
					document.attributes['tweet']['retweeted_status']['timestamp_ms'] = float(document.attributes['tweet']['timestamp_ms']) - 60 * 1000
					self.assertEqual(0.6065307, round(consumer._damp(document), 7))
					trivial = False
					break

		if trivial:
			logger.warning("Trivial test")

	def test_damp_zero(self):
		"""
		Test that when the damping is set to 0, all tweets have a damping factor of 1.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			for document in documents:
				self.assertEqual(1, consumer._damp(document))

	def test_damp_less_than_one_bounds(self):
		"""
		Test that when the damping is less than 1, the damping factor is always bound between 0 and 1.
		"""

		consumer = FUEGOConsumer(Queue(), damping=0.9)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			for document in documents:
				self.assertLessEqual(0, consumer._damp(document))
				self.assertGreaterEqual(1, consumer._damp(document))

	def test_damp_one_bounds(self):
		"""
		Test that when the damping is 1, the damping factor is always bound between 0 and 1.
		"""

		consumer = FUEGOConsumer(Queue(), damping=1)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			for document in documents:
				self.assertLessEqual(0, consumer._damp(document))
				self.assertGreaterEqual(1, consumer._damp(document))

	def test_damp_greater_than_one_bounds(self):
		"""
		Test that when the damping is greater than 1, the damping factor is always bound between 0 and 1.
		"""

		consumer = FUEGOConsumer(Queue(), damping=2)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			for document in documents:
				self.assertLessEqual(0, consumer._damp(document))
				self.assertGreaterEqual(1, consumer._damp(document))

	def test_damp_reduces_with_greater_damping(self):
		"""
		Test that when the damping is increased, the damping factor goes down.
		"""

		trivial = True

		c1, c2 = FUEGOConsumer(Queue(), damping=1), FUEGOConsumer(Queue(), damping=2)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = c1._to_documents(tweets)

			for document in documents:
				if 'retweeted_status' in document.attributes['tweet']:
					trivial = False
					self.assertGreaterEqual(c1._damp(document), c2._damp(document))

		if trivial:
			logger.warning("Trivial test")

	def test_damp_does_not_affect_normal_tweets(self):
		"""
		Test that damping does not affect the damping factor of tweets that are not retweets.
		"""

		trivial = True

		c1, c2 = FUEGOConsumer(Queue(), damping=1), FUEGOConsumer(Queue(), damping=2)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = c1._to_documents(tweets)

			for document in documents:
				if 'retweeted_status' not in document.attributes['tweet']:
					self.assertEqual(1, c1._damp(document))
					self.assertEqual(1, c2._damp(document))
					trivial = False

		if trivial:
			logger.warning("Trivial test")

	def test_damp_custom_example(self):
		"""
		Test the damping factor of a retweet with a custom delay and a custom damping value.
		"""

		trivial = True

		consumer = FUEGOConsumer(Queue(), damping=2)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = consumer._to_documents(tweets)

			for document in documents:
				if 'retweeted_status' in document.attributes['tweet']:
					# copy the timestamp of the retweet to the timestamp of the original tweet (doesn't work the other way round because timestamp_ms gets priority)
					# set the delay to one minute
					document.attributes['tweet']['retweeted_status']['timestamp_ms'] = float(document.attributes['tweet']['timestamp_ms']) - 60 * 1000
					self.assertEqual(0.1353353, round(consumer._damp(document), 7))
					trivial = False
					break

		if trivial:
			logger.warning("Trivial test")
