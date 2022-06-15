"""
Test the functionality of the token split consumer.
"""

import asyncio
import json
import os
import re
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from logger import logger
from nlp import Document, Tokenizer
from nlp.weighting import TF, TFIDF
from objects.exportable import Exportable
from queues import Queue
from queues.consumers.algorithms import ELDConsumer, ZhaoConsumer
from queues.consumers import TokenFilterConsumer, TokenSplitConsumer
from summarization.timeline import Timeline
import twitter
from vsm import vector_math

logger.set_logging_level(logger.LogLevel.WARNING)

class TestTokenSplitConsumer(unittest.TestCase):
    """
    Test the implementation of the token split consumer.
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
        Test that the split consumer passes on the name to the base class.
        """

        name = 'Test Consumer'
        splits = [ ('tackl'), ('goal') ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, name=name)
        self.assertEqual(name, str(consumer))

    def test_init_custom_tokenizer(self):
        """
        Test that when creating the token split consumer with a custom tokenizer, it is used instead of the default one.
        """

        splits = [ ('tackl'), ('goal') ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        self.assertTrue(consumer.tokenizer.stem)
        tokenizer = Tokenizer(stem=False)
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, tokenizer=tokenizer)
        self.assertFalse(consumer.tokenizer.stem)

    def test_create_token_filter_with_tokenizer(self):
        """
        Test that the token filter consumers inherit the token split consumer's tokenizer.
        """

        splits = [ ('tackl'), ('goal') ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        self.assertTrue(consumer.tokenizer.stem)
        tokenizer = Tokenizer(stem=False)
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, tokenizer=tokenizer)
        self.assertFalse(consumer.tokenizer.stem)
        self.assertTrue(not any( _consumer.tokenizer.stem for _consumer in consumer.consumers ))

    def test_init_list_of_list_splits(self):
        """
        Test that when providing a list of list for splits, they are unchanged.
        """

        splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        self.assertEqual(splits, consumer.splits)

    def test_init_list_of_tuple_splits(self):
        """
        Test that when providing a list of tuples for splits, they are converted into lists.
        """

        splits = [ ( 'yellow', 'card' ), ( 'foul', 'tackl' ) ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        self.assertEqual([ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ], consumer.splits)

    def test_init_list_of_str_splits(self):
        """
        Test that when providing a list of strings for splits, they are converted into lists.
        """

        splits = [ 'yellow', 'card' ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        self.assertEqual([ [ 'yellow' ], [ 'card' ] ], consumer.splits)

    def test_init_mixed_splits(self):
        """
        Test that when providing a mix of splits, they are converted into lists.
        """

        splits = [ 'book', [ 'yellow', 'card' ], ( 'foul', 'tackl' ) ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        self.assertEqual([ [ 'book' ], [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ], consumer.splits)

    def test_init_consumer_splits(self):
        """
        Test that the token split consumer creates as many consumers as the number of splits.
        """

        splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        self.assertEqual(2, len(consumer.splits))
        self.assertEqual(2, len(consumer.consumers))

    def test_init_consumer_names(self):
        """
        Test that the token split consumer gives consumers a name when creating them.
        """

        splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        self.assertEqual("['yellow', 'card']", str(consumer.consumers[0].consumer))
        self.assertEqual("['foul', 'tackl']", str(consumer.consumers[1].consumer))

    def test_init_consumers_are_token_filter(self):
        """
        Test that when initializing the token split consumer, its consumers are actually token filter consumers.
        """

        splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        self.assertEqual(2, len(consumer.consumers))
        self.assertTrue(all( type(_consumer) == TokenFilterConsumer for _consumer in consumer.consumers ))
        self.assertTrue(all( type(_consumer.consumer) == ELDConsumer for _consumer in consumer.consumers ))

    def test_init_consumers_default(self):
        """
        Test the default configuration of the downstream consumers.
        This is a sanity check to ensure that by default, the first and second-level consumers have the same configurations.
        """

        splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        self.assertTrue(all( _consumer.consumer.tokenizer.stem for _consumer in consumer.consumers ))
        self.assertTrue(all( _consumer.consumer.tokenizer.stopwords for _consumer in consumer.consumers ))
        self.assertTrue(all( _consumer.consumer.tokenizer.remove_unicode_entities for _consumer in consumer.consumers ))
        self.assertTrue(all( _consumer.consumer.tokenizer.normalize_words for _consumer in consumer.consumers ))
        self.assertTrue(all( 3 == _consumer.consumer.tokenizer.character_normalization_count for _consumer in consumer.consumers ))

    def test_create_token_filter_with_scheme(self):
        """
        Test that the token filter consumers inherit the token split consumer's scheme.
        """

        # create the consumer with a TF-IDF scheme
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, scheme=idf)
        self.assertTrue(all( _consumer.scheme == idf for _consumer in consumer.consumers ))
        self.assertTrue(all( _consumer.consumer.scheme == idf for _consumer in consumer.consumers ))

    def test_create_token_filter_with_matches(self):
        """
        Test that when creating the token filter consumers, they inherit the ``matches`` parameter.
        """

        splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]

        # test with the 'any' function
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, matches=any)
        self.assertEqual(any, consumer.matches)
        self.assertTrue(all( any == _consumer.matches for _consumer in consumer.consumers ))

        # test with the 'all' function
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, matches=all)
        self.assertEqual(all, consumer.matches)
        self.assertTrue(all( all == _consumer.matches for _consumer in consumer.consumers ))

    def test_init_default_scheme(self):
        """
        Test that the default term-weighting scheme is TF.
        """

        splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        self.assertEqual(TF, type(consumer.scheme))

    def test_init_saves_scheme(self):
        """
        Test that the token split consumer stores the given scheme.
        """

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenSplitConsumer(Queue(), filters, ELDConsumer, scheme=idf)
        self.assertEqual(idf, consumer.scheme)
        self.assertEqual(TFIDF, type(consumer.scheme))

    def test_init_consumers_arguments(self):
        """
        Test that when passing on extra arguments to the token split consumer, they are passed on to the consumer.
        """

        splits = [ (0, 50), (50, 100) ]
        consumer = TokenSplitConsumer(Queue(), splits, ZhaoConsumer)
        self.assertTrue(all( 5 == _consumer.consumer.periodicity for _consumer in consumer.consumers ))

        consumer = TokenSplitConsumer(Queue(), splits, ZhaoConsumer, periodicity=10)
        self.assertTrue(all( 10 == _consumer.consumer.periodicity for _consumer in consumer.consumers ))

    @async_test
    async def test_run_returns_timelines(self):
        """
        Test that when running the split consumer, it returns the timelines and other data from its consumers.
        """

        splits = [ (0, 50), (50, 100) ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        self.assertFalse(consumer.active)
        self.assertTrue(consumer.stopped)
        self.assertTrue(all( not _consumer.active for _consumer in consumer.consumers ))
        self.assertTrue(all( _consumer.stopped for _consumer in consumer.consumers ))

        """
        Run the consumer.
        """
        running = asyncio.ensure_future(consumer.run(max_inactivity=1))
        await asyncio.sleep(1)
        self.assertTrue(consumer.active)
        self.assertFalse(consumer.stopped)
        self.assertTrue(all( _consumer.active for _consumer in consumer.consumers ))
        self.assertTrue(all( not _consumer.stopped for _consumer in consumer.consumers ))

        """
        Wait for the consumer to finish.
        """
        results = (await asyncio.gather(running))[0]
        self.assertEqual({ 'consumed', 'filtered', 'skipped', 'timeline' }, set(results.keys()))
        self.assertTrue(all( type(timeline) is Timeline for timeline in results['timeline'] ))

    @async_test
    async def test_run_consumed_(self):
        """
        Test that when running the split consumer, the returned document includes a ``consume`` key with one value for each split.
        """

        splits = [ (0, 50), (50, 100) ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        self.assertFalse(consumer.active)
        self.assertTrue(consumer.stopped)
        self.assertTrue(all( not _consumer.active for _consumer in consumer.consumers ))
        self.assertTrue(all( _consumer.stopped for _consumer in consumer.consumers ))

        """
        Run the consumer.
        """
        running = asyncio.ensure_future(consumer.run(max_inactivity=1))
        await asyncio.sleep(1)
        self.assertTrue(consumer.active)
        self.assertFalse(consumer.stopped)
        self.assertTrue(all( _consumer.active for _consumer in consumer.consumers ))
        self.assertTrue(all( not _consumer.stopped for _consumer in consumer.consumers ))

        """
        Wait for the consumer to finish.
        """
        results = (await asyncio.gather(running))[0]
        self.assertEqual({ 'consumed', 'filtered', 'skipped', 'timeline' }, set(results.keys()))
        self.assertTrue(all( len(splits) == len(results[key]) for key in results ))
        self.assertEqual(len(splits), len(results['consumed']))

    def test_to_documents_expands_mentions(self):
        """
        Test that when converting a list of tweets to documents, mentions are expanded.
        """

        wrong_pattern = re.compile("@[0-9,\\s…]")
        no_space_pattern = re.compile("[^\\s]@")
        end_pattern = re.compile('@$')

        # tokenize all of the tweets
        splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(f.readline())
                text = twitter.full_text(tweet)
                document = consumer.consumers[0]._preprocess(tweet)

                # allow for some manual validation
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

    def test_satisfies_any(self):
        """
        Test that when validating tweets using the ``any`` function, only one token needs to be in the document for it to be valid.
        """

        trivial = True

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        splits = [ [ 'chelsea', 'cfc' ] ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, matches=any, scheme=idf)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                """
                If the document contains either of the tokens, it should succeed.
                Otherwise, the function should fail.
                """
                document = consumer.consumers[0]._preprocess(json.loads(line))
                if splits[0][0] in document.dimensions or splits[0][1] in document.dimensions:
                    trivial = False
                    self.assertTrue(consumer.consumers[0]._satisfies(document, splits[0]))
                else:
                    self.assertFalse(consumer.consumers[0]._satisfies(document, splits[0]))

        if trivial:
            logger.warning("Trivial test")

    def test_satisfies_all(self):
        """
        Test that when validating tweets using the ``all`` function, all tokens need to be in the document for it to be valid.
        """

        trivial = True

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        splits = [ [ 'chelsea', 'cfc' ] ]
        consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, matches=all, scheme=idf)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                """
                If the document contains both tokens, it should succeed.
                Otherwise, the function should fail.
                """
                document = consumer.consumers[0]._preprocess(json.loads(line))
                if splits[0][0] in document.dimensions and splits[0][1] in document.dimensions:
                    trivial = False
                    self.assertTrue(consumer.consumers[0]._satisfies(document, splits[0]))
                else:
                    self.assertFalse(consumer.consumers[0]._satisfies(document, splits[0]))

        if trivial:
            logger.warning("Trivial test")

    @async_test
    async def test_run_correct_streams(self):
        """
        Test that when running, the consumers receive the right tweets.
        """

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']


        """
        Create an empty queue.
        Use it to create a split consumer and set it running.
        Wait a second so that the buffered consumer (ZhaoConsumer) finds nothing and goes to sleep.
        """
        queue = Queue()
        splits = [ [ 'chelsea', 'cfc' ], [ 'crystal' , 'palace' ] ]
        consumer = TokenSplitConsumer(queue, splits, ZhaoConsumer, matches=any, scheme=idf, periodicity=300) # 5 minutes periodicity so that the queue is never emptied
        running = asyncio.ensure_future(consumer.run(max_inactivity=3))
        await asyncio.sleep(0.1)

        """
        Load all tweets into the queue.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                queue.enqueue(json.loads(line))

        """
        Wait some time for the consumer passes on its tweets to the downstream consumers, and then for those consumers to move the tweets from the queue to the buffer.
        Then, stop the consumers before they process any tweets.
        """
        await asyncio.sleep(0.5)
        consumer.stop()

        """
        Wait for the consumer to finish.
        """
        results = (await asyncio.gather(running))[0]
        self.assertEqual(2, len(consumer.consumers))
        self.assertTrue(sum( consumer.consumer.buffer.length() for consumer in consumer.consumers )) # documents go from the queue into the buffer since it's a buffered consumer

        """
        Ensure that the documents were partitioned properly.
        """
        for split, consumer in zip(splits, consumer.consumers):
            documents = consumer.consumer.buffer.dequeue_all()
            for document in documents:
                self.assertTrue(any( token in document.dimensions for token in split ))

    @async_test
    async def test_run_multiple_streams(self):
        """
        Test that when running, the consumer may send a tweet to multiple consumers.
        """

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']


        """
        Create an empty queue.
        Use it to create a split consumer and set it running.
        Wait a second so that the buffered consumer (ZhaoConsumer) finds nothing and goes to sleep.
        """
        queue = Queue()
        splits = [ [ 'chelsea', 'cfc' ], [ 'crystal' , 'palace' ] ]
        consumer = TokenSplitConsumer(queue, splits, ZhaoConsumer, matches=any, scheme=idf, periodicity=300) # 5 minutes periodicity so that the queue is never emptied
        running = asyncio.ensure_future(consumer.run(max_inactivity=3))
        await asyncio.sleep(0.1)

        """
        Load all tweets into the queue.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                queue.enqueue(json.loads(line))

        """
        Wait some time for the consumer passes on its tweets to the downstream consumers, and then for those consumers to move the tweets from the queue to the buffer.
        Then, stop the consumers before they process any tweets.
        """
        await asyncio.sleep(0.5)
        consumer.stop()

        """
        Wait for the consumer to finish.
        """
        results = (await asyncio.gather(running))[0]
        self.assertEqual(2, len(consumer.consumers))
        self.assertTrue(sum( consumer.consumer.buffer.length() for consumer in consumer.consumers )) # documents go from the queue into the buffer since it's a buffered consumer

        """
        Ensure that the documents were partitioned properly.
        """
        documents = [ ]
        for split, consumer in zip(splits, consumer.consumers):
            documents.extend(consumer.consumer.buffer.dequeue_all())

        ids = [ document.attributes['tweet']['id'] for document in documents ]
        self.assertGreater(len(ids), len(set(ids)))
