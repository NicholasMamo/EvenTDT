"""
Test the functionality of the tweet cleaner.
"""

import asyncio
import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
	sys.path.append(path)

from nlp.cleaners import TweetCleaner

class TestTweetCleaner(unittest.TestCase):
	"""
	Test the implementation of the tweet cleaner.
	"""

	def test_no_configuration_default(self):
		"""
		Test that when no configuration is given, the default configuration is used.
		"""

		cleaner = TweetCleaner()
		self.assertFalse(cleaner.remove_alt_codes)
		self.assertFalse(cleaner.complete_sentences)
		self.assertFalse(cleaner.collapse_new_lines)
		self.assertFalse(cleaner.collapse_whitespaces)

	def test_configuration_saved(self):
		"""
		Test that the configuration given to the tweet cleaner is passed on to the cleaner.
		"""

		cleaner = TweetCleaner(remove_alt_codes=True, complete_sentences=True,
							   collapse_new_lines=True, collapse_whitespaces=True)
		self.assertTrue(cleaner.remove_alt_codes)
		self.assertTrue(cleaner.complete_sentences)
		self.assertTrue(cleaner.collapse_new_lines)
		self.assertTrue(cleaner.collapse_whitespaces)
