"""
Test the functionality of the tweet package-level functions.
"""

import json
import os
import sys
import unittest

from datetime import datetime

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

import twitter

class TestPackage(unittest.TestCase):
	"""
	Test the functionality of the tweet package-level functions.
	"""

	def test_timestamp_date(self):
		"""
		Test that the timestamp date is the same and correct for all tweets in the corpus.
		"""

		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				date = datetime.fromtimestamp(twitter.extract_timestamp(tweet))
				self.assertEqual(2020, date.year)
				self.assertEqual(3, date.month)
				self.assertEqual(14, date.day)
				self.assertEqual(14, date.hour)
				self.assertTrue(date.minute in range(39, 42))
