"""
Test the functionality of the consume tool.
"""

import json
import os
import sys
import unittest

from datetime import datetime

paths = [ os.path.join(os.path.dirname(__file__), '..'),
           os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

import consume
from objects.exportable import Exportable
from queues import Queue
from queues.consumers import StatConsumer, TokenSplitConsumer
from queues.consumers.algorithms import *

class TestConsume(unittest.TestCase):
    """
    Test the functionality of the consume tool.
    """

    def test_splits_all_words(self):
        """
        Test that when loading the split tokens, all words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'consume', 'splits.csv')
        splits = consume.splits(file)

        """
        Assert that the correct number of split tokens are loaded.
        """
        self.assertEqual(3, len(splits))
        self.assertEqual([ 'yellow', 'card', 'foul', 'tackl' ], splits[0])
        self.assertEqual([ 'ref', 'refere', 'var' ], splits[1])
        self.assertEqual([ 'goal', 'shot', 'keeper', 'save' ], splits[2])

    def test_splits_list(self):
        """
        Test that when loading the split tokens, they are returned as a list.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'consume', 'splits.csv')
        splits = consume.splits(file)

        """
        Assert that the splits list is returned as a list.
        """
        self.assertEqual(list, type(splits))
        self.assertTrue(all( type(split) is list for split in splits ))

    def test_splits_no_newlines(self):
        """
        Test that when loading the split tokens, the newline symbol is removed.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'consume', 'splits.csv')
        splits = consume.splits(file)

        """
        Assert that the splits list is returned as a list.
        """
        self.assertTrue(all( '\n' not in split for split in splits ))
        self.assertTrue(all( not split[-1].endswith('\n') for split in splits ))

    def test_splits_no_commas(self):
        """
        Test that when loading the split tokens, there are no commas.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'consume', 'splits.csv')
        splits = consume.splits(file)

        """
        Assert that the splits list is returned as a list.
        """
        self.assertTrue(all( ',' not in token for split in splits for token in split ))

    def test_create_consumer_correct_routing(self):
        """
        Test that when creating a consumer, the parameters are sent only when necessary.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        with open(idf) as f:
            data = json.loads(f.readline())
            scheme = Exportable.decode(data)['tfidf']

        """
        Stat consumer
        """
        consumer = consume.create_consumer(StatConsumer, Queue(), scheme=scheme, periodicity=20)
        self.assertEqual(20, consumer.periodicity)

        """
        Zhao consumer - default
        """
        consumer = consume.create_consumer(ZhaoConsumer, Queue(), scheme=scheme)
        self.assertEqual(1.7, consumer.tdt.post_rate)

        """
        Zhao consumer - custom
        """
        consumer = consume.create_consumer(ZhaoConsumer, Queue(), scheme=scheme, periodicity=1, post_rate=2.1)
        self.assertEqual(1, consumer.periodicity)
        self.assertEqual(2.1, consumer.tdt.post_rate)

        """
        FIRE consumer
        """
        consumer = consume.create_consumer(FIREConsumer, Queue(), scheme=scheme, min_size=5, min_burst=0.1,
                                           max_intra_similarity=0.9, periodicity=20, min_volume=50,
                                           burst_start=0.7, log_nutrition=True,)
        self.assertEqual(5, consumer.min_size)
        self.assertEqual(20, consumer.periodicity)
        self.assertEqual(scheme, consumer.scheme)

        """
        ELD consumer
        """
        consumer = consume.create_consumer(ELDConsumer, Queue(), scheme=scheme, min_size=5, min_burst=0.1,
                                           max_intra_similarity=0.9, periodicity=20, min_volume=50,
                                           burst_start=0.7, log_nutrition=True,)
        self.assertEqual(5, consumer.min_size)
        self.assertEqual(0.1, consumer.min_burst)
        self.assertEqual(0.9, consumer.max_intra_similarity)
        self.assertEqual(scheme, consumer.scheme)
        self.assertTrue(consumer.log_nutrition)

        """
        FUEGO consumer
        """
        consumer = consume.create_consumer(FUEGOConsumer, Queue(), scheme=scheme, min_size=5, min_burst=0.1,
                                           max_intra_similarity=0.9, periodicity=20, min_volume=50,
                                           burst_start=0.7, log_nutrition=True,)
        self.assertEqual(scheme, consumer.scheme)
        self.assertEqual(50, consumer.min_volume)
        self.assertEqual(0.7, consumer.burst_start)

    def test_create_consumer_with_splits(self):
        """
        Test that when creating a consumer with splits, the function create a token split consumer with the correct consumers.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'consume', 'splits.csv')
        splits = consume.splits(file)

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        with open(idf) as f:
            data = json.loads(f.readline())
            scheme = Exportable.decode(data)['tfidf']

        """
        Stat
        """
        consumer = consume.create_consumer(StatConsumer, Queue(), scheme=scheme, splits=splits, freeze_period=10)
        self.assertEqual(TokenSplitConsumer, type(consumer))
        self.assertEqual(len(splits), len(consumer.consumers))
        self.assertTrue(all( StatConsumer == type(consumer) for consumer in consumer.consumers ))

        """
        FIRE consumer
        """
        consumer = consume.create_consumer(FIREConsumer, Queue(), scheme=scheme, splits=splits,
                                           min_size=5, max_intra_similarity=0.9, freeze_period=10)
        self.assertEqual(TokenSplitConsumer, type(consumer))
        self.assertEqual(len(splits), len(consumer.consumers))
        self.assertTrue(all( FIREConsumer == type(consumer) for consumer in consumer.consumers ))

        """
        ELD consumer
        """
        consumer = consume.create_consumer(ELDConsumer, Queue(), scheme=scheme, splits=splits,
                                           min_size=5, max_intra_similarity=0.9, freeze_period=10)
        self.assertEqual(TokenSplitConsumer, type(consumer))
        self.assertEqual(len(splits), len(consumer.consumers))
        self.assertTrue(all( ELDConsumer == type(consumer) for consumer in consumer.consumers ))

    def test_create_consumer_with_splits_routing(self):
        """
        Test that when creating a consumer with splits, the function sends the right parameters to the child consumers.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'consume', 'splits.csv')
        splits = consume.splits(file)

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        with open(idf) as f:
            data = json.loads(f.readline())
            scheme = Exportable.decode(data)['tfidf']

        """
        Stat consumer
        """
        consumer = consume.create_consumer(StatConsumer, Queue(), scheme=scheme, splits=splits, periodicity=20)
        self.assertTrue(all( 20 == consumer.periodicity for consumer in consumer.consumers ))

        """
        Zhao consumer - default
        """
        consumer = consume.create_consumer(ZhaoConsumer, Queue(), scheme=scheme, splits=splits)
        self.assertTrue(all( 1.7 == consumer.tdt.post_rate for consumer in consumer.consumers ))

        """
        Zhao consumer - custom
        """
        consumer = consume.create_consumer(ZhaoConsumer, Queue(), scheme=scheme, splits=splits, periodicity=1, post_rate=2.1)
        self.assertTrue(all( 1 == consumer.periodicity for consumer in consumer.consumers ))
        self.assertTrue(all( 2.1 == consumer.tdt.post_rate for consumer in consumer.consumers ))

        """
        FIRE consumer
        """
        consumer = consume.create_consumer(FIREConsumer, Queue(), scheme=scheme, splits=splits, min_size=5,
                                           max_intra_similarity=0.9, min_burst=0.1, periodicity=20,
                                           min_volume=50, burst_start=0.7, freeze_period=10,
                                           log_nutrition=True)
        self.assertTrue(all( FIREConsumer == type(consumer) for consumer in consumer.consumers ))
        self.assertTrue(all( 5 == consumer.min_size for consumer in consumer.consumers ))
        self.assertTrue(all( 20 == consumer.periodicity for consumer in consumer.consumers ))
        self.assertTrue(all( scheme == consumer.scheme for consumer in consumer.consumers ))
        self.assertTrue(all( 10 == consumer.clustering.freeze_period for consumer in consumer.consumers ))

        """
        ELD consumer
        """
        consumer = consume.create_consumer(ELDConsumer, Queue(), scheme=scheme, splits=splits,
                                           min_size=5, min_burst=0.1, max_intra_similarity=0.9,
                                           periodicity=20, min_volume=50, burst_start=0.7, freeze_period=10,
                                           log_nutrition=True)
        self.assertTrue(all( 5 == consumer.min_size for consumer in consumer.consumers ))
        self.assertTrue(all( 0.1 == consumer.min_burst for consumer in consumer.consumers ))
        self.assertTrue(all( 0.9 == consumer.max_intra_similarity for consumer in consumer.consumers ))
        self.assertTrue(all( scheme == consumer.scheme for consumer in consumer.consumers ))
        self.assertTrue(all( 10 == consumer.clustering.freeze_period for consumer in consumer.consumers ))
        self.assertTrue(all( consumer.log_nutrition for consumer in consumer.consumers ))

        """
        FUEGO consumer
        """
        consumer = consume.create_consumer(FUEGOConsumer, Queue(), scheme=scheme, splits=splits,
                                           min_size=5, min_burst=0.1, max_intra_similarity=0.9,
                                           periodicity=20, min_volume=50, burst_start=0.7, freeze_period=10,
                                           log_nutrition=True)
        self.assertTrue(all( scheme == consumer.scheme for consumer in consumer.consumers ))
        self.assertTrue(all( 50 == consumer.min_volume for consumer in consumer.consumers ))
        self.assertTrue(all( 0.7 == consumer.burst_start for consumer in consumer.consumers ))
