"""
Test the functionality of the FIRE consumer.
"""

import asyncio
import json
import logging
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from logger import logger
from queues import Queue
from queues.consumers.algorithms import FIREConsumer
from nlp.document import Document
from nlp.weighting import TF
from summarization.timeline import Timeline
from vsm import vector_math
from vsm.clustering import Cluster
import twitter

logger.set_logging_level(logger.LogLevel.WARNING)
logging.getLogger('asyncio').setLevel(logging.ERROR) # disable task length outputs

class TestFIREConsumer(unittest.IsolatedAsyncioTestCase):
    """
    Test the implementation of the FIRE consumer.
    """

    def test_init_name(self):
        """
        Test that the Zhao consumer passes on the name to the base class.
        """

        name = 'Test Consumer'
        consumer = FIREConsumer(Queue(), periodicity=10, name=name)
        self.assertEqual(name, str(consumer))

    def test_create_consumer(self):
        """
        Test that when creating a consumer, all the parameters are saved correctly.
        """

        queue = Queue()
        consumer = FIREConsumer(queue, 60, scheme=TF())
        self.assertEqual(queue, consumer.queue)
        self.assertEqual(60, consumer.periodicity)
        self.assertEqual(TF, type(consumer.scheme))

    async def test_run_returns(self):
        """
        Test that at the end, the FIRE consumer returns the number of consumed, filtered and skipped tweets, and a timeline.
        """

        """
        Create an empty queue.
        Use it to create a buffered consumer and set it running.
        """
        queue = Queue()
        consumer = FIREConsumer(queue, 60)
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

        """
        Create an empty queue.
        Use it to create a buffered consumer and set it running.
        """
        queue = Queue()
        consumer = FIREConsumer(queue, 60)
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
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
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
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
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
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
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
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
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
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
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
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            filtered = consumer._filter_tweets(tweets)
            self.assertTrue(all(tweet in tweets for tweet in filtered))

    def test_filter_tweets_document(self):
        """
        Test that when filtering a list of documents, the function looks for the tweet in the attributes.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF())
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
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

        consumer = FIREConsumer(Queue(), 60, TF())
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            tweet = json.loads(f.readline())
            document = consumer._to_documents([ tweet ])[0]
            self.assertEqual(tweet, document.attributes['tweet'])

    def test_to_documents_ellipsis(self):
        """
        Test that when the text has an ellipsis, the full text is used.
        """

        consumer = FIREConsumer(Queue(), 60, TF())
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
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
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
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
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
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
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
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

        consumer = FIREConsumer(Queue(), 60, TF())
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            for line in f:
                tweet = json.loads(line)
                document = consumer._to_documents([ tweet ])[0]
                if not document.dimensions:
                    continue

                self.assertEqual(1, round(vector_math.magnitude(document), 10))

    def test_to_documents_documents(self):
        """
        Test that when converting a list of documents to documents, they are retained unchanged.
        """

        consumer = FIREConsumer(Queue(), 60, TF())
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            self.assertEqual(documents, consumer._to_documents(documents))

    def test_latest_timestamp_empty(self):
        """
        Test that when getting the timestamp from an empty set, a ValueError is raised.
        """

        consumer = FIREConsumer(Queue(), 60)
        self.assertRaises(ValueError, consumer._latest_timestamp, [ ])

    def test_latest_timestamp(self):
        """
        Test getting the latest timestamp from a corpus of documents.
        """

        consumer = FIREConsumer(Queue(), 60)
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            self.assertEqual(documents[-1].attributes['timestamp'], consumer._latest_timestamp(documents))

    def test_latest_timestamp_reversed(self):
        """
        Test that when getting the latest timestamp from a corpus of reversed documents, the actual latest timestamp is given.
        """

        consumer = FIREConsumer(Queue(), 60)
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)[::-1]
            self.assertEqual(documents[0].attributes['timestamp'], consumer._latest_timestamp(documents))

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
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
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
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            filtered = consumer._filter_documents(documents)
            self.assertTrue(all(document in documents for document in filtered))

    def test_create_checkpoint_first(self):
        """
        Test that when creating the first checkpoint, the nutrition is created from scratch.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF())
        self.assertEqual({ }, consumer.store.all())
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            line = f.readline()
            tweet = json.loads(line)
            documents = consumer._to_documents([ tweet ])
            timestamp = twitter.extract_timestamp(tweet)
            consumer._create_checkpoint(timestamp, documents)
            self.assertTrue(consumer.store.get(timestamp))

    def test_create_checkpoint_empty(self):
        """
        Test that when creating an empty checkpoint, it is still recorded.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF())
        self.assertEqual({ }, consumer.store.all())
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            line = f.readline()
            tweet = json.loads(line)
            timestamp = twitter.extract_timestamp(tweet)
            consumer._create_checkpoint(timestamp, [ ])
            self.assertEqual({ }, consumer.store.get(timestamp))

    def test_create_checkpoint_timestamp(self):
        """
        Test that when creating checkpoints, the correct timestamp is recorded.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF())
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            line = f.readline()
            tweet = json.loads(line)
            documents = consumer._to_documents([ tweet ])
            timestamp = twitter.extract_timestamp(tweet)
            consumer._create_checkpoint(timestamp, documents)
            self.assertEqual([ timestamp ], list(consumer.store.all().keys()))

    def test_create_checkpoint_scale(self):
        """
        Test that when creating checkpoints, they are rescaled correctly.
        """

        consumer = FIREConsumer(Queue(), 60, TF())
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            documents = consumer._to_documents(tweets)
            timestamp = twitter.extract_timestamp(tweets[-1])
            consumer._create_checkpoint(timestamp, documents)
            self.assertLessEqual(0, min(consumer.store.get(timestamp).values()))
            self.assertEqual(1, max(consumer.store.get(timestamp).values()))

    def test_remove_old_checkpoints_empty(self):
        """
        Test that when removing checkpoints from an empty store, nothing happens.
        """

        consumer = FIREConsumer(Queue(), 60, TF())
        self.assertEqual({ }, consumer.store.all())
        consumer._remove_old_checkpoints(100)
        self.assertEqual({ }, consumer.store.all())

    def test_remove_old_checkpoints_zero_timestamp(self):
        """
        Test that when removing checkpoints at timestamp 0, nothing is removed.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF())
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            line = f.readline()
            tweet = json.loads(line)
            documents = consumer._to_documents([ tweet ])
            timestamp = twitter.extract_timestamp(tweet)
            consumer._create_checkpoint(timestamp, documents)
            self.assertEqual([ timestamp ], list(consumer.store.all().keys()))
            consumer._remove_old_checkpoints(0)

    def test_remove_old_checkpoints_small_timestamp(self):
        """
        Test that when removing checkpoints with a small timestamp that does not cover the entire sets, nothing is removed.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF())
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            line = f.readline()
            tweet = json.loads(line)
            documents = consumer._to_documents([ tweet ])
            timestamp = twitter.extract_timestamp(tweet)
            consumer._create_checkpoint(10, documents)
            self.assertEqual([ 10 ], list(consumer.store.all().keys()))
            consumer._remove_old_checkpoints(9)

    def test_remove_old_checkpoints_exclusive(self):
        """
        Test that when removing checkpoints, the removal is exclusive.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF(), sets=10)
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            line = f.readline()
            tweet = json.loads(line)
            documents = consumer._to_documents([ tweet ])
            timestamp = twitter.extract_timestamp(tweet)
            consumer._create_checkpoint(timestamp, documents)
            self.assertEqual([ timestamp ], list(consumer.store.all().keys()))
            consumer._remove_old_checkpoints(timestamp + 600)
            self.assertEqual([ timestamp ], list(consumer.store.all().keys()))

    def test_remove_old_checkpoints(self):
        """
        Test that when removing checkpoints, any nutrition data out of frame is removed.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF(), sets=10)
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            line = f.readline()
            tweet = json.loads(line)
            documents = consumer._to_documents([ tweet ])
            timestamp = twitter.extract_timestamp(tweet)
            consumer._create_checkpoint(timestamp, documents)
            self.assertEqual([ timestamp ], list(consumer.store.all().keys()))
            consumer._remove_old_checkpoints(timestamp + 600 + 1)
            self.assertEqual([ ], list(consumer.store.all().keys()))

    def test_filter_clusters_empty(self):
        """
        Test that when filtering an empty list of clusters, another empty list is returned.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF())
        self.assertEqual([ ], consumer._filter_clusters([ ]))

    def test_filter_clusters_size_inclusive(self):
        """
        Test that when filtering a list of clusters, the minimum size is inclusive.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF(), min_size=3)
        cluster = Cluster()
        for i in range(3):
            cluster.vectors.append(Document(''))
        self.assertEqual([ cluster ], consumer._filter_clusters([ cluster ]))

    def test_filter_clusters_small(self):
        """
        Test that when filtering a list of clusters, small clusters are filtered out.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF(), min_size=3)
        cluster = Cluster()
        for i in range(2):
            cluster.vectors.append(Document(''))
        self.assertEqual([ ], consumer._filter_clusters([ cluster ]))

    def test_filter_clusters_large(self):
        """
        Test that when filtering a list of clusters, large clusters are retained.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF(), min_size=3)
        cluster = Cluster()
        for i in range(30):
            cluster.vectors.append(Document(''))
        self.assertEqual([ cluster ], consumer._filter_clusters([ cluster ]))

    def test_filter_clusters_mix(self):
        """
        Test that when filtering a list of clusters with mixed sizes, only those that need to be filtered out are removed.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF(), min_size=3)
        clusters = [ Cluster(), Cluster() ]

        for i in range(3):
            clusters[0].vectors.append(Document(''))

        for i in range(2):
            clusters[0].vectors.append(Document(''))

        self.assertEqual([ clusters[0] ], consumer._filter_clusters(clusters))

    def test_detect_topics_store_unchanged(self):
        """
        Test that when detecting topics, the nutrition store itself does not change.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF(), sets=10)
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            line = f.readline()
            tweet = json.loads(line)
            documents = consumer._to_documents([ tweet ])
            timestamp = twitter.extract_timestamp(tweet)
            consumer._create_checkpoint(timestamp, documents)
            self.assertEqual([ timestamp ], list(consumer.store.all().keys()))
            self.assertEqual(documents[0].dimensions.keys(), consumer.store.get(timestamp).keys())

            """
            Create a new cluster with a different tweet.
            The function should not replace the original nutrition data, only make a copy.
            """
            line = f.readline()
            tweet = json.loads(line)
            cluster = Cluster(consumer._to_documents([ tweet ]))
            consumer._detect_topics(cluster, timestamp)
            self.assertEqual(documents[0].dimensions.keys(), consumer.store.get(timestamp).keys())

    def test_detect_topics_breaking(self):
        """
        Test that when detecting topics, the returned terms are breaking.
        """

        consumer = FIREConsumer(Queue(), 60, scheme=TF(), sets=10)
        with open(os.path.join(os.path.dirname(__file__), '../../../../tests/corpora/CRYCHE-500.json')) as f:
            line = f.readline()
            tweet = json.loads(line)
            documents = consumer._to_documents([ tweet ])
            timestamp = twitter.extract_timestamp(tweet)
            consumer._create_checkpoint(timestamp, documents)
            self.assertEqual([ timestamp ], list(consumer.store.all().keys()))
            self.assertEqual(documents[0].dimensions.keys(), consumer.store.get(timestamp).keys())

            """
            Create a new cluster with a sligtly different tweet.
            The function should return some of the different dimensions as breaking terms.
            """
            document = documents[0].copy()
            document.text = document.text + ' pipe'
            cluster = Cluster(document)
            terms = consumer._detect_topics(cluster, timestamp + 60)
            self.assertEqual([ 'pipe' ], terms)
