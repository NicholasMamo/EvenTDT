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
