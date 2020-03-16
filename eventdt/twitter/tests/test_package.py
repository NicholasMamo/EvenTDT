"""
Test the functionality of the tweet package-level functions.
"""

import math
import os
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

import twitter

class TestPackage(unittest.TestCase):
	"""
	Test the functionality of the tweet package-level functions.
	"""

	
