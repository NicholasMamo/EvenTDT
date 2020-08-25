"""
Test the functionality of the buffered consumer.
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
from queues.buffered_consumer import DummySimulatedBufferedConsumer

logger.set_logging_level(logger.LogLevel.WARNING)

class TestSimulatedBufferedConsumer(unittest.TestCase):
	"""
	Test the implementation of the buffered consumer.
	"""
