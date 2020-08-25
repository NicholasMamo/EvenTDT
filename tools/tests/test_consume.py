"""
Test the functionality of the consume tool.
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

import consume

class TestConsume(unittest.TestCase):
	"""
	Test the functionality of the consume tool.
	"""

	def test_splits_all_words(self):
		"""
		Test that when loading the split tokens, all words are returned.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'consume', 'splits.csv')
		splits = consume.splits(file)

		"""
		Assert that the correct number of split tokens are loaded.
		"""
		self.assertEqual(3, len(splits))
		self.assertEqual([ 'yellow', 'card', 'foul', 'tackl' ], splits[0])
		self.assertEqual([ 'ref', 'refere', 'var' ], splits[1])
		self.assertEqual([ 'goal', 'shot', 'keeper', 'save' ], splits[2])

	def test_splits_list(self):
		"""
		Test that when loading the split tokens, they are returned as a list.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'consume', 'splits.csv')
		splits = consume.splits(file)

		"""
		Assert that the splits list is returned as a list.
		"""
		self.assertEqual(list, type(splits))
		self.assertTrue(all( type(split) is list for split in splits ))

	def test_splits_no_newlines(self):
		"""
		Test that when loading the split tokens, the newline symbol is removed.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'consume', 'splits.csv')
		splits = consume.splits(file)

		"""
		Assert that the splits list is returned as a list.
		"""
		self.assertTrue(all( '\n' not in split for split in splits ))
		self.assertTrue(all( not split[-1].endswith('\n') for split in splits ))

	def test_splits_no_commas(self):
		"""
		Test that when loading the split tokens, there are no commas.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'consume', 'splits.csv')
		splits = consume.splits(file)

		"""
		Assert that the splits list is returned as a list.
		"""
		self.assertTrue(all( ',' not in token for split in splits for token in split ))
