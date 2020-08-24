"""
Test the functionality of the token split consumer.
"""

import asyncio
import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
	sys.path.append(path)

from nlp import Tokenizer
from nlp.weighting import TF
from queues import Queue
from queues.consumers.algorithms import ELDConsumer
from queues.consumers.token_split_consumer import TokenSplitConsumer

class TestTokenSplitConsumer(unittest.TestCase):
	"""
	Test the implementation of the token split consumer.
	"""

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

	def test_init_default_scheme(self):
		"""
		Test that the default term-weighting scheme is TF.
		"""

		splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
		self.assertEqual(TF, type(consumer.scheme))
