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
from queues import Queue
from queues.consumers import StatConsumer, TokenSplitConsumer
from queues.consumers.algorithms import ELDConsumer, FIREConsumer

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

		consumer = consume.create_consumer(StatConsumer, Queue(), periodicity=20)
		self.assertEqual(20, consumer.periodicity)

		consumer = consume.create_consumer(FIREConsumer, Queue(), min_size=5, min_burst=0.1,
										   max_intra_similarity=0.9, periodicity=20)
		self.assertEqual(5, consumer.min_size)
		self.assertEqual(20, consumer.periodicity)

		consumer = consume.create_consumer(ELDConsumer, Queue(), min_size=5, min_burst=0.1,
										   max_intra_similarity=0.9, periodicity=20)
		self.assertEqual(5, consumer.min_size)
		self.assertEqual(0.1, consumer.min_burst)
		self.assertEqual(0.9, consumer.max_intra_similarity)

	def test_create_consumer_with_splits(self):
		"""
		Test that when creating a consumer with splits, the function create a token split consumer with the correct consumers.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'consume', 'splits.csv')
		splits = consume.splits(file)

		consumer = consume.create_consumer(StatConsumer, Queue(), splits=splits)
		self.assertEqual(TokenSplitConsumer, type(consumer))
		self.assertEqual(len(splits), len(consumer.consumers))
		self.assertTrue(all( StatConsumer == type(consumer) for consumer in consumer.consumers ))

		consumer = consume.create_consumer(FIREConsumer, Queue(), splits=splits,
										   min_size=5, max_intra_similarity=0.9)
		self.assertEqual(TokenSplitConsumer, type(consumer))
		self.assertEqual(len(splits), len(consumer.consumers))
		self.assertTrue(all( FIREConsumer == type(consumer) for consumer in consumer.consumers ))

		consumer = consume.create_consumer(ELDConsumer, Queue(), splits=splits,
										   min_size=5, max_intra_similarity=0.9)
		self.assertEqual(TokenSplitConsumer, type(consumer))
		self.assertEqual(len(splits), len(consumer.consumers))
		self.assertTrue(all( ELDConsumer == type(consumer) for consumer in consumer.consumers ))

	def test_create_consumer_with_splits_routing(self):
		"""
		Test that when creating a consumer with splits, the function sends the right parameters to the child consumers.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'consume', 'splits.csv')
		splits = consume.splits(file)

		consumer = consume.create_consumer(StatConsumer, Queue(), splits=splits, periodicity=20)
		self.assertTrue(all( 20 == consumer.periodicity for consumer in consumer.consumers ))

		consumer = consume.create_consumer(FIREConsumer, Queue(), splits=splits, min_size=5,
										   max_intra_similarity=0.9, min_burst=0.1, periodicity=20)
		self.assertTrue(all( FIREConsumer == type(consumer) for consumer in consumer.consumers ))
		self.assertTrue(all( 5 == consumer.min_size for consumer in consumer.consumers ))
		self.assertTrue(all( 20 == consumer.periodicity for consumer in consumer.consumers ))

		consumer = consume.create_consumer(ELDConsumer, Queue(), splits=splits,
										   min_size=5, min_burst=0.1, max_intra_similarity=0.9)
		self.assertTrue(all( 5 == consumer.min_size for consumer in consumer.consumers ))
		self.assertTrue(all( 0.1 == consumer.min_burst for consumer in consumer.consumers ))
		self.assertTrue(all( 0.9 == consumer.max_intra_similarity for consumer in consumer.consumers ))
