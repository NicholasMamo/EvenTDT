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
from logger import logger
from objects.exportable import Exportable
from queues import Queue
from queues.consumers import StatConsumer, TokenFilterConsumer, TokenSplitConsumer
from queues.consumers.algorithms import *
from queues.consumers.algorithms.fuego_consumer import DynamicThreshold

logger.set_logging_level(logger.LogLevel.WARNING)

class TestConsume(unittest.TestCase):
    """
    Test the functionality of the consume tool.
    """

    def test_is_own_timelines(self):
        """
        Test that checking whether an output was produced by this tool returns true when given its own output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', "#ParmaMilan-streams.json")
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            self.assertTrue(consume.is_own(output))

    def test_is_own_other(self):
        """
        Test that checking whether an output was produced by this tool returns false when given another tool's output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', "bootstrapped.json")
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            self.assertFalse(consume.is_own(output))

    def test_is_own_txt(self):
        """
        Test that checking whether an output was produced by this tool returns false when given another tool's output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "gold.txt")
        self.assertFalse(consume.is_own(file))

    def test_is_own_timelines_path(self):
        """
        Test that checking whether an output was produced by this tool returns true when given its own output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', "#ParmaMilan-streams.json")
        self.assertTrue(consume.is_own(file))

    def test_is_own_other_path(self):
        """
        Test that checking whether an output was produced by this tool returns false when given another tool's output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', "bootstrapped.json")
        self.assertFalse(consume.is_own(file))

    def test_load_from_output(self):
        """
        Test that when loading terms from the output of the tool, they are loaded correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', '#ParmaMilan-streams.json')
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            timelines = consume.load(output)
            original = output['timeline']
        self.assertEqual(original, timelines)

    def test_load_from_path(self):
        """
        Test that when loading timelines from a filepath, they are loaded correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', '#ParmaMilan-streams.json')
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            original = output['timeline']
        timelines = consume.load(file)
        self.assertEqual(original, timelines)

    def test_filters_all_words(self):
        """
        Test that when loading the filter tokens, all words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/consume/filters.csv')
        filters = consume.filters(file)

        """
        Assert that the correct number of filter tokens are loaded.
        """
        self.assertEqual(11, len(filters))
        self.assertEqual([ 'yellow', 'card', 'foul', 'tackl', 'ref',
                           'refere', 'var', 'goal', 'shot', 'keeper', 'save' ], filters)

    def test_filters_list(self):
        """
        Test that when loading the filter tokens, they are returned as a list.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/consume/filters.csv')
        filters = consume.filters(file)

        """
        Assert that the filters list is returned as a list.
        """
        self.assertEqual(list, type(filters))

    def test_filters_no_newlines(self):
        """
        Test that when loading the filter tokens, the newline symbol is removed.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/consume/filters.csv')
        filters = consume.filters(file)

        """
        Assert that the filters list does not contain any newlines.
        """
        self.assertFalse('\n' in filters)
        self.assertTrue(all( not token.endswith('\n') for token in filters ))

    def test_filters_extracted(self):
        """
        Test that when loading terms from the output of the ``terms`` tool, the terms themselves are loaded.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/bootstrapping/seed.json')
        terms = consume.filters(file)
        self.assertTrue(all( type(term) is str for term in terms ))
        with open(file) as f:
            original = json.loads(''.join(f.readlines()))['terms']
            original = [ term['term'] for term in original ]
        self.assertEqual(len(original), len(terms))

    def test_filters_extracted_cmd(self):
        """
        Test that when loading terms from the output of the ``terms`` tool, the terms themselves are loaded.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'sample.json')
        terms = consume.filters(file)
        self.assertTrue(all( type(term) is str for term in terms ))
        with open(file) as f:
            original = json.loads(''.join(f.readlines()))['terms']
            original = [ term['term'] for term in original ]
        self.assertEqual(len(original), len(terms))

    def test_filters_extracted_order(self):
        """
        Test that when loading terms from the output of the ``terms`` tool, they are loaded in order of rank.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/bootstrapping/seed.json')
        terms = consume.filters(file)
        with open(file) as f:
            original = json.loads(''.join(f.readlines()))['terms']
            original = [ term['term'] for term in original ]
        self.assertEqual(original, terms)

    def test_filters_bootstrapped(self):
        """
        Test that when loading terms from the output of the ``bootstrap`` tool, the terms themselves are loaded.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/bootstrapping/bootstrapped.json')
        terms = consume.filters(file)
        self.assertTrue(all( type(term) is str for term in terms ))
        with open(file) as f:
            data = json.loads(''.join(f.readlines()))
            original = data['meta']['seed'] + data['bootstrapped']
        self.assertEqual(len(original), len(terms))

    def test_filters_bootstrapped_order(self):
        """
        Test that when loading terms from the output of the ``bootstrap`` tool, the seed terms are first, followed by the bootstrapped terms.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/bootstrapping/bootstrapped.json')
        terms = consume.filters(file)
        with open(file) as f:
            data = json.loads(''.join(f.readlines()))
            original = data['meta']['seed'] + data['bootstrapped']
        self.assertEqual(original, terms)

    def test_filters_keep_two(self):
        """
        Test that when the maximum number of terms is 2, the first 2 terms are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/bootstrapping/bootstrapped.json')
        with open(file) as f:
            data = json.loads(''.join(f.readlines()))
            terms = data['meta']['seed'] + data['bootstrapped']
        self.assertEqual(terms[:2], consume.filters(file, keep=2))

    def test_filters_no_keep(self):
        """
        Test that when no maximum number of terms is given, all terms are retained.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/bootstrapping/bootstrapped.json')
        with open(file) as f:
            data = json.loads(''.join(f.readlines()))
            terms = data['meta']['seed'] + data['bootstrapped']
        self.assertEqual(terms, consume.filters(file, keep=None))

    def test_filters_keep(self):
        """
        Test that when the maximum number of terms is given, the first few terms are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/bootstrapping/bootstrapped.json')
        with open(file) as f:
            data = json.loads(''.join(f.readlines()))
            terms = data['meta']['seed'] + data['bootstrapped']
        self.assertEqual(terms[:3], consume.filters(file, keep=3))

    def test_filters_keep_many(self):
        """
        Test that when the maximum number of terms is higher than the number of terms, all terms are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/bootstrapping/bootstrapped.json')
        with open(file) as f:
            data = json.loads(''.join(f.readlines()))
            terms = data['meta']['seed'] + data['bootstrapped']
        self.assertEqual(terms, consume.filters(file, keep=len(terms) + 1))

    def test_splits_concepts(self):
        """
        Test that when loading splits from concepts, the concepts are loaded correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/ate/concepts.json')
        splits = consume.splits(file)
        with open(file) as f:
            concepts = json.loads(f.readline())['concepts']
            self.assertEqual(concepts, splits)

    def test_splits_all_words(self):
        """
        Test that when loading the split tokens, all words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/consume/splits.csv')
        splits = consume.splits(file)

        """
        Assert that the correct number of split tokens are loaded.
        """
        self.assertEqual(3, len(splits))
        self.assertEqual([ 'yellow', 'card', 'foul', 'tackl' ], splits[0])
        self.assertEqual([ 'ref', 'refere', 'var' ], splits[1])
        self.assertEqual([ 'goal', 'shot', 'keeper', 'save' ], splits[2])

    def test_splits_concepts_list(self):
        """
        Test that when loading splits from concepts, they are returned as a list
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/ate/concepts.json')
        splits = consume.splits(file)

        # assert that the splits list is returned as a list
        self.assertEqual(list, type(splits))
        self.assertTrue(all( type(split) is list for split in splits ))

    def test_splits_list(self):
        """
        Test that when loading the split tokens, they are returned as a list.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/consume/splits.csv')
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

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/consume/splits.csv')
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

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/consume/splits.csv')
        splits = consume.splits(file)

        """
        Assert that the splits list is returned as a list.
        """
        self.assertTrue(all( ',' not in token for split in splits for token in split ))

    def test_threshold_mean(self):
        """
        Test that the threshold function correctly maps 'mean' to the :class:`~queues.consumers.algorithms.fuego_consumer.DynamicThreshold.MEAN`.
        """

        self.assertEqual(DynamicThreshold.MEAN, consume.threshold('mean'))

    def test_threshold_moving_mean(self):
        """
        Test that the threshold function correctly maps 'moving_mean' to the :class:`~queues.consumers.algorithms.fuego_consumer.DynamicThreshold.MOVING_MEAN`.
        """

        self.assertEqual(DynamicThreshold.MOVING_MEAN, consume.threshold('moving_mean'))

    def test_threshold_mean_stdev(self):
        """
        Test that the threshold function correctly maps 'mean_stdev' to the :class:`~queues.consumers.algorithms.fuego_consumer.DynamicThreshold.MEAN_STDEV`.
        """

        self.assertEqual(DynamicThreshold.MEAN_STDEV, consume.threshold('mean_stdev'))

    def test_threshold_case_insensitive(self):
        """
        Test that the threshold function ignores the case when mapping.
        """

        self.assertEqual(DynamicThreshold.MEAN_STDEV, consume.threshold('Mean_STDEV'))

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
        consumer = consume.create_consumer(FIREConsumer, Queue(), scheme=scheme, min_size=5, min_burst=0.1, window_size=900,
                                           max_intra_similarity=0.9, periodicity=20, min_volume=50, threshold=0.8,
                                           burst_start=0.7, burst_end=0.4, log_nutrition=True,)
        self.assertEqual(5, consumer.min_size)
        self.assertEqual(20, consumer.periodicity)
        self.assertEqual(scheme, consumer.scheme)
        self.assertEqual(0.8, consumer.clustering.threshold)

        """
        ELD consumer
        """
        consumer = consume.create_consumer(ELDConsumer, Queue(), scheme=scheme, min_size=5, min_burst=0.1, window_size=900,
                                           max_intra_similarity=0.9, periodicity=20, min_volume=50, threshold=0.8,
                                           burst_start=0.7, burst_end=0.4, log_nutrition=True,)
        self.assertEqual(5, consumer.min_size)
        self.assertEqual(0.1, consumer.min_burst)
        self.assertEqual(0.9, consumer.max_intra_similarity)
        self.assertEqual(900, consumer.window_size)
        self.assertEqual(0.8, consumer.clustering.threshold)
        self.assertEqual(scheme, consumer.scheme)
        self.assertTrue(consumer.log_nutrition)

        """
        FUEGO consumer
        """
        consumer = consume.create_consumer(FUEGOConsumer, Queue(), scheme=scheme, min_size=5, min_burst=0.1, window_size=900,
                                           max_intra_similarity=0.9, periodicity=20, min_volume=50, threshold=0.8,
                                           burst_start=0.7, burst_end=0.4, log_nutrition=True, threshold_type=DynamicThreshold.MEAN_STDEV)
        self.assertEqual(scheme, consumer.scheme)
        self.assertEqual(50, consumer.min_volume)
        self.assertEqual(0.7, consumer.burst_start)
        self.assertEqual(0.4, consumer.burst_end)
        self.assertEqual(900, consumer.tdt.window_size)
        self.assertEqual(DynamicThreshold.MEAN_STDEV, consumer.threshold)

    def test_create_consumer_with_splits(self):
        """
        Test that when creating a consumer with splits, the function create a token split consumer with the correct consumers.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/consume/splits.csv')
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
        self.assertTrue(all( StatConsumer == type(_consumer) for _consumer in consumer.consumers ))

        """
        FIRE consumer
        """
        consumer = consume.create_consumer(FIREConsumer, Queue(), scheme=scheme, splits=splits,
                                           min_size=5, max_intra_similarity=0.9, freeze_period=10)
        self.assertEqual(TokenSplitConsumer, type(consumer))
        self.assertEqual(len(splits), len(consumer.consumers))
        self.assertTrue(all( FIREConsumer == type(_consumer) for _consumer in consumer.consumers ))

        """
        ELD consumer
        """
        consumer = consume.create_consumer(ELDConsumer, Queue(), scheme=scheme, splits=splits,
                                           min_size=5, max_intra_similarity=0.9, freeze_period=10)
        self.assertEqual(TokenSplitConsumer, type(consumer))
        self.assertEqual(len(splits), len(consumer.consumers))
        self.assertTrue(all( ELDConsumer == type(_consumer) for _consumer in consumer.consumers ))

        """
        FUEGO consumer
        """
        consumer = consume.create_consumer(FUEGOConsumer, Queue(), scheme=scheme, splits=splits,
                                           min_size=5, max_intra_similarity=0.9, freeze_period=10)
        self.assertEqual(TokenSplitConsumer, type(consumer))
        self.assertEqual(len(splits), len(consumer.consumers))
        self.assertTrue(all( FUEGOConsumer == type(_consumer) for _consumer in consumer.consumers ))

        """
        SEER consumer
        """
        consumer = consume.create_consumer(SEERConsumer, Queue(), scheme=scheme, splits=splits,
                                           min_size=5, max_intra_similarity=0.9, freeze_period=10)
        self.assertEqual(TokenSplitConsumer, type(consumer))
        self.assertEqual(len(splits), len(consumer.consumers))
        self.assertTrue(all( SEERConsumer == type(_consumer) for _consumer in consumer.consumers ))

    def test_create_consumer_with_splits_default(self):
        """
        Test that when creating a consumer with splits and a default stream, an extra stream is created.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/consume/splits.csv')
        splits = consume.splits(file)

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        with open(idf) as f:
            data = json.loads(f.readline())
            scheme = Exportable.decode(data)['tfidf']

        consumer = consume.create_consumer(StatConsumer, Queue(), scheme=scheme, splits=splits, with_default_split=False, periodicity=20)
        self.assertEqual(len(splits), len(consumer.splits))
        self.assertEqual(len(splits), len(consumer.consumers))

        consumer = consume.create_consumer(StatConsumer, Queue(), scheme=scheme, splits=splits, with_default_split=True, periodicity=20)
        self.assertEqual(len(splits) + 1, len(consumer.splits))
        self.assertEqual(len(splits) + 1, len(consumer.consumers))
        self.assertEqual('*', consumer.splits[-1])

    def test_create_consumer_with_splits_routing(self):
        """
        Test that when creating a consumer with splits, the function sends the right parameters to the child consumers.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/consume/splits.csv')
        splits = consume.splits(file)

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        with open(idf) as f:
            data = json.loads(f.readline())
            scheme = Exportable.decode(data)['tfidf']

        """
        Stat consumer
        """
        consumer = consume.create_consumer(StatConsumer, Queue(), scheme=scheme, splits=splits, periodicity=20)
        self.assertTrue(all( 20 == _consumer.periodicity for _consumer in consumer.consumers ))

        """
        Zhao consumer - default
        """
        consumer = consume.create_consumer(ZhaoConsumer, Queue(), scheme=scheme, splits=splits)
        self.assertTrue(all( 1.7 == _consumer.tdt.post_rate for _consumer in consumer.consumers ))

        """
        Zhao consumer - custom
        """
        consumer = consume.create_consumer(ZhaoConsumer, Queue(), scheme=scheme, splits=splits, periodicity=1, post_rate=2.1)
        self.assertTrue(all( 1 == _consumer.periodicity for _consumer in consumer.consumers ))
        self.assertTrue(all( 2.1 == _consumer.tdt.post_rate for _consumer in consumer.consumers ))

        """
        FIRE consumer
        """
        consumer = consume.create_consumer(FIREConsumer, Queue(), scheme=scheme, splits=splits, min_size=5,
                                           max_intra_similarity=0.9, min_burst=0.1, periodicity=20, threshold=0.8,
                                           min_volume=50, burst_start=0.7, burst_end=0.4, freeze_period=10,
                                           log_nutrition=True)
        self.assertTrue(all( FIREConsumer == type(_consumer) for _consumer in consumer.consumers ))
        self.assertTrue(all( 5 == _consumer.min_size for _consumer in consumer.consumers ))
        self.assertTrue(all( 20 == _consumer.periodicity for _consumer in consumer.consumers ))
        self.assertTrue(all( scheme == _consumer.scheme for _consumer in consumer.consumers ))
        self.assertTrue(all( 10 == _consumer.clustering.freeze_period for _consumer in consumer.consumers ))
        self.assertTrue(all( 0.8 == _consumer.clustering.threshold for _consumer in consumer.consumers ))

        """
        ELD consumer
        """
        consumer = consume.create_consumer(ELDConsumer, Queue(), scheme=scheme, splits=splits, window_size=90,
                                           min_size=5, min_burst=0.1, max_intra_similarity=0.9, threshold=0.8,
                                           periodicity=20, min_volume=50, burst_start=0.7, burst_end=0.4,
                                           freeze_period=10, log_nutrition=True)
        self.assertTrue(all( 90 == _consumer.window_size for _consumer in consumer.consumers ))
        self.assertTrue(all( 5 == _consumer.min_size for _consumer in consumer.consumers ))
        self.assertTrue(all( 0.1 == _consumer.min_burst for _consumer in consumer.consumers ))
        self.assertTrue(all( 0.9 == _consumer.max_intra_similarity for _consumer in consumer.consumers ))
        self.assertTrue(all( scheme == _consumer.scheme for _consumer in consumer.consumers ))
        self.assertTrue(all( 10 == _consumer.clustering.freeze_period for _consumer in consumer.consumers ))
        self.assertTrue(all( 0.8 == _consumer.clustering.threshold for _consumer in consumer.consumers ))
        self.assertTrue(all( _consumer.log_nutrition for _consumer in consumer.consumers ))

        """
        FUEGO consumer
        """
        consumer = consume.create_consumer(FUEGOConsumer, Queue(), scheme=scheme, splits=splits, threshold=0.8, window_size=900,
                                           min_size=5, min_burst=0.1, max_intra_similarity=0.9, threshold_type=DynamicThreshold.MEAN_STDEV,
                                           periodicity=20, min_volume=50, burst_start=0.7, burst_end=0.4,
                                           freeze_period=10, log_nutrition=True)
        self.assertTrue(all( scheme == _consumer.scheme for _consumer in consumer.consumers ))
        self.assertTrue(all( 50 == _consumer.min_volume for _consumer in consumer.consumers ))
        self.assertTrue(all( 0.7 == _consumer.burst_start for _consumer in consumer.consumers ))
        self.assertTrue(all( 0.4 == _consumer.burst_end for _consumer in consumer.consumers ))
        self.assertTrue(all( 900 == _consumer.tdt.window_size for _consumer in consumer.consumers ))
        self.assertTrue(all( DynamicThreshold.MEAN_STDEV == _consumer.threshold for _consumer in consumer.consumers ))

        """
        SEER consumer, alias for the FUEGO consumer
        """
        consumer = consume.create_consumer(SEERConsumer, Queue(), scheme=scheme, splits=splits, threshold=0.8, window_size=900,
                                           min_size=5, min_burst=0.1, max_intra_similarity=0.9, threshold_type=DynamicThreshold.MEAN_STDEV,
                                           periodicity=20, min_volume=50, burst_start=0.7, burst_end=0.4,
                                           freeze_period=10, log_nutrition=True)
        self.assertTrue(all( scheme == _consumer.scheme for _consumer in consumer.consumers ))
        self.assertTrue(all( 50 == _consumer.min_volume for _consumer in consumer.consumers ))
        self.assertTrue(all( 0.7 == _consumer.burst_start for _consumer in consumer.consumers ))
        self.assertTrue(all( 0.4 == _consumer.burst_end for _consumer in consumer.consumers ))
        self.assertTrue(all( 900 == _consumer.tdt.window_size for _consumer in consumer.consumers ))
        self.assertTrue(all( DynamicThreshold.MEAN_STDEV == _consumer.threshold for _consumer in consumer.consumers ))

    def test_create_consumer_with_filters(self):
        """
        Test that when creating a consumer with filters, the function create a token filter consumer with the correct consumers.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/consume/filters.csv')
        filters = consume.filters(file)

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        with open(idf) as f:
            data = json.loads(f.readline())
            scheme = Exportable.decode(data)['tfidf']

        """
        Stat
        """
        consumer = consume.create_consumer(StatConsumer, Queue(), scheme=scheme, filters=filters, freeze_period=10)
        self.assertEqual(TokenFilterConsumer, type(consumer))
        self.assertEqual(StatConsumer, type(consumer.consumer))

        """
        FIRE consumer
        """
        consumer = consume.create_consumer(FIREConsumer, Queue(), scheme=scheme, filters=filters,
                                           min_size=5, max_intra_similarity=0.9, freeze_period=10)
        self.assertEqual(TokenFilterConsumer, type(consumer))
        self.assertEqual(FIREConsumer, type(consumer.consumer))

        """
        ELD consumer
        """
        consumer = consume.create_consumer(ELDConsumer, Queue(), scheme=scheme, filters=filters,
                                           min_size=5, max_intra_similarity=0.9, freeze_period=10)
        self.assertEqual(TokenFilterConsumer, type(consumer))
        self.assertEqual(ELDConsumer, type(consumer.consumer))

    def test_create_consumer_with_filters_routing(self):
        """
        Test that when creating a consumer with filters, the function sends the right parameters to the child consumers.
        """

        file = os.path.join(os.path.dirname(__file__), '../../eventdt/tests/corpora/consume/filters.csv')
        filters = consume.filters(file)

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        with open(idf) as f:
            data = json.loads(f.readline())
            scheme = Exportable.decode(data)['tfidf']

        """
        Stat consumer
        """
        consumer = consume.create_consumer(StatConsumer, Queue(), scheme=scheme, filters=filters, periodicity=20)
        self.assertEqual(20, consumer.consumer.periodicity)

        """
        Zhao consumer - default
        """
        consumer = consume.create_consumer(ZhaoConsumer, Queue(), scheme=scheme, filters=filters)
        self.assertEqual(1.7, consumer.consumer.tdt.post_rate)

        """
        Zhao consumer - custom
        """
        consumer = consume.create_consumer(ZhaoConsumer, Queue(), scheme=scheme, filters=filters, periodicity=1, post_rate=2.1)
        self.assertEqual(1, consumer.consumer.periodicity)
        self.assertEqual(2.1, consumer.consumer.tdt.post_rate)

        """
        FIRE consumer
        """
        consumer = consume.create_consumer(FIREConsumer, Queue(), scheme=scheme, filters=filters, min_size=5,
                                           max_intra_similarity=0.9, min_burst=0.1, periodicity=20, threshold=0.8,
                                           min_volume=50, burst_start=0.7, burst_end=0.4, freeze_period=10,
                                           log_nutrition=True, threshold_type=DynamicThreshold.MEAN_STDEV)
        self.assertEqual(FIREConsumer, type(consumer.consumer))
        self.assertEqual(5, consumer.consumer.min_size)
        self.assertEqual(20, consumer.consumer.periodicity)
        self.assertEqual(scheme, consumer.consumer.scheme)
        self.assertEqual(10, consumer.consumer.clustering.freeze_period)
        self.assertEqual(0.8, consumer.consumer.clustering.threshold)

        """
        ELD consumer
        """
        consumer = consume.create_consumer(ELDConsumer, Queue(), scheme=scheme, filters=filters, window_size=90,
                                           min_size=5, min_burst=0.1, max_intra_similarity=0.9, threshold=0.8,
                                           periodicity=20, min_volume=50, burst_start=0.7, burst_end=0.4, freeze_period=10,
                                           log_nutrition=True, threshold_type=DynamicThreshold.MEAN_STDEV)
        self.assertEqual(5, consumer.consumer.min_size)
        self.assertEqual(0.1, consumer.consumer.min_burst)
        self.assertEqual(0.9, consumer.consumer.max_intra_similarity)
        self.assertEqual(90, consumer.consumer.window_size)
        self.assertEqual(scheme, consumer.consumer.scheme)
        self.assertEqual(0.8, consumer.consumer.clustering.threshold)
        self.assertEqual(10, consumer.consumer.clustering.freeze_period)
        self.assertTrue(consumer.consumer.log_nutrition)

        """
        FUEGO consumer
        """
        consumer = consume.create_consumer(FUEGOConsumer, Queue(), scheme=scheme, filters=filters,
                                           min_size=5, min_burst=0.1, max_intra_similarity=0.9, threshold=0.8, window_size=900,
                                           periodicity=20, min_volume=50, burst_start=0.7, burst_end=0.4, freeze_period=10,
                                           log_nutrition=True, threshold_type=DynamicThreshold.MEAN_STDEV)
        self.assertEqual(scheme, consumer.consumer.scheme)
        self.assertEqual(50, consumer.consumer.min_volume)
        self.assertEqual(0.7, consumer.consumer.burst_start)
        self.assertEqual(0.4, consumer.consumer.burst_end)
        self.assertEqual(900, consumer.consumer.tdt.window_size)
        self.assertEqual(DynamicThreshold.MEAN_STDEV, consumer.consumer.threshold)

        """
        SEER consumer, alias for the FUEGO consumer
        """
        consumer = consume.create_consumer(SEERConsumer, Queue(), scheme=scheme, filters=filters,
                                           min_size=5, min_burst=0.1, max_intra_similarity=0.9, threshold=0.8, window_size=900,
                                           periodicity=20, min_volume=50, burst_start=0.7, burst_end=0.4, freeze_period=10,
                                           log_nutrition=True, threshold_type=DynamicThreshold.MEAN_STDEV)
        self.assertEqual(scheme, consumer.consumer.scheme)
        self.assertEqual(50, consumer.consumer.min_volume)
        self.assertEqual(0.7, consumer.consumer.burst_start)
        self.assertEqual(0.4, consumer.consumer.burst_end)
        self.assertEqual(900, consumer.consumer.tdt.window_size)
        self.assertEqual(DynamicThreshold.MEAN_STDEV, consumer.consumer.threshold)
