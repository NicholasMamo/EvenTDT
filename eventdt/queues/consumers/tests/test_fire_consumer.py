"""
Test the functionality of the FIRE consumer.
"""

import asyncio
import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
	sys.path.append(path)

from queues import Queue
from queues.consumers import FIREConsumer
from nlp.term_weighting import TF

class TestFIREConsumer(unittest.TestCase):
	"""
	Test the implementation of the FIRE consumer.
	"""

	def test_create_consumer(self):
		"""
		Test that when creating a consumer, all the parameters are saved correctly.
		"""

		queue = Queue()
		consumer = FIREConsumer(queue, 60, scheme=TF())
		self.assertEqual(queue, consumer.queue)
		self.assertEqual(60, consumer.periodicity)
		self.assertEqual(TF, type(consumer.scheme))
