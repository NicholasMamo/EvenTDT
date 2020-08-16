"""
Test the functionality of the summarization tool.
"""

import json
import os
import re
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
 		  os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

from tools import summarize
from summarization.algorithms import MMR, DGS

class TestSummarize(unittest.TestCase):
	"""
	Test the functionality of the summarization tool.
	"""
