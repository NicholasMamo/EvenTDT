"""
Test the functionality of the aggregation functions.
"""

import json
import os
import sys
import unittest

from datetime import datetime

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from twitter import corpus

class TestAggregate(unittest.TestCase):
	"""
	Test the functionality of the aggregation functions.
	"""

	pass
