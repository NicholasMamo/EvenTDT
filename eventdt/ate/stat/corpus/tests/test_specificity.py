"""
Test the functionality of the domain specificity extractor functions.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate.stat.corpus import SpecificityExtractor

class TestSpecificityExtractor(unittest.TestCase):
	"""
	Test the functionality of the domain specificity extractor functions.
	"""
