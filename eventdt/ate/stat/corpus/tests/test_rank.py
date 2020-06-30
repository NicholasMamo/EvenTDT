"""
Test the functionality of the rank difference extractor functions.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate.stat.corpus import RankExtractor
from ate import linguistic

class TestRankExtractor(unittest.TestCase):
	"""
	Test the functionality of the rank difference extractor functions.
	"""

	
