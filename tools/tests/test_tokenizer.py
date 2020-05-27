"""
Test the functionality of the tokenizer tool.
"""

import json
import os
import sys
import unittest

from datetime import datetime

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

import tokenizer

class TestTokenizer(unittest.TestCase):
	"""
	Test the functionality of the Tokenizer tool.
	"""

	def test_create_output_dir(self):
		"""
		Test that if the output directory does not exist, the tool creates it.
		"""

		path = 'tools/tests/.out/tokenized.json'
		dir = os.path.dirname(path)
		if os.path.exists(dir):
			os.rmdir(dir)

		tokenizer.prepare_output(path)
		self.assertTrue(os.path.exists(dir))
		os.rmdir(dir)
