"""
Test the functionality of the probability functions.
"""

import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from probability import *

class TestProbability(unittest.TestCase):
	"""
	Test the functionality of the probability functions.
	"""
