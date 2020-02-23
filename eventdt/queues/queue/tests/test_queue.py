"""
Test the functionality of the Wikipedia extrapolator.
"""

import os
import random
import re
import string
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

import queue

class TestQueue(unittest.TestCase):
	"""
	Test the implementation of the Queue.
	"""

	pass
