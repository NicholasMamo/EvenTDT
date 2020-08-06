"""
Test the functionality of the package functions.
"""

import json
import os
import sys
import unittest

from datetime import datetime

paths = [ os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

import tools

class TestPackage(unittest.TestCase):
	"""
	Test the functionality of the package functions.
	"""

	def test_is_json_json_file(self):
		"""
		Test that when given a JSON file path, it is recognized as a JSON file.
		"""

		self.assertTrue(tools.is_json('/path/to/file.json'))

	def test_is_json_text_file(self):
		"""
		Test that when given a text file path, it is not recognized as a JSON file.
		"""

		self.assertFalse(tools.is_json('/path/to/file.txt'))
