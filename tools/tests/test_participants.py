"""
Test the functionality of the APD tool.
"""

import json
import os
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
 		  os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

from tools import participants

class TestAPD(unittest.TestCase):
	"""
	Test the functionality of the APD tool.
	"""
