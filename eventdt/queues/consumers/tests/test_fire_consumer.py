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

class TestFIREConsumer(unittest.TestCase):
	"""
	Test the implementation of the FIRE consumer.
	"""
