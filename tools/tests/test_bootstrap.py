"""
Test the functionality of the bootstrap tool.
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

import tokenizer as tool
from eventdt.nlp.tokenizer import Tokenizer

class TestBootstrap(unittest.TestCase):
	"""
	Test the functionality of the bootstrap tool.
	"""
