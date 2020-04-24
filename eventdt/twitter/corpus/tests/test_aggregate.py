"""
Test the functionality of the aggregation functions.
"""

import json
import os
import sys
import unittest

from datetime import datetime

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from twitter.corpus.aggregate import *

class TestAggregate(unittest.TestCase):
	"""
	Test the functionality of the aggregation functions.
	"""

	def test_volume_empty_bin(self):
		"""
		Test that the volume of an empty bin is 0.
		"""

		self.assertEqual(0, volume([ ]))

	def test_volume_all(self):
		"""
		Test that the overall volume is the length of the bin.
		"""

		self.assertEqual(10, volume(range(0, 10)))

	def test_volume_track(self):
		"""
		Test that the volume of a tracked keyword looks in the document's dimensions.
		"""

		self.assertEqual(1, volume([ Document('a', { 'b': 1 }) ], track='b'))

	def test_volume_track_no_matches(self):
		"""
		Test that the volume of a tracked keyword returns 0 if there are no matches.
		"""

		self.assertEqual(0, volume([ Document('a', { 'b': 1 }) ], track='a'))

	def test_volume_track_matches(self):
		"""
		Test that the volume of a tracked keyword returns the number of matches.
		"""

		self.assertEqual(1, volume([ Document('a', { 'b': 1 }),
									 Document('a', { 'c': 1 }) ], track='b'))
