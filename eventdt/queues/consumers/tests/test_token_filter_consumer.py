"""
Test the functionality of the token filter consumer.
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
from queues.consumers.algorithms import FUEGOConsumer, ELDConsumer, ZhaoConsumer
from queues.consumers.token_filter_consumer import TokenFilterConsumer
from summarization.timeline import Timeline
import twitter
from vsm import vector_math

logger.set_logging_level(logger.LogLevel.WARNING)

class TestTokenFilterConsumer(unittest.TestCase):
    """
    Test the implementation of the token filter consumer.
    """

    def async_test(f):
        def wrapper(*args, **kwargs):
            coro = asyncio.coroutine(f)
            future = coro(*args, **kwargs)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(future)
        return wrapper

    def test_init_custom_tokenizer(self):
        """
        Test that when creating the token filter consumer with a custom tokenizer, it is used instead of the default one.
        """

        filters = [ 'tackl', 'goal' ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertTrue(consumer.tokenizer.stem)
        tokenizer = Tokenizer(stem=False)
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer, tokenizer=tokenizer)
        self.assertFalse(consumer.tokenizer.stem)

    def test_init_str_filters(self):
        """
        Test that when providing string as a filter, it is converted into lists.
        """

        filters = 'yellow'
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertEqual([ 'yellow' ], consumer.filters)

    def test_init_list_of_str_filters(self):
        """
        Test that when providing a list of strings for filters, they are retained as a list.
        """

        filters = [ 'yellow', 'card' ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertEqual([ 'yellow', 'card' ], consumer.filters)

    def test_init_consumer_filters(self):
        """
        Test that the token filter consumer creates as many consumers as the number of filters.
        """

        filters = [ 'yellow', 'card', 'foul', 'tackl' ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertEqual(4, len(consumer.filters))
        self.assertTrue(consumer.consumer)

    def test_init_default_scheme(self):
        """
        Test that the default term-weighting scheme is TF.
        """

        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertEqual(TF, type(consumer.scheme))

    def test_init_saves_scheme(self):
        """
        Test that the token filter consumer stores the given scheme.
        """

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer, scheme=idf)
        self.assertEqual(idf, consumer.scheme)
        self.assertEqual(TFIDF, type(consumer.scheme))

    def test_init_saves_scheme_to_consumers(self):
        """
        Test that the token filter consumer also stores the given scheme in its consumers.
        """

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer, scheme=idf)
        self.assertEqual(idf, consumer.consumer.scheme)
        self.assertEqual(TFIDF, type(consumer.consumer.scheme))

    def test_init_consumers_arguments(self):
        """
        Test that when passing on extra arguments to the token filter consumer, they are passed on to the consumer.
        """

        filters = [ (0, 50), (50, 100) ]
        consumer = TokenFilterConsumer(Queue(), filters, ZhaoConsumer)
        self.assertEqual(5 , consumer.consumer.periodicity)

        consumer = TokenFilterConsumer(Queue(), filters, ZhaoConsumer, periodicity=10)
        self.assertEqual(10, consumer.consumer.periodicity)

    def test_init_consumers_default(self):
        """
        Test the default configuration of the downstream consumers.
        This is a sanity check to ensure that by default, the first and second-level consumers have the same configurations.
        """

        filters = [ (0, 50), (50, 100) ]
        consumer = TokenFilterConsumer(Queue(), filters, FUEGOConsumer)
        self.assertTrue(consumer.consumer.tokenizer.stem)
        self.assertTrue(consumer.consumer.tokenizer.stopwords)
        self.assertTrue(consumer.consumer.tokenizer.remove_unicode_entities)
        self.assertTrue(consumer.consumer.tokenizer.normalize_words)
        self.assertEqual(3, consumer.consumer.tokenizer.character_normalization_count)

    @async_test
    async def test_run_filters(self):
        """
        Test that when running, the downstream consumer receives filtered tweets.
        """

        # create the consumer with a TF-IDF scheme
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        """
        Create an empty queue.
        Use it to create a split consumer and set it running.
        Wait a second so that the buffered consumer (ZhaoConsumer) finds nothing and goes to sleep.
        """
        queue = Queue()
        filters = [ 'chelsea', 'cfc' ]
        consumer = TokenFilterConsumer(queue, filters, ZhaoConsumer, matches=any, scheme=idf, periodicity=300) # 5 minutes periodicity so that the queue is never emptied
        running = asyncio.ensure_future(consumer.run(max_inactivity=3))
        await asyncio.sleep(0.1)

        # load all tweets into the queue
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                queue.enqueue(json.loads(line))

        """
        Wait some time for the consumer passes on its tweets to the downstream consumers, and then for those consumers to move the tweets from the queue to the buffer.
        Then, stop the consumers before they process any tweets.
        """
        await asyncio.sleep(0.5)
        consumer.stop()

        # wait for the consumer to finish
        results = (await asyncio.gather(running))[0]
        self.assertTrue(consumer.consumer.buffer.length()) # documents go from the queue into the buffer since it's a buffered consumer

        # ensure that the documents were partitioned properly
        documents = consumer.consumer.buffer.dequeue_all()
        for document in documents:
            self.assertTrue(any( token in document.dimensions for token in filters ))

    @async_test
    async def test_run_returns_consumed_after_filter(self):
        """
        Test that at the end, when the filter consumer returns the number of consumed tweets, the count includes only filtered tweets.
        """

        """
        Create an empty queue.
        Use it to create a consumer and set it running.
        """
        queue = Queue()
        filters = [ 'chelsea', 'cfc' ]
        consumer = TokenFilterConsumer(queue, filters, ELDConsumer)
        running = asyncio.ensure_future(consumer.run(max_inactivity=3))
        await asyncio.sleep(0.5)

        """
        Load all tweets into the queue.
        """
        with open(os.path.join(os.path.dirname(__file__), '../../../tests/corpora/CRYCHE-500.json')) as f:
            tweets = [ json.loads(line) for line in f ]
            queue.enqueue(*tweets)

        output = await running
        self.assertEqual(dict, type(output))
        self.assertTrue('consumed' in output)
        self.assertGreater(500, output['consumed'])

    @async_test
    async def test_run_returns_timeline(self):
        """
        Test that when running the filter consumer, it returns the timeline from its own consumers.
        """

        filters = [ 'chelsea', 'cfc' ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertFalse(consumer.active)
        self.assertTrue(consumer.stopped)
        self.assertFalse(consumer.consumer.active)
        self.assertTrue(consumer.consumer.stopped)

        """
        Run the consumer.
        """
        running = asyncio.ensure_future(consumer.run(max_inactivity=1))
        await asyncio.sleep(1)
        self.assertTrue(consumer.active)
        self.assertFalse(consumer.stopped)
        self.assertTrue(consumer.consumer.active)
        self.assertFalse(consumer.consumer.stopped)

        """
        Wait for the consumer to finish.
        """
        output = (await asyncio.gather(running))[0]
        self.assertEqual(dict, type(output))
        self.assertTrue('timeline' in output)
        self.assertEqual(Timeline, type(output['timeline']))

    def test_preprocess_creates_documents(self):
        """
        Test that when pre-processing tweets, the function creates documents.
        """

        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(Document, type(consumer._preprocess(tweet)))

    def test_preprocess_removes_stopwords(self):
        """
        Test that when pre-processing tweets, the returned documents do not have stopwords in them.
        """

        trivial = True

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        """
        Tokenize all of the tweets.
        Words like 'hazard' should have a greater weight than more common words, like 'goal'.
        """
        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer, scheme=idf)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                document = consumer._preprocess(json.loads(line))
                if 'and' in document.text.lower() or 'while' in document.text.lower():
                    trivial = False

                self.assertFalse('and' in document.dimensions)
                self.assertFalse('while' in document.dimensions)
                self.assertFalse('whil' in document.dimensions)

        if trivial:
            logger.warning("Trivial test")

    def test_preprocess_uses_scheme(self):
        """
        Test that when pre-processing tweets, the function uses the term-weighting scheme.
        """

        trivial = True

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        """
        Tokenize all of the tweets.
        Words like 'hazard' should have a greater weight than more common words, like 'goal'.
        """
        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer, scheme=idf)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                document = consumer._preprocess(json.loads(line))
                if 'hazard' in document.dimensions and 'goal' in document.dimensions:
                    trivial = False
                    self.assertGreater(document.dimensions['hazard'], document.dimensions['goal'])

        if trivial:
            logger.warning("Trivial test")

    def test_preprocess_normalizes_documents(self):
        """
        Test that when pre-processing tweets, the returned documents are normalized.
        """

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        """
        Tokenize all of the tweets.
        Words like 'hazard' should have a greater weight than more common words, like 'goal'.
        """
        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer, scheme=idf)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                document = consumer._preprocess(json.loads(line))
                self.assertTrue(round(vector_math.magnitude(document), 10) in [ 0, 1 ])

    def test_preprocess_with_text(self):
        """
        Test that when pre-processing tweets, the returned documents have non-empty text.
        """

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        """
        Tokenize all of the tweets.
        Words like 'hazard' should have a greater weight than more common words, like 'goal'.
        """
        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer, scheme=idf)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                document = consumer._preprocess(json.loads(line))
                self.assertTrue(document.text)

    def test_preprocess_with_full_text(self):
        """
        Test that when pre-processing tweets, the returned documents use the full text.
        """

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        """
        Tokenize all of the tweets.
        Words like 'hazard' should have a greater weight than more common words, like 'goal'.
        """
        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer, scheme=idf)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                document = consumer._preprocess(json.loads(line))
                self.assertFalse(document.text.endswith('…'))

    def test_preprocess_with_tweet(self):
        """
        Test that when pre-processing tweets, the returned documents include the original tweet.
        """

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        """
        Tokenize all of the tweets.
        """
        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer, scheme=idf)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                tweet = json.loads(line)
                document = consumer._preprocess(tweet)
                self.assertEqual(tweet, document.attributes['tweet'])

    def test_preprocess_with_timestamp(self):
        """
        Test that when pre-processing tweets, the returned documents include the timestamp as an attribute.
        """

        """
        Create the consumer with a TF-IDF scheme.
        """
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
            idf = Exportable.decode(json.loads(f.readline()))['tfidf']

        """
        Tokenize all of the tweets.
        """
        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer, scheme=idf)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                tweet = json.loads(line)
                document = consumer._preprocess(tweet)
                self.assertEqual(twitter.extract_timestamp(tweet), document.attributes['timestamp'])

    def test_to_documents_mentions_in_dimensions(self):
        """
        Test that when creating a document from a tweet, the expanded mentions are part of the dimensions.
        """

        # tokenize all of the tweets
        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'examples', '#ParmaMilan-hakan.json'), 'r') as f:
            tweet = json.loads(f.readline())
            document = consumer._preprocess(tweet)
            self.assertEqual(twitter.extract_timestamp(tweet), document.attributes['timestamp'])

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

        # tokenize all of the tweets
        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(f.readline())
                text = twitter.full_text(tweet)
                document = consumer._preprocess(tweet)

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

        filters = [ 'chelsea', 'cfc' ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer, matches=any, scheme=idf)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                """
                If the document contains either of the tokens, it should succeed.
                Otherwise, the function should fail.
                """
                document = consumer._preprocess(json.loads(line))
                if filters[0] in document.dimensions or filters[1] in document.dimensions:
                    trivial = False
                    self.assertTrue(consumer._satisfies(document, filters))
                else:
                    self.assertFalse(consumer._satisfies(document, filters))

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

        filters = [ 'chelsea', 'cfc' ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer, matches=all, scheme=idf)
        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
            for line in f:
                """
                If the document contains both tokens, it should succeed.
                Otherwise, the function should fail.
                """
                document = consumer._preprocess(json.loads(line))
                if filters[0] in document.dimensions and filters[1] in document.dimensions:
                    trivial = False
                    self.assertTrue(consumer._satisfies(document, filters))
                else:
                    self.assertFalse(consumer._satisfies(document, filters))

        if trivial:
            logger.warning("Trivial test")
