"""
Test the functionality of the FUEGO consumer.
"""

import asyncio
import copy
import json
import logging
import os
import re
import statistics
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from logger import logger
from nlp import Tokenizer
from nlp.document import Document
from nlp.weighting import TF
from objects.exportable import Exportable
from queues import Queue
from queues.consumers.algorithms import FUEGOConsumer
from queues.consumers.algorithms import DynamicThreshold, FilteringLevel, ReportingLevel, StorageLevel
from summarization import Summary
from summarization.algorithms import DGS
from summarization.timeline import Timeline
from summarization.timeline.nodes import TopicalClusterNode
from tdt.algorithms import SlidingELD
import twitter
from vsm import vector_math, Vector
from vsm.clustering import Cluster

logging.getLogger('asyncio').setLevel(logging.ERROR) # disable task length outputs
logger.set_logging_level(logger.LogLevel.WARNING)

class TestFUEGOConsumer(unittest.IsolatedAsyncioTestCase):
    """
    Test the implementation of the FUEGO consumer.
    """

    def test_init_name(self):
        """
        Test that the ELD consumer passes on the name to the base class.
        """

        name = 'Test Consumer'
        consumer = FUEGOConsumer(Queue(), name=name)
        self.assertEqual(name, str(consumer))

    def test_init_tracking(self):
        """
        Test that on initialization, the tracking variable is saved.
        """

        consumer = FUEGOConsumer(Queue(), tracking=90)
        self.assertEqual(90, consumer.tracking)

        consumer = FUEGOConsumer(Queue(), tracking=300)
        self.assertEqual(300, consumer.tracking)

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

    def test_init_correlations_store(self):
        """
        Test that when creating a consumer, the class creates an empty correlations store.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertTrue(consumer.correlations)
        self.assertEqual({ }, consumer.correlations.all())

    def test_init_with_tdt(self):
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

    def test_init_burst_start_less_than_minus_one(self):
        """
        Test that when creating a consumer with a burst that is less than -1, the consumer raises a ValueError.
        """

        self.assertRaises(ValueError, FUEGOConsumer, Queue(), burst_start=-1.1)

    def test_init_burst_start_minus_one(self):
        """
        Test that when creating a consumer with a burst of -1, the consumer accepts it.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=-1)
        self.assertTrue(consumer)
        self.assertEqual(-1, consumer.burst_start)

    def test_init_burst_start_intermediate(self):
        """
        Test that when creating a consumer with a normal burst value, the consumer accepts it.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=0)
        self.assertTrue(consumer)
        self.assertEqual(0, consumer.burst_start)

    def test_init_burst_start_one(self):
        """
        Test that when creating a consumer with a burst of 1, the consumer accepts it.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=1)
        self.assertTrue(consumer)
        self.assertEqual(1, consumer.burst_start)

    def test_init_burst_start_greater_than_one(self):
        """
        Test that when creating a consumer with a burst that is greater than 1, the consumer raises a ValueError.
        """

        self.assertRaises(ValueError, FUEGOConsumer, Queue(), burst_start=1.1)

    def test_init_min_volume(self):
        """
        Test that when creating a consumer, it saves the minimum volume.
        """

        consumer = FUEGOConsumer(Queue(), min_volume=0)
        self.assertEqual(0, consumer.min_volume)

    def test_init_default_threshold(self):
        """
        Test the default dynamic threshold when creating a consumer.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertEqual(DynamicThreshold.MEAN, consumer.threshold)

    def test_init_threshold(self):
        """
        Test setting the type of dynamic threshold when creating a consumer.
        """

        consumer = FUEGOConsumer(Queue(), threshold=DynamicThreshold.MOVING_MEAN)
        self.assertEqual(DynamicThreshold.MOVING_MEAN, consumer.threshold)

    def test_init_filtering(self):
        """
        Test setting the type of filtering level when creating a consumer.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.NONE)
        self.assertEqual(FilteringLevel.NONE, consumer.filtering)

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        self.assertEqual(FilteringLevel.LENIENT, consumer.filtering)

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        self.assertEqual(FilteringLevel.STRICT, consumer.filtering)

    def test_init_reporting(self):
        """
        Test setting the type of reporting level when creating a consumer.
        """

        consumer = FUEGOConsumer(Queue(), reporting=ReportingLevel.ALL)
        self.assertEqual(ReportingLevel.ALL, consumer.reporting)

        consumer = FUEGOConsumer(Queue(), reporting=ReportingLevel.ORIGINAL)
        self.assertEqual(ReportingLevel.ORIGINAL, consumer.reporting)

    def test_init_storage(self):
        """
        Test setting the type of storage level when creating a consumer.
        """

        consumer = FUEGOConsumer(Queue(), storage=StorageLevel.TWEET)
        self.assertEqual(StorageLevel.TWEET, consumer.storage)

        consumer = FUEGOConsumer(Queue(), storage=StorageLevel.ATTRIBUTES)
        self.assertEqual(StorageLevel.ATTRIBUTES, consumer.storage)

    def test_init_with_summarization(self):
        """
        Test that when creating a consumer, the class creates the summarization algorithm.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertTrue(consumer.summarization)
        self.assertEqual(DGS, type(consumer.summarization))

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

    async def test_run_returns(self):
        """
        Test that at the end, the FUEGO consumer returns the number of consumed, filtered and skipped tweets, and a timeline.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'idf.json'), 'r') as f:
            data = json.loads(f.readline())
            scheme = Exportable.decode(data)['tfidf']

        """
        Create an empty queue.
        Use it to create a consumer and set it running.
        """
        queue = Queue()
        consumer = FUEGOConsumer(queue, scheme=scheme)
        running = asyncio.ensure_future(consumer.run(max_inactivity=3))
        await asyncio.sleep(0.5)

        """
        Load all tweets into the queue.
        """
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            tweets = [ json.loads(line) for line in f ]
            queue.enqueue(*tweets)

        output = await running
        self.assertEqual(dict, type(output))
        self.assertEqual(3, len(output))
        self.assertEqual({ 'consumed', 'filtered', 'timeline' }, set(output.keys()))
        self.assertEqual(500, output['consumed'])
        self.assertTrue(output['filtered'])
        self.assertEqual(Timeline, type(output['timeline']))

    async def test_run_returns_consumed_greater_than_filtered(self):
        """
        Test that at the end, the number of filtered tweets is less than the number of consumed tweets.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'idf.json'), 'r') as f:
            data = json.loads(f.readline())
            scheme = Exportable.decode(data)['tfidf']

        """
        Create an empty queue.
        Use it to create a consumer and set it running.
        """
        queue = Queue()
        consumer = FUEGOConsumer(queue, scheme=scheme)
        running = asyncio.ensure_future(consumer.run(max_inactivity=3))
        await asyncio.sleep(0.5)

        """
        Load all tweets into the queue.
        """
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            tweets = [ json.loads(line) for line in f ]
            queue.enqueue(*tweets)

        output = await running
        self.assertEqual(dict, type(output))
        self.assertLess(output['filtered'], output['consumed'])

    async def test_run_timeline_with_tracking(self):
        """
        Test that the FUEGO consumer's timeline uses the tracking variable.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'idf.json'), 'r') as f:
            data = json.loads(f.readline())
            scheme = Exportable.decode(data)['tfidf']

        """
        Create an empty queue.
        Use it to create a consumer and set it running.
        """
        queue = Queue()
        consumer = FUEGOConsumer(queue, scheme=scheme, tracking=150)
        running = asyncio.ensure_future(consumer.run(max_inactivity=3))
        await asyncio.sleep(0.5)

        """
        Load all tweets into the queue.
        """
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            tweets = [ json.loads(line) for line in f ]
            queue.enqueue(*tweets)

        output = await running
        self.assertEqual(consumer.tracking, output['timeline'].expiry)

    def test_filter_tweets_empty(self):
        """
        Test that when filtering a list of empty tweets, another empty list is returned.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertEqual([ ], consumer._filter_tweets([ ]))

    def test_filter_tweets_none(self):
        """
        Test that when filtering a list of tweets without actually filtering, all tweets are accepted.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.NONE)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertEqual(tweets, filtered)

    def test_filter_tweets_strict_english(self):
        """
        Test that when filtering a list of tweets, only English tweets are returned.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all(twitter.lang(tweet) == 'en' for tweet in tweets))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_lenient_english(self):
        """
        Test that when filtering a list of tweets leniently, only English tweets are returned.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all(twitter.lang(tweet) == 'en' for tweet in tweets))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_strict_v2_english(self):
        """
        Test that when filtering a list of tweets, only English tweets are returned.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all(twitter.lang(tweet) == 'en' for tweet in tweets))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_lenient_v2_english(self):
        """
        Test that when filtering a list of tweets leniently, only English tweets are returned.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all(twitter.lang(tweet) == 'en' for tweet in tweets))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_strict_hashtags(self):
        """
        Test that when filtering tweets, all returned tweets have no more than 2 hashtags.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all(len(twitter.hashtags(tweet)) <= 2 for tweet in tweets))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_lenient_hashtags(self):
        """
        Test that when filtering tweets leniently, all returned tweets have no more than 2 hashtags.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all(len(twitter.hashtags(tweet)) <= 2 for tweet in tweets))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_strict_v2_hashtags(self):
        """
        Test that when filtering tweets, all returned tweets have no more than 2 hashtags.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all(len(twitter.hashtags(tweet)) <= 2 for tweet in tweets))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_lenient_v2_hashtags(self):
        """
        Test that when filtering tweets leniently, all returned tweets have no more than 2 hashtags.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all(len(twitter.hashtags(tweet)) <= 2 for tweet in tweets))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_strict_no_favourites(self):
        """
        Test that when filtering tweets, all returned tweets' authors have favourited at least one tweet.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all(tweet['user']['favourites_count'] > 0 for tweet in tweets))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_lenient_no_favourites(self):
        """
        Test that when filtering tweets leniently, all returned tweets' authors have favourited at least one tweet.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all(tweet['user']['favourites_count'] > 0 for tweet in tweets))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_strict_follower_ratio(self):
        """
        Test that when filtering tweets, all users have at least one follower for every thousand tweets they've published.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            for tweet in tweets:
                self.assertTrue((not twitter.is_retweet(tweet) and twitter.user_followers(tweet) / twitter.user_statuses(tweet) >= 1./1000.) or
                                 twitter.is_retweet(tweet) and twitter.user_followers(twitter.original(tweet))  / twitter.user_statuses(twitter.original(tweet)) >= 1./1000.)
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_lenient_follower_ratio(self):
        """
        Test that when filtering tweets leniently, all users have at least one follower for every thousand tweets they've published.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            for tweet in tweets:
                self.assertTrue((not twitter.is_retweet(tweet) and twitter.user_followers(tweet) / twitter.user_statuses(tweet) >= 1./1000.) or
                                 twitter.is_retweet(tweet) and twitter.user_followers(twitter.original(tweet))  / twitter.user_statuses(twitter.original(tweet)) >= 1./1000.)
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_strict_v2_follower_ratio(self):
        """
        Test that when filtering tweets, all users have at least one follower for every thousand tweets they've published.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            for tweet in tweets:
                self.assertTrue((not twitter.is_retweet(tweet) and twitter.user_followers(tweet) / twitter.user_statuses(tweet) >= 1./1000.) or
                                 twitter.is_retweet(tweet) and twitter.user_followers(tweet, twitter.original(tweet)['author_id'])  / twitter.user_statuses(tweet, twitter.original(tweet)['author_id']) >= 1./1000.)
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_lenient_v2_follower_ratio(self):
        """
        Test that when filtering tweets leniently, all users have at least one follower for every thousand tweets they've published.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            for tweet in tweets:
                self.assertTrue((not twitter.is_retweet(tweet) and twitter.user_followers(tweet) / twitter.user_statuses(tweet) >= 1./1000.) or
                                 twitter.is_retweet(tweet) and twitter.user_followers(tweet, twitter.original(tweet)['author_id'])  / twitter.user_statuses(tweet, twitter.original(tweet)['author_id']) >= 1./1000.)
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_strict_follower_ratio_no_statuses(self):
        """
        Test that when filtering tweets, all users have at least one status.
        It's possible that a user has no statuses, which is weird.
        Not sure how that happens, possibly a short delay in updating the user profile.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all( not twitter.is_retweet(tweet) and twitter.user_statuses(tweet) or
                                 twitter.is_retweet(tweet) and twitter.user_statuses(tweet)
                                 for tweet in tweets ))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_strict_v2_follower_ratio_no_statuses(self):
        """
        Test that when filtering tweets, all users have at least one status.
        It's possible that a user has no statuses, which is weird.
        Not sure how that happens, possibly a short delay in updating the user profile.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all( not twitter.is_retweet(tweet) and twitter.user_statuses(tweet) or
                                 twitter.is_retweet(tweet) and twitter.user_statuses(tweet, twitter.original(tweet)['author_id'])
                                 for tweet in tweets ))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_strict_urls(self):
        """
        Test that when filtering tweets, none of the retained ones have URLs in them.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertTrue(all( len(twitter.urls(tweet)) == 0 for tweet in filtered ))
            self.assertGreater(len(tweets), len(filtered))

    def test_filter_tweets_lenient_urls(self):
        """
        Test that when filtering tweets leniently, the retained ones may have URLs in them.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertGreater(len(tweets), len(filtered))
            self.assertTrue(any( len(twitter.urls(tweet)) > 0 for tweet in filtered ))

    def test_filter_tweets_strict_v2_urls(self):
        """
        Test that when filtering tweets, none of the retained ones have URLs in them.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertTrue(all( len(twitter.urls(tweet)) == 0 for tweet in filtered ))
            self.assertGreater(len(tweets), len(filtered))

    def test_filter_tweets_lenient_v2_urls(self):
        """
        Test that when filtering tweets leniently, the retained ones may have URLs in them.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertGreater(len(tweets), len(filtered))
            self.assertTrue(any( len(twitter.urls(tweet)) > 0 for tweet in filtered ))

    def test_filter_tweets_strict_removes_quotes(self):
        """
        Test that when filtering tweets, quotes are automatically filtered.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertFalse(any( twitter.is_quote(tweet) for tweet in filtered ))

    def test_filter_tweets_lenient_keeps_quotes(self):
        """
        Test that when filtering tweets leniently, quotes are retained.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertTrue(any( twitter.is_quote(tweet) for tweet in filtered ))

    def test_filter_tweets_strict_v2_removes_quotes(self):
        """
        Test that when filtering tweets, quotes are automatically filtered.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertFalse(any( twitter.is_quote(tweet) for tweet in filtered ))

    def test_filter_tweets_lenient_v2_keeps_quotes(self):
        """
        Test that when filtering tweets leniently, quotes are retained.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertTrue(any( twitter.is_quote(tweet) for tweet in filtered ))

    def test_filter_tweets_strict_urls_not_media(self):
        """
        Test that when filtering tweets, tweets with media are retained.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all( len(twitter.urls(tweet)) == 0 or
                                 len(twitter.urls(tweet)) == 1 and twitter.is_quote(tweet)
                                for tweet in tweets ))
            self.assertTrue(any('media' in tweet['entities'] and len(tweet['entities']['media']) for tweet in tweets))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_strict_v2_urls_not_media(self):
        """
        Test that when filtering tweets, tweets with media are retained.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(all( len(twitter.urls(tweet)) == 0 or
                                 len(twitter.urls(tweet)) == 1 and twitter.is_quote(tweet)
                                for tweet in tweets ))
            self.assertTrue(any('media' in tweet['includes'] and len(tweet['includes']['media']) for tweet in tweets))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_strict_bio(self):
        """
        Test that when filtering tweets, their authors must have a non-empty biography.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            for tweet in tweets:
                self.assertTrue(not twitter.is_retweet(tweet) and twitter.user_description(tweet) or
                                twitter.is_retweet(tweet) and twitter.user_description(twitter.original(tweet)))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_lenient_bio(self):
        """
        Test that when filtering tweets leniently, their authors must have a non-empty biography.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            for tweet in tweets:
                self.assertTrue(not twitter.is_retweet(tweet) and twitter.user_description(tweet) or
                                twitter.is_retweet(tweet) and twitter.user_description(twitter.original(tweet)))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_strict_v2_bio(self):
        """
        Test that when filtering tweets, their authors must have a non-empty biography.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            for tweet in tweets:
                self.assertTrue(not twitter.is_retweet(tweet) and twitter.user_description(tweet) or
                                twitter.is_retweet(tweet) and twitter.user_description(tweet, twitter.original(tweet)['author_id']))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_lenient_v2_bio(self):
        """
        Test that when filtering tweets leniently, their authors must have a non-empty biography.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            for tweet in tweets:
                self.assertTrue(not twitter.is_retweet(tweet) and twitter.user_description(tweet) or
                                twitter.is_retweet(tweet) and twitter.user_description(tweet, twitter.original(tweet)['author_id']))
            self.assertGreater(count, len(tweets))

    def test_filter_tweets_strict_repeat(self):
        """
        Test that when filtering tweets twice, the second time has no effect.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
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

    def test_filter_tweets_lenient_repeat(self):
        """
        Test that when filtering tweets leniently twice, the second time has no effect.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
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

    def test_filter_tweets_strict_repeat(self):
        """
        Test that when filtering tweets twice, the second time has no effect.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
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

    def test_filter_tweets_lenient_repeat(self):
        """
        Test that when filtering tweets leniently twice, the second time has no effect.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
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

    def test_filter_tweets_strict_unchanged(self):
        """
        Test that when filtering tweets, the tweet data does not change.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertTrue(all(tweet in tweets for tweet in filtered))

    def test_filter_tweets_lenient_unchanged(self):
        """
        Test that when filtering tweets leniently, the tweet data does not change.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertTrue(all(tweet in tweets for tweet in filtered))

    def test_filter_tweets_strict_v2_unchanged(self):
        """
        Test that when filtering tweets, the tweet data does not change.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertTrue(all(tweet in tweets for tweet in filtered))

    def test_filter_tweets_lenient_v2_unchanged(self):
        """
        Test that when filtering tweets leniently, the tweet data does not change.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertTrue(all(tweet in tweets for tweet in filtered))

    def test_filter_tweets_strict_document(self):
        """
        Test that when filtering a list of documents, the function looks for the tweet in the attributes.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = [ Document('', attributes={ 'tweet': tweet }) for tweet in tweets ]

            tweets = consumer._filter_tweets(tweets)
            documents = consumer._filter_tweets(documents)
            self.assertEqual(len(tweets), len(documents))
            self.assertTrue(all( document.tweet in tweets for document in documents ))

    def test_filter_tweets_lenient_document(self):
        """
        Test that when filtering a list of documents leniently, the function looks for the tweet in the attributes.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = [ Document('', attributes={ 'tweet': tweet }) for tweet in tweets ]

            tweets = consumer._filter_tweets(tweets)
            documents = consumer._filter_tweets(documents)
            self.assertEqual(len(tweets), len(documents))
            self.assertTrue(all( document.tweet in tweets for document in documents ))

    def test_filter_tweets_strict_v2_document(self):
        """
        Test that when filtering a list of documents, the function looks for the tweet in the attributes.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = [ Document('', attributes={ 'tweet': tweet }) for tweet in tweets ]

            tweets = consumer._filter_tweets(tweets)
            documents = consumer._filter_tweets(documents)
            self.assertEqual(len(tweets), len(documents))
            self.assertTrue(all( document.tweet in tweets for document in documents ))

    def test_filter_tweets_lenient_v2_document(self):
        """
        Test that when filtering a list of documents leniently, the function looks for the tweet in the attributes.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = [ Document('', attributes={ 'tweet': tweet }) for tweet in tweets ]

            tweets = consumer._filter_tweets(tweets)
            documents = consumer._filter_tweets(documents)
            self.assertEqual(len(tweets), len(documents))
            self.assertTrue(all( document.tweet in tweets for document in documents ))

    def test_filter_tweets_strict_retweets(self):
        """
        Test that if the tweet is a retweet, the original tweet is filtered, not the retweet.
        In other words, the validation of the retweet is the same as the validation of the original tweet.
        """

        trivial = True

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            for tweet in tweets:
                if twitter.is_retweet(tweet):
                    self.assertEqual(consumer._validate_tweet(twitter.original(tweet)), consumer._validate_tweet(tweet))
                    trivial = False

        if trivial:
            logger.warning("Trivial test")

    def test_filter_tweets_lenient_retweets(self):
        """
        Test that if the tweet is a retweet, the original tweet is filtered, not the retweet.
        In other words, the validation of the retweet is the same as the validation of the original tweet.
        """

        trivial = True

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            for tweet in tweets:
                if twitter.is_retweet(tweet):
                    self.assertEqual(consumer._validate_tweet(twitter.original(tweet)), consumer._validate_tweet(tweet))
                    trivial = False

        if trivial:
            logger.warning("Trivial test")

    def test_filter_tweets_strict_replies(self):
        """
        Test that if the tweet is a reply, it is filtered out in lenient filtering.
        """

        trivial = True

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            for tweet in tweets:
                if twitter.is_reply(tweet):
                    self.assertFalse(consumer._validate_tweet(tweet))
                    trivial = False

        if trivial:
            logger.warning("Trivial test")

    def test_filter_tweets_lenient_replies(self):
        """
        Test that if the tweet is a reply, it is filtered out in lenient filtering.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(not any( twitter.is_reply(tweet) for tweet in tweets ))

    def test_filter_tweets_strict_v2_replies(self):
        """
        Test that if the tweet is a reply, it is filtered out in lenient filtering.
        """

        trivial = True

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            for tweet in tweets:
                if twitter.is_reply(tweet):
                    self.assertFalse(consumer._validate_tweet(tweet))
                    trivial = False

        if trivial:
            logger.warning("Trivial test")

    def test_filter_tweets_v2_lenient_replies(self):
        """
        Test that if the tweet is a reply, it is filtered out in lenient filtering.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(not any( twitter.is_reply(tweet) for tweet in tweets ))

    def test_filter_tweets_strict_reply_retweet(self):
        """
        Test that if the tweet is a retweet of a reply, it is filtered out.
        """

        trivial = True

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            for tweet in tweets:
                if twitter.is_retweet(tweet) and twitter.is_reply(tweet):
                    self.assertFalse(consumer._validate_tweet(tweet))
                    trivial = False

        if trivial:
            logger.warning("Trivial test")

    def no_test_filter_tweets_lenient_reply_retweet(self):
        """
        Test that if the tweet is a retweet of a reply, it is not filtered out.
        Note: This test is disabled because every retweeted reply is filtered for other reasons.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(any( twitter.is_retweet(tweet) and twitter.is_reply(tweet) for tweet in tweets ))

    def test_filter_tweets_strict_v2_reply_retweet(self):
        """
        Test that if the tweet is a retweet of a reply, it is filtered out.
        """

        trivial = True

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.STRICT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            for tweet in tweets:
                if twitter.is_retweet(tweet) and twitter.is_reply(tweet):
                    self.assertFalse(consumer._validate_tweet(tweet))
                    trivial = False

        if trivial:
            logger.warning("Trivial test (test_filter_tweets_strict_v2_reply_retweet)")

    def test_filter_tweets_lenient_v2_reply_retweet(self):
        """
        Test that if the tweet is a retweet of a reply, it is filtered out in lenient filtering.
        """

        consumer = FUEGOConsumer(Queue(), filtering=FilteringLevel.LENIENT)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            count = len(tweets)
            tweets = consumer._filter_tweets(tweets)
            self.assertTrue(not any( twitter.is_retweet(tweet) and twitter.is_reply(tweet) for tweet in tweets ))

    def test_to_documents_storage_tweet(self):
        """
        Test that when creating a document from a tweet with the `TWEET` storage strategy, the tweet is saved as an attribute.
        """

        consumer = FUEGOConsumer(Queue(), storage=StorageLevel.TWEET)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            tweets = [ json.loads(tweet) for tweet in f ]
            documents = consumer._to_documents(tweets)
            self.assertTrue(all( tweet == document.tweet for tweet, document in zip(tweets, documents) ))

    def test_to_documents_storage_tweet_v2(self):
        """
        Test that when creating a document from a tweet with the `TWEET` storage strategy, the tweet is saved as an attribute.
        """

        consumer = FUEGOConsumer(Queue(), storage=StorageLevel.TWEET)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            tweets = [ json.loads(tweet) for tweet in f ]
            documents = consumer._to_documents(tweets)
            self.assertTrue(all( tweet == document.tweet for tweet, document in zip(tweets, documents) ))

    def test_to_documents_storage_attributes(self):
        """
        Test that when creating a document from a tweet with the `ATTRIBUTES` storage strategy, the tweet is saved as an attribute.
        """

        consumer = FUEGOConsumer(Queue(), storage=StorageLevel.ATTRIBUTES)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            tweets = [ json.loads(tweet) for tweet in f ]
            documents = consumer._to_documents(tweets)
            self.assertTrue(all( not document.tweet for document in documents ))

    def test_to_documents_storage_attributes_v2(self):
        """
        Test that when creating a document from a tweet with the `ATTRIBUTES` storage strategy, the tweet is saved as an attribute.
        """

        consumer = FUEGOConsumer(Queue(), storage=StorageLevel.ATTRIBUTES)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            tweets = [ json.loads(tweet) for tweet in f ]
            documents = consumer._to_documents(tweets)
            self.assertTrue(all( not document.tweet for document in documents ))

    def test_to_documents_id(self):
        """
        Test that when creating a document from a tweet, the tweet ID is saved as an attribute.
        """

        consumer = FUEGOConsumer(Queue())
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            tweets = [ json.loads(tweet) for tweet in f ]
            documents = consumer._to_documents(tweets)
            self.assertTrue(all( tweet['id_str'] == document.id for tweet, document in zip(tweets, documents) ))

    def test_to_documents_v2_id(self):
        """
        Test that when creating a document from a tweet, the tweet ID is saved as an attribute.
        """

        consumer = FUEGOConsumer(Queue())
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            tweets = [ json.loads(tweet) for tweet in f ]
            documents = consumer._to_documents(tweets)
            self.assertTrue(all( tweet['data']['id'] == document.id for tweet, document in zip(tweets, documents) ))

    def test_to_documents_split_dash(self):
        """
        Test that when creating a document from a tweet, dashes are split.
        """

        trivial = True

        term = ' kick-off'
        tokenized = [ 'kick' ] # off is a stopword

        consumer = FUEGOConsumer(Queue())
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for tweet in f:
                tweet = json.loads(tweet)
                text = twitter.full_text(tweet)
                if term in text.lower():
                    trivial = False
                    document = consumer._to_documents([ tweet ])[0]
                    for token in tokenized:
                        self.assertTrue(token in document.dimensions)

        if trivial:
            logger.warning("Trivial test")

    def test_to_documents_mentions_in_dimensions(self):
        """
        Test that when creating a document from a tweet, the expanded mentions are part of the dimensions.
        """

        consumer = FUEGOConsumer(Queue())
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'examples', '#ParmaMilan-hakan.json'), 'r') as f:
            tweet = json.loads(f.readline())
            document = consumer._to_documents([ tweet ])[0]
            self.assertTrue('Hakan' in document.text)
            self.assertTrue('hakan' in document.dimensions)
            self.assertTrue('Çalhanoğlu' in document.text)
            self.assertTrue('calhanoglu' in document.dimensions)

    def test_to_documents_expands_mentions(self):
        """
        Test that when converting a list of tweets to documents, mentions are expanded.
        """

        wrong_pattern = re.compile("@[0-9,\\s…]")
        no_space_pattern = re.compile("[^\\s]@")
        end_pattern = re.compile('@$')

        """
        Check that when there are two tokens in the same document, and one of them is rarer than the other, it has a higher TF-IDF score.
        """
        consumer = FUEGOConsumer(Queue())
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                text = twitter.full_text(tweet)
                document = consumer._to_documents([ tweet ])[0]

                """
                Allow for some manual validation.
                """
                not_accounts = [ 'real_realestsounds', 'nevilleiesta', 'naija927', 'naijafm92.7', 'manchesterunited', 'ManchesterUnited',
                                 'clintasena', 'Maksakal88', 'Aubamayeng7', 'JustWenginIt', 'marcosrojo5', 'btsportsfootball',
                                 'Nsibirwahall', 'YouTubeより', 'juniorpepaseed', 'Mezieblog', 'UtdAlamin', 'spurs_vincente' ]
                if '@' in document.text:
                    if '@@' in text or ' @ ' in text or '@&gt;' in text or any(account in text for account in not_accounts):
                        continue
                    if end_pattern.findall(text):
                        continue
                    if no_space_pattern.findall(text) or no_space_pattern.findall(document.text):
                        continue
                    if wrong_pattern.findall(text):
                        continue

                self.assertFalse('@' in document.text)

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
                        self.assertEqual(twitter.expand_mentions(tweet["extended_tweet"].get("full_text", tweet.get("text", "")), tweet),
                                         twitter.expand_mentions(document.text, tweet))
                    else:
                        self.assertEqual(twitter.expand_mentions(tweet.get('text'), tweet),
                                         twitter.expand_mentions(document.text, tweet))

    def test_to_documents_retweeted(self):
        """
        Test that when the tweet is a retweet, the retweet's text is used.
        """

        consumer = FUEGOConsumer(Queue())
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if 'retweeted_status' in tweet:
                    document = consumer._to_documents([ tweet ])[0]

                    retweet = tweet['retweeted_status']
                    if 'extended_tweet' in retweet:
                        self.assertEqual(twitter.expand_mentions(retweet["extended_tweet"].get("full_text", retweet.get("text", "")), tweet),
                                         twitter.expand_mentions(document.text, tweet))
                    else:
                        self.assertEqual(twitter.expand_mentions(retweet.get('text'), tweet),
                                         twitter.expand_mentions(document.text, tweet))

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
                        self.assertEqual(twitter.expand_mentions(tweet["extended_tweet"].get("full_text", tweet.get("text", "")), tweet),
                                         twitter.expand_mentions(document.text, tweet))
                    else:
                        self.assertEqual(twitter.expand_mentions(tweet.get('text'), tweet),
                                         twitter.expand_mentions(document.text, tweet))

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
        Test that when converting a list of documents to documents, they are re-created again.
        """

        self.tokenizer = Tokenizer()

        consumer = FUEGOConsumer(Queue())
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            self.assertFalse(documents == consumer._to_documents(documents))

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

    def test_update_cache_no_documents(self):
        """
        Test that when updating the cache without providing any documents, the same cache is returned.
        """

        consumer = FUEGOConsumer(Queue())

        cache = [ Document('ABC', attributes={ 'timestamp': 10 }),
                  Document('DEF', attributes={ 'timestamp': 10 }) ]
        _cache = consumer._update_cache([ ], cache, 10)
        self.assertEqual(set(cache), set(_cache))

    def test_update_cache_no_cache(self):
        """
        Test that when updating an empty cache, the new cache only has the new documents.
        """

        consumer = FUEGOConsumer(Queue())

        documents = [ Document('ABC', attributes={ 'timestamp': 10 }),
                      Document('DEF', attributes={ 'timestamp': 10 }) ]
        cache = consumer._update_cache(documents, [ ], 10)
        self.assertEqual(set(documents), set(cache))

    def test_update_cache_copy_by_reference(self):
        """
        Test that when updating the cache, the documents are added by reference, not copied.
        """

        consumer = FUEGOConsumer(Queue())

        documents = [ Document('ABC', attributes={ 'timestamp': 10 }),
                      Document('DEF', attributes={ 'timestamp': 10 }) ]
        cache = consumer._update_cache(documents, [ ], 10)
        self.assertTrue(all( document in documents for document in cache ))

    def test_update_cache_list_of_documents(self):
        """
        Test that updating cache returns a list of documents.
        """

        consumer = FUEGOConsumer(Queue())

        documents = [ Document('ABC', attributes={ 'timestamp': 10 }),
                      Document('DEF', attributes={ 'timestamp': 10 }) ]
        cache = consumer._update_cache(documents, [ ], 10)
        self.assertEqual(list, type(cache))
        self.assertTrue(all( Document is type(document) for document in cache ))

    def test_update_cache_copy(self):
        """
        Test that when updating the cache, the new cache is a copied list.
        """

        consumer = FUEGOConsumer(Queue())

        cache = [ Document('ABC', attributes={ 'timestamp': 10 }),
                  Document('DEF', attributes={ 'timestamp': 10 }) ]
        _cache = consumer._update_cache([ ], cache, 10)
        self.assertFalse(cache is _cache)
        self.assertTrue(all( document in _cache for document in cache ))
        self.assertTrue(all( document in cache for document in _cache ))

    def test_update_cache_remove_old(self):
        """
        Test that when updating the cache, old documents are removed.
        """

        consumer = FUEGOConsumer(Queue(), window_size=10)

        cache = [ Document('ABC', attributes={ 'timestamp': 10 }),
                  Document('DEF', attributes={ 'timestamp': 10 }) ]
        _cache = consumer._update_cache([ ], cache, 30)
        self.assertFalse(_cache)

    def test_update_cache_window_start_exclusive(self):
        """
        Test that the window start is exclusive when removing documents from the cache.
        """

        window_size, time = 10, 20
        consumer = FUEGOConsumer(Queue(), window_size=window_size)

        cache = [ Document('ABC', attributes={ 'timestamp': time - window_size - 1 }),
                  Document('DEF', attributes={ 'timestamp': time - window_size }),
                  Document('GHI', attributes={ 'timestamp': time - window_size + 1 }), ]
        _cache = consumer._update_cache([ ], cache, time)
        self.assertEqual(3, len(cache))
        self.assertEqual(1, len(_cache))
        self.assertTrue(all( document.attributes['timestamp'] > time - window_size for document in _cache ))

    def test_update_cache_remove_old_new_documents(self):
        """
        Test that when updating cache, the function also removes new documents that are old.
        """

        window_size, time = 10, 20
        consumer = FUEGOConsumer(Queue(), window_size=window_size)

        documents = [ Document('ABC', attributes={ 'timestamp': time - window_size - 1 }),
                      Document('DEF', attributes={ 'timestamp': time - window_size }),
                      Document('GHI', attributes={ 'timestamp': time - window_size + 1 }), ]
        cache = consumer._update_cache(documents, [ ], time)
        self.assertEqual(1, len(cache))
        self.assertTrue(all( document.attributes['timestamp'] > time - window_size for document in cache ))

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

    def test_update_correlations_all_timestamps(self):
        """
        Test that when updating the correlations, it includes all recorded timestamps.
        """

        consumer = FUEGOConsumer(Queue(), damping=0)
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            timestamps = set( document.attributes['timestamp'] for document in documents )
            consumer._update_correlations(documents)
            self.assertEqual(timestamps, set(consumer.correlations.all()))

    def test_update_correlations_all_terms(self):
        """
        Test that when updating the correlations, it includes all terms in the correct timestamps.
        """

        consumer = FUEGOConsumer(Queue(), damping=0)
        self.assertEqual({ }, consumer.correlations.all())

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
            Calculate the correlations.
            """
            for document in documents: # to have an extra test with gradual adding
                consumer._update_correlations([ document ])

            """
            Check that the bins are correct.
            """
            self.assertEqual(terms.keys(), consumer.correlations.all().keys())
            for timestamp in terms:
                self.assertEqual(terms[timestamp], set(consumer.correlations.get(timestamp).keys()))

    def test_update_correlations_sum(self):
        """
        Test that when updating the correlations, the correct term correlations are recorded.
        """

        consumer = FUEGOConsumer(Queue(), damping=0)
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

            """
            Calculate the correlations and separate them for each timestamp.
            """
            correlations = { }
            for document in documents:
                timestamp = document.attributes['timestamp']
                correlations[timestamp] = correlations.get(timestamp, { })
                for t0 in document.dimensions:
                    correlations[timestamp][t0] = correlations[timestamp].get(t0, { })
                    for t1 in document.dimensions:
                        if t0 == t1:
                            continue

                        correlations[timestamp][t0][t1] = correlations[timestamp][t0].get(t1, 0) + 1

            """
            Calculate the correlations.
            """
            consumer._update_correlations(documents)

            """
            Check that the correlations are correct.
            """
            self.assertEqual(correlations.keys(), consumer.correlations.all().keys())
            for timestamp in correlations:
                self.assertEqual(correlations[timestamp], consumer.correlations.get(timestamp))

    def test_update_correlations_sum_gradual(self):
        """
        Test that when updating the correlations gradually, the correct term correlations are recorded.
        """

        consumer = FUEGOConsumer(Queue(), damping=0)
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

            """
            Calculate the correlations and separate them for each timestamp.
            """
            correlations = { }
            for document in documents:
                timestamp = document.attributes['timestamp']
                correlations[timestamp] = correlations.get(timestamp, { })
                for t0 in document.dimensions:
                    correlations[timestamp][t0] = correlations[timestamp].get(t0, { })
                    for t1 in document.dimensions:
                        if t0 == t1:
                            continue

                        correlations[timestamp][t0][t1] = correlations[timestamp][t0].get(t1, 0) + 1

            """
            Calculate the correlations from the consumer.
            """
            for document in documents:
                consumer._update_correlations([ document ])

            """
            Check that the correlations are correct.
            """
            self.assertEqual(correlations.keys(), consumer.correlations.all().keys())
            for timestamp in correlations:
                self.assertEqual(correlations[timestamp], consumer.correlations.get(timestamp))

    def test_update_correlations_sum_no_damping(self):
        """
        Test that when updating the nutrition, the term weights are not dampened.
        """

        consumer = FUEGOConsumer(Queue(), damping=0.5)
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

            """
            Calculate the correlations.
            """
            consumer._update_correlations(documents)
            self.assertTrue(all( type(correlation) is int
                                 for timestamp in consumer.correlations.all()
                                 for term in consumer.correlations.get(timestamp)
                                 for correlation in consumer.correlations.get(timestamp)[term].values() ))
            self.assertTrue(all( correlation == int(correlation)
                                 for timestamp in consumer.correlations.all()
                                 for term in consumer.correlations.get(timestamp)
                                 for correlation in consumer.correlations.get(timestamp)[term].values() ))

    def test_update_correlations_update(self):
        """
        Test that when there is a correlation value set for a timestamp, adding a new document at that timestamp increments the values of the terms.
        """

        consumer = FUEGOConsumer(Queue(), damping=0)
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

            """
            Apply nutrition updating twice.
            """
            consumer._update_correlations(documents)
            correlations = copy.deepcopy(consumer.correlations.all())
            consumer._update_correlations(documents)
            for timestamp in correlations:
                self.assertTrue(all(round(correlations[timestamp][t0][t1] * 2, 10) == round(consumer.correlations.get(timestamp)[t0][t1], 10) # account for floating point error
                                    for t0 in correlations[timestamp]
                                    for t1 in correlations[timestamp][t0]))

    def test_update_correlations_update_timestamp_only(self):
        """
        Test that when updating the correlations at a certain timestamp, the other timestamps are not changed.
        """

        consumer = FUEGOConsumer(Queue(), damping=0)
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            document = documents[0]
            timestamp = document.attributes['timestamp']
            consumer.correlations.add(timestamp + 1, { 'a': 1 })
            self.assertEqual({ 'a': 1 }, consumer.correlations.get(timestamp + 1))
            consumer._update_correlations([ document ])
            self.assertEqual({ 'a': 1 }, consumer.correlations.get(timestamp + 1))

    def test_update_correlations_no_self_correlations(self):
        """
        Test that when updating correlations, the function excludes self-correlations.
        """

        consumer = FUEGOConsumer(Queue(), damping=0.5)
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            consumer._update_correlations(documents)
            self.assertTrue(consumer.correlations) # check that the correlations store is not empty
            self.assertTrue(all( term not in consumer.correlations.get(timestamp).get(term, { })
                                 for timestamp in consumer.correlations.all()
                                 for term in consumer.correlations.get(timestamp) ))

    def test_update_correlations_symmetric(self):
        """
        Test that the correlations are symmetric.
        """

        consumer = FUEGOConsumer(Queue(), damping=0.5)
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            consumer._update_correlations(documents)
            self.assertTrue(consumer.correlations) # check that the correlations store is not empty
            self.assertTrue(all( consumer.correlations.get(timestamp).get(t0, { }).get(t1, 0) == consumer.correlations.get(timestamp).get(t1, { }).get(t0, 0)
                                 for timestamp in consumer.correlations.all()
                                 for t0 in consumer.correlations.get(timestamp)
                                 for t1 in consumer.correlations.get(timestamp) ))

    def test_update_correlations_no_zeroes(self):
        """
        Test that no correlation values can be zeroes.
        If the correlation is zero, the function automatically skips it.
        Therefore a correlation of zero indicates some other problem.
        """

        consumer = FUEGOConsumer(Queue(), damping=0.5)
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            consumer._update_correlations(documents)
            self.assertTrue(consumer.correlations) # check that the correlations store is not empty
            self.assertTrue(all( consumer.correlations.get(timestamp)[t0][t1] > 0
                                 for timestamp in consumer.correlations.all()
                                 for t0 in consumer.correlations.get(timestamp)
                                 for t1 in consumer.correlations.get(timestamp)[t0] ))

    def test_update_correlations_not_trivial(self):
        """
        Test that not all correlations are 1, which could indicate overwriting existing values.
        """

        consumer = FUEGOConsumer(Queue(), damping=0.5)
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            consumer._update_correlations(documents)
            self.assertTrue(consumer.correlations) # check that the correlations store is not empty
            self.assertTrue(any( consumer.correlations.get(timestamp)[t0][t1] > 1
                                 for timestamp in consumer.correlations.all()
                                 for t0 in consumer.correlations.get(timestamp)
                                 for t1 in consumer.correlations.get(timestamp)[t0] ))

    def test_combine_correlations_empy(self):
        """
        Test that when combining correlations, an empty dictionary is returned if there are no correlations.
        """

    def test_combine_correlations_dict(self):
        """
        Test that when combining correlations, the return value is a dictionary of terms.
        """

        consumer = FUEGOConsumer(Queue(), damping=0)
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            timestamp = documents[-1].attributes['timestamp']
            consumer._update_correlations(documents)
            self.assertEqual(dict, type(consumer._combine_correlations(timestamp)))

    def test_combine_correlations_dict_of_dict(self):
        """
        Test that when combining correlations, the return value is a dictionary of terms, and each term is associated with another dictionary.
        """

        consumer = FUEGOConsumer(Queue(), damping=0)
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            timestamp = documents[-1].attributes['timestamp']
            consumer._update_correlations(documents)
            correlations = consumer._combine_correlations(timestamp)
            self.assertTrue(all( dict == type(correlations[term]) for term in correlations ))

    def test_combine_correlations_start_exclusive(self):
        """
        Test that when combining correlations, the start of the correlations time window is exclusive.
        """

        consumer = FUEGOConsumer(Queue(), window_size=60)
        self.assertEqual({ }, consumer.correlations.all())
        documents = [ Document('', dimensions={ 'a': 10, 'b': 10 }, attributes={ 'timestamp': 10 }),
                      Document('', dimensions={ 'a': 20, 'b': 20 }, attributes={ 'timestamp': 70 }) ]
        consumer._update_correlations(documents)
        correlations = consumer._combine_correlations(70)
        self.assertEqual({ 'a': { 'b': 1 }, 'b': { 'a': 1 } }, correlations)

    def test_combine_correlations_end_inclusive(self):
        """
        Test that when combining correlations, the end of the correlations time window is inclusive.
        """

        consumer = FUEGOConsumer(Queue(), window_size=60)
        self.assertEqual({ }, consumer.correlations.all())
        documents = [ Document('', dimensions={ 'a': 10, 'b': 10 }, attributes={ 'timestamp': 10 }),
                      Document('', dimensions={ 'a': 20, 'b': 20 }, attributes={ 'timestamp': 70 }) ]
        consumer._update_correlations(documents)
        correlations = consumer._combine_correlations(70)
        self.assertEqual({ 'a': { 'b': 1 }, 'b': { 'a': 1 } }, correlations)

    def test_combine_correlations_all_terms(self):
        """
        Test that when combining correlations, the combined dictionary includes all terms.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            timestamp = documents[-1].attributes['timestamp']
            consumer._update_correlations(documents)

            # extract all terms in the past time window
            correlations = consumer.correlations.between(timestamp - consumer.tdt.window_size + 1, timestamp + 1)
            terms = set([ term for timestamp in correlations for term in correlations[timestamp] ])

            # compare the two sets of terms
            correlations = consumer._combine_correlations(timestamp)
            self.assertEqual(terms, set(correlations))

    def test_combine_correlations_add(self):
        """
        Test that when combining correlations, the function adds the scores at each timestamp.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            timestamp = documents[-1].attributes['timestamp']

            # calculate the correlations from the latest time window
            recent = [ document for document in documents if document.attributes['timestamp'] > timestamp - consumer.tdt.window_size ]
            _correlations = { }
            for document in recent:
                for t0 in document.dimensions:
                    _correlations[t0] = _correlations.get(t0, { })
                    for t1 in document.dimensions:
                        if t0 == t1:
                            continue

                        _correlations[t0][t1] = _correlations[t0].get(t1, 0) + 1

            consumer._update_correlations(documents)
            correlations = consumer._combine_correlations(timestamp)
            self.assertEqual(_correlations, correlations)

    def test_combine_correlations_normalized_upper_bound(self):
        """
        Test that when combining correlations and normalizing, the upper bound of correlations for each term is 1.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            timestamp = documents[-1].attributes['timestamp']
            consumer._update_correlations(documents)
            correlations = consumer._combine_correlations(timestamp, normalize=True)
            self.assertTrue(all( max(correlations[term].values()) <= 1 for term in correlations ))

    def test_combine_correlations_normalized_lower_bound(self):
        """
        Test that when combining correlations and normalizing, the lower bound of correlations for each term is 0.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            timestamp = documents[-1].attributes['timestamp']
            consumer._update_correlations(documents)
            correlations = consumer._combine_correlations(timestamp, normalize=True)
            self.assertTrue(all( 0 <= min(correlations[term].values()) for term in correlations ))

    def test_combine_correlations_normalized_sum(self):
        """
        Test that when combining correlations and normalizing, the sum of correlations for each term is 1.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            timestamp = documents[-1].attributes['timestamp']
            consumer._update_correlations(documents)
            correlations = consumer._combine_correlations(timestamp, normalize=True)
            self.assertTrue(all( 1 == round(sum(correlations[term].values()), 10)
                                 for term in correlations ))

    def test_combine_correlations_same_terms(self):
        """
        Test that when combining correlations and normalizing, all the same terms are retained.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            timestamp = documents[-1].attributes['timestamp']
            consumer._update_correlations(documents)
            original = consumer._combine_correlations(timestamp, normalize=False)
            normalized = consumer._combine_correlations(timestamp, normalize=True)
            self.assertEqual(set(original), set(normalized))
            self.assertTrue(all( set(original[term]) == set(normalized[term]) for term in original ))

    def test_combine_correlations_same_order(self):
        """
        Test that when combining correlations and normalizing, the highest correlations remain the highest, and vice-versa.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertEqual({ }, consumer.correlations.all())

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            timestamp = documents[-1].attributes['timestamp']
            consumer._update_correlations(documents)
            original = consumer._combine_correlations(timestamp, normalize=False)
            normalized = consumer._combine_correlations(timestamp, normalize=True)

            self.assertTrue(all( sorted(original[term], key=original[term].get) == sorted(normalized[term], key=normalized[term].get)
                                 for term in original ))

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
                if document.is_retweet:
                    # copy the timestamp of the retweet to the timestamp of the original tweet (doesn't work the other way round because timestamp_ms gets priority)
                    document.published = document.timestamp
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
                if twitter.is_retweet(document.tweet):
                    diff = twitter.extract_timestamp(document.tweet) - twitter.extract_timestamp(twitter.original(document.tweet))
                    tweets[diff] = document

            trivial = True
            # sort the tweets in ascending order of time difference (the delay until the retweet)
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

    def test_damp_v2_recency(self):
        """
        Test that the damping factor of a recent retweet is higher than that of an older retweet.
        """

        consumer = FUEGOConsumer(Queue())
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

            tweets = { } # retweets where the keys are the delay in retweeting
            for document in documents:
                if twitter.is_retweet(document.tweet):
                    diff = twitter.extract_timestamp(document.tweet) - twitter.extract_timestamp(twitter.original(document.tweet))
                    tweets[diff] = document

            trivial = True
            # sort the tweets in ascending order of time difference (the delay until the retweet)
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

    def test_damp_recency_attributes(self):
        """
        Test that damping works even when the `ATTRIBUTES` storage strategy is used.
        """

        consumer = FUEGOConsumer(Queue(), storage=StorageLevel.ATTRIBUTES)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

            tweets = { } # retweets where the keys are the delay in retweeting
            for document in documents:
                if document.is_retweet:
                    diff = document.timestamp - document.published
                    tweets[diff] = document

            trivial = True
            # sort the tweets in ascending order of time difference (the delay until the retweet)
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

    def test_damp_v2_recency_attributes(self):
        """
        Test that damping works even when the `ATTRIBUTES` storage strategy is used.
        """

        consumer = FUEGOConsumer(Queue(), storage=StorageLevel.ATTRIBUTES)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

            tweets = { } # retweets where the keys are the delay in retweeting
            for document in documents:
                if document.is_retweet:
                    diff = document.timestamp - document.published
                    tweets[diff] = document

            trivial = True
            # sort the tweets in ascending order of time difference (the delay until the retweet)
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
                if document.is_retweet:
                    # copy the timestamp of the retweet to the timestamp of the original tweet (doesn't work the other way round because timestamp_ms gets priority)
                    # set the delay to one minute
                    document.published = float(document.timestamp) - 60
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
                if document.is_retweet:
                    # copy the timestamp of the retweet to the timestamp of the original tweet (doesn't work the other way round because timestamp_ms gets priority)
                    # set the delay to one minute
                    document.published = float(document.timestamp) - 60
                    self.assertEqual(0.1353353, round(consumer._damp(document), 7))
                    trivial = False
                    break

        if trivial:
            logger.warning("Trivial test")

    def test_track_list_of_str(self):
        """
        Test that when tracking, the function returns a list of strings.
        """

        consumer = FUEGOConsumer(Queue(), burst_end=0, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 10, 'b': 2, 'c': 3 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 10, 'c': 0 })
        tracked = consumer._track([ 'a', 'b', 'c' ], 10)
        self.assertEqual(dict, type(tracked))
        self.assertTrue(tracked)
        self.assertEqual(set([ 'a', 'c' ]), set(tracked.keys()))
        self.assertTrue(all( str == type(term) for term in tracked ))

    def test_track_burst_end(self):
        """
        Test that when tracking, the function returns terms that have a burst higher than the burst end.
        """

        consumer = FUEGOConsumer(Queue(), burst_end=0, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        tracked = consumer._track([ 'a', 'b', 'c' ], 10)
        self.assertEqual(set([ 'a', 'c' ]), set(tracked))

        """
        Increase the burst end value.
        """

        consumer = FUEGOConsumer(Queue(), burst_end=0.5, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        tracked = consumer._track([ 'a', 'b', 'c' ], 10)
        self.assertEqual(set([ 'a' ]), set(tracked))

    def test_track_burst_end_negative(self):
        """
        Test that when tracking, the function returns terms that have a burst higher than the burst end even when it is negative.
        """

        consumer = FUEGOConsumer(Queue(), burst_end=-0.5, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        tracked = consumer._track([ 'a', 'b', 'c' ], 10)
        self.assertEqual(set([ 'a', 'c' ]), set(tracked))

        """
        Decrease the burst end value.
        """
        consumer = FUEGOConsumer(Queue(), burst_end=-0.7, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5, 'd': 0 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 0.6, 'c': 0, 'd': 1 })
        tracked = consumer._track([ 'a', 'b', 'c' ], 10)
        self.assertEqual(set([ 'a', 'b', 'c' ]), set(tracked))

    def test_track_burst_end_exclusive(self):
        """
        Test that when tracking, the function returns terms that have a burst higher than the burst end and this value is exclusive.
        """

        consumer = FUEGOConsumer(Queue(), burst_end=-0.5, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        tracked = consumer._track([ 'a', 'b', 'c' ], 10)
        self.assertEqual(set([ 'a', 'c' ]), set(tracked))

        """
        Decrease the burst end value.
        """
        consumer = FUEGOConsumer(Queue(), burst_end=-0.6, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5, 'd': 0 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 0.6, 'c': 0, 'd': 1 })
        tracked = consumer._track([ 'a', 'b', 'c' ], 10)
        self.assertEqual(set([ 'a', 'c' ]), set(tracked))

        """
        Decrease the burst end value further.
        """
        consumer = FUEGOConsumer(Queue(), burst_end=-0.61, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5, 'd': 0 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 0.6, 'c': 0, 'd': 1 })
        tracked = consumer._track([ 'a', 'b', 'c' ], 10)
        self.assertEqual(set([ 'a', 'b', 'c' ]), set(tracked))

    def test_track_only_tracked_terms(self):
        """
        Test that when tracking, the function returns only bursty terms that are being tracked.
        """

        consumer = FUEGOConsumer(Queue(), burst_end=0, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        tracked = consumer._track([ 'a', 'b', 'c' ], 10)
        self.assertEqual(set([ 'a', 'c' ]), set(tracked))

        """
        Remove 'c' from the tracked terms.
        """
        tracked = consumer._track([ 'a', 'b' ], 10)
        self.assertEqual(set([ 'a' ]), set(tracked))

    def test_track_no_duplicates(self):
        """
        Test that when tracking, the function does not return duplicate terms.
        """

        consumer = FUEGOConsumer(Queue(), burst_end=0, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        tracked = consumer._track([ 'a', 'b', 'c' ], 10)
        self.assertEqual(sorted(list(set(tracked))), sorted(tracked))

    def test_track_correct_windows(self):
        """
        Test that when tracking, the function uses the correct time windows.
        """

        consumer = FUEGOConsumer(Queue(), burst_end=0.3, window_size=5, windows=2)
        consumer.nutrition.add(15, { 'a': 1, 'b': 1, 'c': 0.5 })
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        tracked = consumer._track([ 'a', 'b', 'c' ], 10)
        self.assertEqual(set([ 'a', 'c' ]), set(tracked))
        tracked = consumer._track([ 'a', 'b', 'c' ], 15)
        self.assertEqual(set([ 'b' ]), set(tracked))

    def test_track_timestamp_inclusive(self):
        """
        Test that when tracking, the function includes the nutrition values at the given timestamp.
        """

        consumer = FUEGOConsumer(Queue(), burst_end=0.3, window_size=5, windows=2)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        tracked = consumer._track([ 'a', 'b', 'c' ], 9)
        self.assertEqual(set(), set(tracked))
        tracked = consumer._track([ 'a', 'b', 'c' ], 10)
        self.assertEqual(set([ 'a', 'c' ]), set(tracked))

    def test_track_uses_burst_start(self):
        """
        Test that when tracking bursty terms, the function uses burst end, not burst start.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=0.3, burst_end=0.5, window_size=5, windows=2)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        tracked = consumer._track([ 'a', 'b', 'c' ], 10)
        self.assertEqual(set([ 'a' ]), set(tracked))

    def test_filter_topics_empty_topics(self):
        """
        Test that when filtering topics and there are no topics, another empty dictionary is returned.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertEqual({ }, consumer._filter_topics({ }, [ ]))

    def test_filter_topics_empty_tracking(self):
        """
        Test that when filtering topics and there are no topics to track, another empty dictionary is returned.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertEqual({ }, consumer._filter_topics({ 'goal': (Vector(), Cluster()) }, [ ]))

    def test_filter_topics_only_tracking(self):
        """
        Test that when filtering topics, the function only returns the terms that are still bursting.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector(), Cluster()),
            'foul': (Vector(), Cluster()),
        }
        self.assertEqual({ 'goal' }, set(consumer._filter_topics(topics, [ 'goal' ])))

    def test_filter_topics_same_vectors(self):
        """
        Test that the topics' vectors do not change when filtering them.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster()),
            'foul': (Vector({ 'foul': 0.6 }), Cluster()),
        }
        tracked = consumer._filter_topics(topics, topics.keys())
        self.assertTrue(all( tracked[term][0] == topics[term][0] for term in topics ))
        self.assertTrue(all( tracked[term][0].to_array() == topics[term][0].to_array() for term in topics ))

    def test_filter_topics_same_clusters(self):
        """
        Test that the topics' clusters do not change when filtering them.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster()),
            'foul': (Vector({ 'foul': 0.6 }), Cluster()),
        }
        tracked = consumer._filter_topics(topics, topics.keys())
        self.assertTrue(all( tracked[term][1] == topics[term][1] for term in topics ))
        self.assertTrue(all( tracked[term][1].to_array() == topics[term][1].to_array() for term in topics ))

    def test_dormant_empty(self):
        """
        Test that when checking whether the stream is dormant and the volume is empty, the function always returns ``True``.
        """

        consumer = FUEGOConsumer(Queue(), min_volume=1)
        self.assertEqual({ }, consumer.volume.all())
        self.assertTrue(consumer._dormant(9))
        self.assertTrue(consumer._dormant(10))

    def test_dormant_exclusive(self):
        """
        Test that when checking the volume in the last time window, the check is exclusive.
        """

        consumer = FUEGOConsumer(Queue(), min_volume=1)
        consumer.volume.add(10, 1.1)
        self.assertFalse(consumer._dormant(10))
        consumer.volume.add(10, 1)
        self.assertTrue(consumer._dormant(10)) # equal to the minimum volume
        consumer.volume.add(10, 0.9)
        self.assertTrue(consumer._dormant(10)) # less than the minimum volume

    def test_dormant_end_timestamp_inclusive(self):
        """
        Test that when checking the volume in the last time window, the given timestamp is inclusive.
        """

        consumer = FUEGOConsumer(Queue(), min_volume=1)
        consumer.volume.add(10, 1)
        self.assertTrue(consumer._dormant(9))
        self.assertTrue(consumer._dormant(10)) # equal to the minimum volume
        consumer.volume.add(10, 2)
        self.assertFalse(consumer._dormant(10)) # higher than the minimum volume

    def test_dormant_start_timestamp_exclusive(self):
        """
        Test that when checking whether the stream is dormant, the function uses the correct time window.
        """

        consumer = FUEGOConsumer(Queue(), min_volume=1, window_size=5)
        consumer.volume.add(5, 0)
        self.assertTrue(consumer._dormant(10)) # there is no volume at timestamp 10

        """
        Increase the window size so it covers timestamp 5 at timestamp 10.
        """
        consumer = FUEGOConsumer(Queue(), min_volume=1, window_size=6)
        consumer.volume.add(5, 0)
        self.assertTrue(consumer._dormant(10))
        consumer.volume.add(10, 1)
        self.assertTrue(consumer._dormant(10)) # equal to the minimum volume
        consumer.volume.add(10, 1.1)
        self.assertFalse(consumer._dormant(10)) # equal to the minimum volume

    def test_dormant_mean_negative(self):
        """
        Test that when checking the volume, if the average value of the past historic windows is negative, the minimum value is considered.
        This function is mainly meant to test that the function does not fail with negative historic windows.
        """

        consumer = FUEGOConsumer(Queue(), min_volume=2, window_size=10)
        consumer.volume.add(10, -20)
        consumer.volume.add(20, -30)
        consumer.volume.add(30, -30)
        consumer.volume.add(40, -30)
        consumer.volume.add(50, -30)
        consumer.volume.add(60, -20)

        self.assertTrue(consumer._dormant(60))

    def test_dormant_mean_zero(self):
        """
        Test that when checking the volume, if the average value of the past historic windows is zero, the minimum value is considered.
        This function is mainly meant to test that the function does not fail with zero historic windows.
        """

        consumer = FUEGOConsumer(Queue(), min_volume=2, window_size=10)
        consumer.volume.add(10, 0)
        consumer.volume.add(20, 0)
        consumer.volume.add(30, 0)
        consumer.volume.add(40, 0)
        consumer.volume.add(50, 0)
        consumer.volume.add(60, 0)

        self.assertTrue(consumer._dormant(60))

    def test_dormant_mean_small_numbers(self):
        """
        Test that when checking the volume, if the average value of the past historic windows is very small, the minimum value is considered.
        This function is mainly meant to test that the function does not fail with very small historic windows.
        """

        consumer = FUEGOConsumer(Queue(), min_volume=2, window_size=10)
        consumer.volume.add(10, 1e-300)
        consumer.volume.add(20, 4e-300)
        consumer.volume.add(30, 2e-300)
        consumer.volume.add(40, 3e-300)
        consumer.volume.add(50, 1e-300)
        consumer.volume.add(60, 1e-300)

        self.assertTrue(consumer._dormant(60))

    def test_dormant_mean_min_volume(self):
        """
        Test that when checking the volume, if the minimum volume is very low, the function considers the mean.
        """

        consumer = FUEGOConsumer(Queue(), min_volume=2, window_size=10, threshold=DynamicThreshold.MEAN)
        consumer.volume.add(10, 20)
        consumer.volume.add(20, 30)
        consumer.volume.add(30, 25)
        consumer.volume.add(40, 20)
        consumer.volume.add(50, 20)
        consumer.volume.add(60, 20)

        self.assertFalse(consumer._dormant(10)) # higher than the minimum volume

        _, historic = consumer._partition(20)
        self.assertEqual(20, statistics.mean(historic.values()))
        self.assertFalse(consumer._dormant(20)) # equal to the mean

        _, historic = consumer._partition(30)
        self.assertEqual(25, statistics.mean(historic.values()))
        self.assertEqual(7.07, round(statistics.stdev(historic.values()), 2))
        # self.assertTrue(consumer._dormant(30)) # lower than mean + stdev
        self.assertTrue(consumer._dormant(30)) # lower than mean

        self.assertTrue(consumer._dormant(40))
        self.assertTrue(consumer._dormant(50))
        self.assertTrue(consumer._dormant(60))

    def test_dormant_moving_mean_recent_only(self):
        """
        Test that when checking the mean volume, the function only considers the recent time windows.
        """

        consumer = FUEGOConsumer(Queue(), min_volume=2, window_size=10, windows=3, threshold=DynamicThreshold.MOVING_MEAN)
        consumer.volume.add(10, 20) # mean = 0 (no previous windows)
        consumer.volume.add(20, 30) # mean = 20 (from t=10)
        consumer.volume.add(30, 25) # mean = 25
        consumer.volume.add(40, 20) # mean = 25
        consumer.volume.add(50, 20) # mean = 25

        self.assertFalse(consumer._dormant(10)) # higher than the minimum volume

        _, historic = consumer._partition(20)
        self.assertEqual(20, statistics.mean(historic.values()))
        self.assertFalse(consumer._dormant(20)) # equal to the mean
        self.assertTrue(consumer._dormant(30)) # equal to the mean
        self.assertTrue(consumer._dormant(40)) # lower than the mean
        self.assertTrue(consumer._dormant(50)) # lower than the mean

        _, historic = consumer._partition(60)
        self.assertEqual(115 / 5, statistics.mean(historic.values()))

        consumer.volume.add(60, 22) # mean = 21.67 (average of 20, 20 and 25); overall mean: 23
        self.assertFalse(consumer._dormant(60)) # higher than the mean

        consumer.volume.add(60, 21) # mean = 21.67 (average of 20, 20 and 25); overall mean: 23
        self.assertTrue(consumer._dormant(60)) # equal to the mean

    def test_dormant_mean_stdev_volume(self):
        """
        Test that when checking the volume, if the minimum volume is very low, the function considers the mean and the standard deviation.
        """

        consumer = FUEGOConsumer(Queue(), min_volume=2, window_size=10, threshold=DynamicThreshold.MEAN_STDEV)
        consumer.volume.add(10, 20)
        consumer.volume.add(20, 30)
        consumer.volume.add(30, 25)
        consumer.volume.add(40, 20)
        consumer.volume.add(50, 20)
        consumer.volume.add(60, 20)

        self.assertFalse(consumer._dormant(10)) # higher than the minimum volume

        _, historic = consumer._partition(20)
        self.assertEqual(20, statistics.mean(historic.values()))
        self.assertFalse(consumer._dormant(20)) # equal to the mean

        _, historic = consumer._partition(30)
        self.assertEqual(25, statistics.mean(historic.values()))
        self.assertEqual(7.07, round(statistics.stdev(historic.values()), 2))
        self.assertTrue(consumer._dormant(30)) # lower than mean + stdev

        self.assertTrue(consumer._dormant(40))
        self.assertTrue(consumer._dormant(50))
        self.assertTrue(consumer._dormant(60))

    def test_partition(self):
        """
        Test partitioning with an example.
        """

        consumer = FUEGOConsumer(Queue(), window_size=5)
        consumer.volume.add(60, 50)
        consumer.volume.add(55, 30)
        consumer.volume.add(50, 25)

        """
        Use the latest data.
        """
        current, historic = consumer._partition(timestamp=60)
        self.assertEqual(50, current)
        self.assertEqual(30, historic[55])
        self.assertEqual(25, historic[50])

        """
        Move one time window back.
        """
        current, historic = consumer._partition(timestamp=55)
        self.assertEqual(30, current)
        self.assertEqual(25, historic[50])

        """
        Use a larger time window.
        """
        consumer = FUEGOConsumer(Queue(), window_size=10)
        consumer.volume.add(60, 50)
        consumer.volume.add(55, 30)
        consumer.volume.add(50, 25)
        current, historic = consumer._partition(timestamp=60)
        self.assertEqual(80, current)
        self.assertEqual(25, historic[50])

    def test_partition_empty(self):
        """
        Test that when partitioning an empty volume store, the current value is 0 and the historic data is empty.
        """

        consumer = FUEGOConsumer(Queue(), window_size=10)
        current, historic = consumer._partition(600)
        self.assertEqual(0, current)
        self.assertEqual({ }, historic)

    def test_partition_nutrition_include_timestamp(self):
        """
        Test that when partitioning, the end timestamp of the volume is included.
        """

        consumer = FUEGOConsumer(Queue(), window_size=10)
        consumer.volume.add(60, 50)
        consumer.volume.add(50, 40)
        current, _ = consumer._partition(60)
        self.assertEqual(50, current)

    def test_partition_nutrition_exclude_timestamp(self):
        """
        Test that when partitioning, the start of the time window of the volume for the given timestamp is excluded.
        """

        consumer = FUEGOConsumer(Queue(), window_size=10)
        consumer.volume.add(60, 50)
        consumer.volume.add(51, 10)
        consumer.volume.add(50, 5)
        current, _ = consumer._partition(60)
        self.assertEqual(60, current)

    def test_partition_historic_until_inclusive(self):
        """
        Test that when partitioning, the ``until`` timestamp is inclusive in the volume and historic data.
        """

        consumer = FUEGOConsumer(Queue(), window_size=2)
        consumer.volume.add(10, 100)
        consumer.volume.add(9, 90)
        consumer.volume.add(8, 80)
        consumer.volume.add(7, 70)
        consumer.volume.add(6, 60)
        consumer.volume.add(5, 50)
        consumer.volume.add(4, 40)
        current, historic = consumer._partition(10)
        self.assertEqual(190, current)
        self.assertEqual(150, historic[8])
        self.assertEqual(110, historic[6])
        self.assertEqual(40, historic[4])

    def test_partition_time_windows(self):
        """
        Test that when partitioning, the function creates time windows that span the timespan of all documents.
        """

        consumer = FUEGOConsumer(Queue(), windows=1, window_size=2)
        consumer.volume.add(10, 100)
        consumer.volume.add(1, 10)
        current, historic = consumer._partition(10)
        self.assertEqual(4, len(historic))
        self.assertEqual([ 2, 4, 6, 8 ], sorted(historic.keys()))

    def test_partition_all_documents(self):
        """
        Test that when partitioning, the function creates time windows that include all documents.
        """

        consumer = FUEGOConsumer(Queue(), window_size=10, damping=0)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            consumer._update_volume(documents)
            timestamps = [ document.attributes['timestamp'] for document in documents ]

            current, historic = consumer._partition(max(timestamps))
            self.assertEqual(len(lines), current + sum(historic.values()))

    def test_detect_dict(self):
        """
        Test that when detecting bursty terms, the function returns a dictionary with strings as keys and burst values as values.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=0, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 10, 'b': 2, 'c': 3 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 10, 'c': 0 })
        bursty = consumer._detect(10)
        self.assertEqual(dict, type(bursty))
        self.assertTrue(bursty)
        self.assertEqual(set([ 'a', 'c' ]), set(bursty.keys()))
        self.assertTrue(all( str == type(term) for term in bursty.keys() ))
        self.assertTrue(all( float == type(burst) for burst in bursty.values() ))

    def test_detect_burst_start(self):
        """
        Test that when detecting bursty terms, the function returns terms that have a burst higher than the burst start.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=0, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        bursty = consumer._detect(10)
        self.assertEqual(set([ 'a', 'c' ]), set(bursty))

        """
        Increase the burst start value.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=0.5, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        bursty = consumer._detect(10)
        self.assertEqual(set([ 'a' ]), set(bursty))

    def test_detect_burst_start_negative(self):
        """
        Test that when detecting bursty terms, the function returns terms that have a burst higher than the burst start even when it is negative.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=-0.5, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        bursty = consumer._detect(10)
        self.assertEqual(set([ 'a', 'c' ]), set(bursty))

        """
        Decrease the burst start value.
        """
        consumer = FUEGOConsumer(Queue(), burst_start=-0.7, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5, 'd': 0 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 0.6, 'c': 0, 'd': 1 })
        bursty = consumer._detect(10)
        self.assertEqual(set([ 'a', 'b', 'c' ]), set(bursty))

    def test_detect_burst_start_exclusive(self):
        """
        Test that when detecting bursty terms, the function returns terms that have a burst higher than the burst start and this value is exclusive.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=-0.5, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        bursty = consumer._detect(10)
        self.assertEqual(set([ 'a', 'c' ]), set(bursty))

        """
        Decrease the burst start value.
        """
        consumer = FUEGOConsumer(Queue(), burst_start=-0.6, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5, 'd': 0 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 0.6, 'c': 0, 'd': 1 })
        bursty = consumer._detect(10)
        self.assertEqual(set([ 'a', 'c' ]), set(bursty))

        """
        Decrease the burst start value further.
        """
        consumer = FUEGOConsumer(Queue(), burst_start=-0.61, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5, 'd': 0 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 0.6, 'c': 0, 'd': 1 })
        bursty = consumer._detect(10)
        self.assertEqual(set([ 'a', 'b', 'c' ]), set(bursty))

    def test_detect_burst_no_weights(self):
        """
        Test the burst calculation for terms that correlate with no other terms.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=-0.5, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        consumer.correlations.add(10, { 'a': { 'b': 1 } })
        bursty = consumer._detect(10)
        self.assertEqual(set([ 'a', 'c' ]), set(bursty))

    def test_detect_burst_weights_upper_bound(self):
        """
        Test that when detecting topics using correlation weights, the upper bound of burst is still 1.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=-0.5, window_size=5, windows=3)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            consumer._update_nutrition(documents)
            consumer._update_correlations(documents)
            topics = consumer._detect(documents[-1].attributes['timestamp'])
            self.assertGreater(1, max(topics.values()))

    def test_detect_burst_weights_lower_bound(self):
        """
        Test that when detecting topics using correlation weights, the lower bound of burst is still 0.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=-0.5, window_size=5, windows=3)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            consumer._update_nutrition(documents)
            consumer._update_correlations(documents)
            topics = consumer._detect(documents[-1].attributes['timestamp'])
            self.assertGreater(0, min(topics.values()))

    def test_detect_no_duplicates(self):
        """
        Test that when detecting bursty terms, the function does not return duplicate terms.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=0, window_size=5, windows=3)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        bursty = consumer._detect(10)
        self.assertEqual(sorted(list(set(bursty))), sorted(bursty))

    def test_detect_correct_windows(self):
        """
        Test that when detecting bursty terms, the function uses the correct time windows.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=0.3, window_size=5, windows=2)
        consumer.nutrition.add(15, { 'a': 1, 'b': 1, 'c': 0.5 })
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        tracked = consumer._detect(10)
        self.assertEqual(set([ 'a', 'c' ]), set(tracked))
        bursty = consumer._track([ 'a', 'b', 'c' ], 15)
        self.assertEqual(set([ 'b' ]), set(bursty))

    def test_detect_timestamp_inclusive(self):
        """
        Test that when detecting bursty terms, the function includes the nutrition values at the given timestamp.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=0.3, window_size=5, windows=2)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        bursty = consumer._track([ 'a', 'b', 'c' ], 9)
        self.assertEqual(set(), set(bursty))
        bursty = consumer._detect(10)
        self.assertEqual(set([ 'a', 'c' ]), set(bursty))

    def test_detect_uses_burst_start(self):
        """
        Test that when detecting bursty terms, the function uses burst start, not burst end.
        """

        consumer = FUEGOConsumer(Queue(), burst_start=0.5, burst_end=0.3, window_size=5, windows=2)
        consumer.nutrition.add(10, { 'a': 1, 'b': 0, 'c': 0.5 })
        consumer.nutrition.add(5, { 'a': 0, 'b': 1, 'c': 0 })
        bursty = consumer._detect(10)
        self.assertEqual(set([ 'a' ]), set(bursty))

    def test_new_topics_list_of_str(self):
        """
        Test that the new topics are a list of strings.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster()),
            'foul': (Vector({ 'foul': 0.6 }), Cluster()),
        }
        terms = { 'goal': 0.7, 'foul': 0.5, 'tackl': 0.6 }
        self.assertEqual(list, type(consumer._new_topics({ }, terms)))
        self.assertTrue(all( str == type(term) for term in consumer._new_topics({ }, terms)))

    def test_new_topics_empty_topics(self):
        """
        Test that when there are no topics, all the bursty terms are new topics.
        """

        consumer = FUEGOConsumer(Queue())
        terms = { 'goal': 0.7, 'foul': 0.5 }
        self.assertEqual(set(terms), set(consumer._new_topics({ }, terms)))

    def test_new_topics_empty_bursty(self):
        """
        Test that when there are no bursty terms, there are no new topics.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertEqual([ ], consumer._new_topics({ }, [ ]))

    def test_new_topics_not_in_topics(self):
        """
        Test that any new topics are not already in the list of topics.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster()),
            'foul': (Vector({ 'foul': 0.6 }), Cluster()),
        }
        terms = { 'goal': 0.7, 'foul': 0.5, 'tackl': 0.6 }
        self.assertEqual([ 'tackl' ], consumer._new_topics(topics, terms))

    def test_new_topics_are_bursty(self):
        """
        Test that all new topics are bursty.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster()),
            'foul': (Vector({ 'foul': 0.6 }), Cluster()),
        }
        terms = { 'goal': 0.7, 'foul': 0.5, 'tackl': 0.6 }
        self.assertTrue(all( term in terms for term in consumer._new_topics(topics, terms) ))

    def test_new_topics_ignore_no_longer_bursty(self):
        """
        Test that when checking for new topics, terms that were bursting previously do not affect the function.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster()),
            'foul': (Vector({ 'foul': 0.6 }), Cluster()),
        }
        terms = { 'tackl': 0.6 }
        self.assertEqual([ 'tackl' ], consumer._new_topics(topics, terms))
        self.assertTrue(all( term not in topics for term in consumer._new_topics(topics, terms) ))

    def test_update_topics_by_reference(self):
        """
        Test that topics are updated by reference.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster()),
            'foul': (Vector({ 'foul': 0.6 }), Cluster()),
        }
        bursty = { 'goal': 0.8, 'foul': 0.5 }
        updated = consumer._update_topics(topics, bursty)
        self.assertEqual(updated, topics)

    def test_update_topics_smaller_burst(self):
        """
        Test that when updating topics, the vector's burst does not change if the burst is smaller.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster()),
            'foul': (Vector({ 'foul': 0.6 }), Cluster()),
        }
        bursty = { 'goal': 0.5 }
        updated = consumer._update_topics(topics, bursty)
        self.assertTrue(all( topics[term][0].to_array() == updated[term][0].to_array() for term in updated ))

    def test_update_topics_larger_burst(self):
        """
        Test that when updating topics, the vector's burst only changes if the burst is larger.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster()),
            'foul': (Vector({ 'foul': 0.6 }), Cluster()),
        }
        bursty = { 'goal': 0.8, 'foul': 0.5 }
        updated = consumer._update_topics(topics, bursty)
        self.assertEqual(topics['goal'][0].dimensions['goal'], bursty['goal'])
        self.assertEqual(0.6, topics['foul'][0].dimensions['foul'])

    def test_update_topics_missing_terms(self):
        """
        Test that if there are currently-bursting topics which are no longer bursty, the function ignores them.
        Note that this scenario should not happen normally.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster()),
            'foul': (Vector({ 'foul': 0.6 }), Cluster()),
        }
        tracking = list(topics)
        bursty = { 'goal': 0.8 }
        updated = consumer._update_topics(topics, bursty)
        self.assertEqual(set(tracking), set(updated))

    def test_update_topics_corresponding_burst(self):
        """
        Test that when updating topics, the vector's burst changes depending on the associated term's burst.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster()),
            'foul': (Vector({ 'foul': 0.6 }), Cluster()),
        }
        bursty = { 'goal': 0.8, 'foul': 0.9 }
        updated = consumer._update_topics(topics, bursty)
        self.assertEqual(topics['goal'][0].dimensions['goal'], bursty['goal'])
        self.assertEqual(topics['foul'][0].dimensions['foul'], bursty['foul'])

    def test_update_topics_new_terms(self):
        """
        Test that when introducing new terms as topics, the function adds a vector and an empty cluster.
        """

        consumer = FUEGOConsumer(Queue())
        topics = { }
        bursty = { 'goal': 0.8 }
        updated = consumer._update_topics(topics, bursty)
        self.assertTrue(all( term in updated for term in bursty ))
        self.assertTrue(all( Vector == type(updated[term][0]) for term in bursty ))
        self.assertTrue(all( updated[term][0].dimensions[term] == bursty[term] for term in bursty ))
        self.assertTrue(all( Cluster == type(updated[term][1]) for term in bursty ))

    def test_update_topics_empty_topics(self):
        """
        Test that when there are no topics, all bursty terms are new topics.
        """

        consumer = FUEGOConsumer(Queue())
        topics = { }
        bursty = { 'goal': 0.8, 'foul': 0.5 }
        updated = consumer._update_topics(topics, bursty)
        self.assertEqual(set(bursty), set(updated))

    def test_update_topics_empty_burst(self):
        """
        Test that when updating topics, if there are no bursty terms, the function returns the previous topics.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster()),
            'foul': (Vector({ 'foul': 0.6 }), Cluster()),
        }
        tracking = set(topics)
        updated = consumer._update_topics(topics, { })
        self.assertEqual(tracking, set(updated))

    def test_update_topics_does_not_change_clusters(self):
        """
        Test that when updating topics, existing clusters do not change.
        """

        consumer = FUEGOConsumer(Queue())
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster(vectors=[ Document('ABC') ])),
            'foul': (Vector({ 'foul': 0.6 }), Cluster(vectors=[ Document('DEF') ])),
        }
        clusters = { term: topics[term][1].to_array() for term in topics }
        bursty = { 'goal': 0.8, 'foul': 0.5 }
        updated = consumer._update_topics(topics, bursty)
        self.assertTrue(all( updated[term][1].to_array() == clusters[term] for term in topics ))

    def test_add_to_timeline_no_topics(self):
        """
        Test that when adding no topics to the timeline, the timeline does not change.
        """

        consumer = FUEGOConsumer(Queue())
        timeline = Timeline(TopicalClusterNode, expiry=60, min_similarity=0.5)
        consumer._add_to_timeline(101, timeline, { })

    def test_add_to_timeline_by_reference(self):
        """
        Test that when adding topics to the timeline, vectors and clusters are copied by reference.
        """

        consumer = FUEGOConsumer(Queue())
        timeline = Timeline(TopicalClusterNode, expiry=60, min_similarity=0.5)
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster(vectors=[ Document('ABC') ])),
            'foul': (Vector({ 'foul': 0.6 }), Cluster(vectors=[ Document('DEF') ])),
        }

        # add a new node to the timeline
        consumer._add_to_timeline(101, timeline, topics)
        self.assertEqual(101, timeline.nodes[0].created_at)

        for i, (topic, (vector, cluster)) in enumerate(topics.items()):
            # update the burst of the vector
            new_burst = vector.dimensions[topic] + 1
            vector.dimensions[topic] = new_burst
            self.assertEqual(new_burst, timeline.nodes[0].topics[i].dimensions[topic])

            # add a new document to each cluster
            cluster.vectors.append(Document(topic))
            self.assertEqual(topic, timeline.nodes[0].clusters[i].vectors[-1].text)

    def test_add_to_timeline_no_duplicates(self):
        """
        Test when adding topics to the timeline, the function rejects duplicates.
        """

        consumer = FUEGOConsumer(Queue())
        timeline = Timeline(TopicalClusterNode, expiry=60, min_similarity=0.5)
        topics = {
            'goal': (Vector({ 'goal': 0.7 }), Cluster(vectors=[ Document('ABC') ])),
            'foul': (Vector({ 'foul': 0.6 }), Cluster(vectors=[ Document('DEF') ])),
        }

        # add a new node to the timeline
        consumer._add_to_timeline(101, timeline, topics)
        self.assertEqual(101, timeline.nodes[0].created_at)
        self.assertEqual(1, len(timeline.nodes))
        self.assertEqual(2, len(timeline.nodes[0].topics))
        self.assertEqual(2, len(timeline.nodes[0].clusters))

        # try to add the same topics to the timeline
        consumer._add_to_timeline(101, timeline, topics)
        self.assertEqual(101, timeline.nodes[0].created_at)
        self.assertEqual(1, len(timeline.nodes))
        self.assertEqual(2, len(timeline.nodes[0].topics))
        self.assertEqual(2, len(timeline.nodes[0].clusters))

    def test_collect_empty(self):
        """
        Test that when collecting from an empty list of documents, another empty list is returned.
        """

        consumer = FUEGOConsumer(Queue())
        self.assertEqual([ ], consumer._collect('chelsea', [ ]))

    def test_collect_all_include_term(self):
        """
        Test that when collecting documents that include a term, they all really contain that term.
        """

        consumer = FUEGOConsumer(Queue())
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            collected = consumer._collect('chelsea', documents)
            self.assertTrue(collected)
            self.assertTrue(all( 'chelsea' in document.dimensions for document in collected ))

    def tests_collect_includes_all_with_term(self):
        """
        Test that when collecting documents, all documents with the term are included.
        """

        consumer = FUEGOConsumer(Queue())
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            collected = consumer._collect('chelsea', documents)
            self.assertTrue(collected)
            for document in documents:
                if 'chelsea' in document.dimensions:
                    self.assertTrue(document in collected)

    def test_collect_no_duplicates(self):
        """
        Test that when collecting documents, the function does not return duplicates.
        """

        consumer = FUEGOConsumer(Queue())
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            collected = consumer._collect('chelsea', documents)
            self.assertTrue(collected)
            self.assertEqual(len(set(collected)), len(collected))

    def test_collect_does_not_change_documents(self):
        """
        Test that when collecting documents, the same documents are returned.
        """

        consumer = FUEGOConsumer(Queue())
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            collected = consumer._collect('chelsea', documents)
            self.assertTrue(collected)
            self.assertTrue(all( document in documents for document in collected ))

    def test_difference_empty_to_add(self):
        """
        Test that when getting unique documents, and the current documents is an empty list, the new unique documents are returned.
        """

        consumer = FUEGOConsumer(Queue())
        to_add = [ Document('ABC'), Document('DEF') ]
        self.assertFalse(to_add is consumer._difference(to_add, [ ]))
        self.assertEqual(to_add, consumer._difference(to_add, [ ]))

    def test_difference_empty_current(self):
        """
        Test that when checking for unique documents without providing any documents, an empty list is returned, regardless of the existing documents.
        """

        consumer = FUEGOConsumer(Queue())
        current = [ Document('ABC'), Document('DEF') ]
        self.assertEqual([ ], consumer._difference([ ], current))

    def test_difference_list_of_document(self):
        """
        Test that when getting the difference, a list of documents is returned.
        """

        consumer = FUEGOConsumer(Queue())
        to_add = [ Document('ABC'), Document('DEF') ]
        self.assertEqual(list, type(consumer._difference(to_add, [ ])))
        self.assertTrue(all( Document is type(document) for document in consumer._difference(to_add, [ ]) ))

    def test_difference_keep_to_add(self):
        """
        Test when using the difference operation, the original list of documents is not changed.
        """

        consumer = FUEGOConsumer(Queue())
        current = [ Document('ABC'), Document('DEF') ]
        to_add = [ Document('GHI'), Document('JKL') ]
        self.assertEqual(to_add, consumer._difference(to_add, current))
        self.assertEqual(2, len(to_add))

    def test_difference_keep_current(self):
        """
        Test when using the difference operation, the original list of documents is not changed.
        """

        consumer = FUEGOConsumer(Queue())
        current = [ Document('ABC'), Document('DEF') ]
        to_add = [ Document('GHI'), Document('JKL') ]
        self.assertEqual(to_add, consumer._difference(to_add, current))
        self.assertEqual(2, len(current))

    def test_difference_copy_by_reference(self):
        """
        Test that when getting the difference between two lists of documents, the documents are copied by reference.
        """

        consumer = FUEGOConsumer(Queue())
        current = [ Document('ABC'), Document('DEF') ]
        to_add = [ Document('GHI'), Document('JKL') ]
        self.assertEqual(to_add, consumer._difference(to_add, current))
        self.assertFalse(to_add is consumer._difference(to_add, current))
        self.assertTrue(all( document in to_add for document in consumer._difference(to_add, current) ))

    def test_difference_remove_duplicates_in_to_add(self):
        """
        Test that when getting the difference between two lists of documents, duplicates in the original list are not kept.
        """

        consumer = FUEGOConsumer(Queue())
        current = [ Document('ABC'), Document('DEF') ]
        document = Document('GHI')
        to_add = [ document, document ]
        self.assertFalse(to_add == consumer._difference(to_add, current))
        self.assertEqual(2, len(to_add))
        self.assertEqual(1, len(consumer._difference(to_add, current)))
        self.assertEqual([ document ], consumer._difference(to_add, current))
        self.assertEqual(list(set(to_add)), consumer._difference(to_add, current))

    def test_difference_same_order(self):
        """
        Test that the documents are kept in their original order when getting the difference.
        """

        consumer = FUEGOConsumer(Queue())
        documents = [ Document(letter) for letter in string.ascii_uppercase ]
        difference = consumer._difference(documents, [ ])
        self.assertEqual(string.ascii_uppercase, ''.join([ document.text for document in difference ]))

    def test_apply_reporting_empty(self):
        """
        Test that applying the reporting level to an empty set of documents returns another empty set.
        """

        consumer = FUEGOConsumer(Queue(), reporting=ReportingLevel.ALL)
        self.assertEqual([ ], consumer._apply_reporting_level([ ]))

    def test_apply_reporting_all(self):
        """
        Test that applying the reporting level with the `ALL` strategy returns the same list of documents.
        """

        consumer = FUEGOConsumer(Queue(), reporting=ReportingLevel.ALL)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

        self.assertEqual(documents, consumer._apply_reporting_level(documents))

    def test_apply_reporting_all_returns_list_of_documents(self):
        """
        Test that applying the reporting level with the `ALL` strategy returns a list of documents.
        """

        consumer = FUEGOConsumer(Queue(), reporting=ReportingLevel.ALL)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

        self.assertEqual(list, type(consumer._apply_reporting_level(documents)))
        self.assertTrue(all( Document == type(document) for document in consumer._apply_reporting_level(documents) ))

    def test_apply_reporting_original_returns_list_of_documents(self):
        """
        Test that applying the reporting level with the `ORIGINAL` strategy returns a list of documents.
        """

        consumer = FUEGOConsumer(Queue(), reporting=ReportingLevel.ORIGINAL)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

        self.assertEqual(list, type(consumer._apply_reporting_level(documents)))
        self.assertTrue(all( Document == type(document) for document in consumer._apply_reporting_level(documents) ))

    def test_apply_reporting_original_subset(self):
        """
        Test that applying the reporting level with the `ORIGINAL` strategy returns a subset of the original documents.
        """

        consumer = FUEGOConsumer(Queue(), reporting=ReportingLevel.ORIGINAL)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

        self.assertTrue(all( document in documents for document in consumer._apply_reporting_level(documents) ))

    def test_apply_reporting_original_same_order(self):
        """
        Test that applying the reporting level with the `ORIGINAL` strategy returns the documents in the original order.
        """

        consumer = FUEGOConsumer(Queue(), reporting=ReportingLevel.ORIGINAL)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

        filtered = consumer._apply_reporting_level(documents)
        self.assertTrue(all( documents.index(filtered[i]) < documents.index(filtered[i+1]) for i in  range(len(filtered) - 1) ))

    def test_apply_reporting_original_only_retweets(self):
        """
        Test that applying the reporting level with the `ORIGINAL` strategy to a list of retweets returns the same documents.
        """

        consumer = FUEGOConsumer(Queue(), reporting=ReportingLevel.ORIGINAL)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            tweets = [ tweet for tweet in tweets if twitter.is_retweet(tweet) ]
            documents = consumer._to_documents(tweets)

        self.assertEqual(documents, consumer._apply_reporting_level(documents))

    def test_apply_reporting_original_no_retweets(self):
        """
        Test that applying the reporting level with the `ORIGINAL` strategy returns no retweets if at least one document is not a retweet.
        """

        consumer = FUEGOConsumer(Queue(), reporting=ReportingLevel.ORIGINAL)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

        filtered = consumer._apply_reporting_level(documents)
        self.assertLess(len(filtered), len(documents))
        self.assertTrue(not any( document.is_retweet for document in filtered ))

    def test_summarize_empty_node(self):
        """
        Test that when summarizing an empty node, the function returns an empty summary.
        """

        consumer = FUEGOConsumer(Queue())
        node = TopicalClusterNode(created_at=10)
        summary = consumer._summarize(node)
        self.assertEqual(Summary, type(summary))
        self.assertEqual([ ], summary.documents)

    def test_summarize(self):
        """
        Test that when summarizing a node, the function returns a summary.
        """

        consumer = FUEGOConsumer(Queue())
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)

            node = TopicalClusterNode(created_at=10)
            node.add(Cluster([ document for document in documents
                                 if len(str(document)) < 140 ]), Vector({ 'chelsea': 0.6 }))
            summary = consumer._summarize(node)
            self.assertEqual(Summary, type(summary))
            self.assertTrue(summary.documents)
