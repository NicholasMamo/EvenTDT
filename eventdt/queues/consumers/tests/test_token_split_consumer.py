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

from logger import logger
from queues import Queue
from queues.consumers import PrintConsumer
from queues.consumers.algorithms import ELDConsumer, ZhaoConsumer
from queues.consumers.token_split_consumer import TokenSplitConsumer
from summarization.timeline import Timeline

logger.set_logging_level(logger.LogLevel.WARNING)

class TestTokenSplitConsumer(unittest.TestCase):
	"""
	Test the implementation of the token split consumer.
	"""
