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
