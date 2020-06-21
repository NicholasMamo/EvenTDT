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

import bootstrap

class TestBootstrap(unittest.TestCase):
	"""
	Test the functionality of the bootstrap tool.
	"""

	def test_load_seed_all_words(self):
		"""
		Test that when loading the seed words, all words are returned.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'seed.txt')
		seed = bootstrap.load_seed(file)

		"""
		Assert that the correct number of seed words are loaded.
		"""
		self.assertEqual(30, len(seed))

		"""
		Load each seed set separately and ensure it has been loaded.
		"""
		with open(file, 'r') as f:
			for word in f:
				self.assertTrue(word.strip() in seed)

	def test_load_seed_list(self):
		"""
		Test that when loading the seed words, they are returned as a list.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'seed.txt')
		seed = bootstrap.load_seed(file)

		"""
		Assert that the seed list is returned as a list.
		"""
		self.assertEqual(list, type(seed))

	def test_load_seed_no_newlines(self):
		"""
		Test that when loading the seed words, the newline symbol is removed.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'seed.txt')
		seed = bootstrap.load_seed(file)

		"""
		Assert that the seed list is returned as a list.
		"""
		self.assertTrue(all( '\n' not in word for word in seed ))
