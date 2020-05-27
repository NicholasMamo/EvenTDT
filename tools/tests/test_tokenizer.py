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

	def test_prepare_output_dir(self):
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

	def test_get_text_full(self):
		"""
		Test that when getting the text from tweets, the full text is returned.
		"""

		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				if '…' in tweet['text']:
					text = tokenizer.get_text(tweet)

					"""
					Make an exception for a special case.
					"""
					if not ('retweeted_status' in tweet and tweet['retweeted_status']['id_str'] == '1238513167573147648'):
						self.assertFalse(text.endswith('…'))
