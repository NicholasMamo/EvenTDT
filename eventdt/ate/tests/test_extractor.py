"""
Test the functionality of the abstract extractor class.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from extractor import DummyExtractor

class TestPackage(unittest.TestCase):
	"""
	Test the functionality of the ATE package-level functions.
	"""
