"""
Test the functionality of the ATE package-level functions.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

import ate

class TestPackage(unittest.TestCase):
	"""
	Test the functionality of the ATE package-level functions.
	"""
