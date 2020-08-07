"""
Test the functionality of the correlation tool.
"""

import json
import os
import sys
import unittest

from datetime import datetime

paths = [ os.path.join(os.path.dirname(__file__), '..'),
 		  os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

import correlation
from eventdt.ate.bootstrapping.probability import PMIBootstrapper
from logger import logger

logger.set_logging_level(logger.LogLevel.ERROR)

class TestCorrelation(unittest.TestCase):
	"""
	Test the functionality of the correlation tool.
	"""
