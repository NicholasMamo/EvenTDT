"""
Test the functionality of the FUEGO consumer.
"""

import asyncio
import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
	sys.path.append(path)

from queues import Queue
from queues.consumers.algorithms import FUEGOConsumer
from nlp.document import Document
from nlp.weighting import TF
from vsm import vector_math
from vsm.clustering import Cluster
import twitter

class TestFUEGOConsumer(unittest.TestCase):
	"""
	Test the implementation of the FUEGO consumer.
	"""

	def async_test(f):
		def wrapper(*args, **kwargs):
			coro = asyncio.coroutine(f)
			future = coro(*args, **kwargs)
			loop = asyncio.get_event_loop()
			loop.run_until_complete(future)
		return wrapper
