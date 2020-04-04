"""
Test the functionality of the base cleaner.
"""

import asyncio
import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
	sys.path.append(path)

from nlp.cleaners import Cleaner

class TestCleaner(unittest.TestCase):
	"""
	Test the implementation of the base cleaner.
	"""
