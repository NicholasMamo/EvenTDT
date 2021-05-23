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
from nlp.weighting import TF
from objects.exportable import Exportable
from queues import Queue
from queues.consumers.algorithms import ELDConsumer, ZhaoConsumer
from queues.consumers.token_filter_consumer import TokenFilterConsumer
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

        filters = [ ('tackl'), ('goal') ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertTrue(consumer.tokenizer.stem)
        tokenizer = Tokenizer(stem=False)
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer, tokenizer=tokenizer)
        self.assertFalse(consumer.tokenizer.stem)

    def test_init_list_of_list_filters(self):
        """
        Test that when providing a list of list for filters, they are unchanged.
        """

        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertEqual(filters, consumer.filters)

    def test_init_list_of_tuple_filters(self):
        """
        Test that when providing a list of tuples for filters, they are converted into lists.
        """

        filters = [ ( 'yellow', 'card' ), ( 'foul', 'tackl' ) ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertEqual([ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ], consumer.filters)

    def test_init_list_of_str_filters(self):
        """
        Test that when providing a list of strings for filters, they are converted into lists.
        """

        filters = [ 'yellow', 'card' ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertEqual([ [ 'yellow' ], [ 'card' ] ], consumer.filters)

    def test_init_mixed_filters(self):
        """
        Test that when providing a mix of filters, they are converted into lists.
        """

        filters = [ 'book', [ 'yellow', 'card' ], ( 'foul', 'tackl' ) ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertEqual([ [ 'book' ], [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ], consumer.filters)

    def test_init_consumer_filters(self):
        """
        Test that the token filter consumer creates as many consumers as the number of filters.
        """

        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertEqual(2, len(consumer.filters))
        self.assertTrue(consumer.consumer)

    def test_init_default_scheme(self):
        """
        Test that the default term-weighting scheme is TF.
        """

        filters = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
        consumer = TokenFilterConsumer(Queue(), filters, ELDConsumer)
        self.assertEqual(TF, type(consumer.scheme))

    def test_init_consumers_arguments(self):
        """
        Test that when passing on extra arguments to the token filter consumer, they are passed on to the consumer.
        """

        filters = [ (0, 50), (50, 100) ]
        consumer = TokenFilterConsumer(Queue(), filters, ZhaoConsumer)
        self.assertEqual(5 , consumer.consumer.periodicity)

        consumer = TokenFilterConsumer(Queue(), filters, ZhaoConsumer, periodicity=10)
        self.assertEqual(10, consumer.consumer.periodicity)
