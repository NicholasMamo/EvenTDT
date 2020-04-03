"""
Test the functionality of the ELD consumer.
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
from queues.consumers import ELDConsumer
from nlp.document import Document
from nlp.term_weighting import TF
from vsm import vector_math
from vsm.clustering import Cluster
import twitter

class TestELDConsumer(unittest.TestCase):
	"""
	Test the implementation of the ELD consumer.
	"""
