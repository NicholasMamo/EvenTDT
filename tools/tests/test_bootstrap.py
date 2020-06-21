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

	def test_load_candidates_all_words(self):
		"""
		Test that when loading the candidates words, all words are returned.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'candidates.txt')
		candidates = bootstrap.load_candidates(file)

		"""
		Assert that the correct number of candidates words are loaded.
		"""
		self.assertEqual(500, len(candidates))

		"""
		Load each candidates set separately and ensure it has been loaded.
		"""
		with open(file, 'r') as f:
			for word in f:
				self.assertTrue(word.strip() in candidates)

	def test_load_candidates_list(self):
		"""
		Test that when loading the candidates words, they are returned as a list.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'candidates.txt')
		candidates = bootstrap.load_candidates(file)

		"""
		Assert that the candidates list is returned as a list.
		"""
		self.assertEqual(list, type(candidates))

	def test_load_candidates_no_newlines(self):
		"""
		Test that when loading the candidates words, the newline symbol is removed.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'candidates.txt')
		candidates = bootstrap.load_candidates(file)

		"""
		Assert that the candidates list is returned as a list.
		"""
		self.assertTrue(all( '\n' not in word for word in candidates ))

	def test_generate_candidates_cutoff(self):
		"""
		Test that when generating candidates, the cutoff is respected.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'tokenized.json')

		"""
		Assert that the number of candidates is correct.
		"""
		candidates = bootstrap.generate_candidates(file, cutoff=100)
		self.assertEqual(100, len(candidates))

		candidates = bootstrap.generate_candidates(file, cutoff=250)
		self.assertEqual(250, len(candidates))

	def test_generate_candidates_words_only(self):
		"""
		Test that when generating candidates, only words are returned.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'tokenized.json')

		"""
		Assert that all items in the list are words.
		"""
		candidates = bootstrap.generate_candidates(file, cutoff=100)
		self.assertEqual(list, type(candidates))
		self.assertTrue(all(str == type(word) for word in candidates))

	def test_generate_candidates(self):
		"""
		Test that when generating candidates, the returned candidates make sense
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'tokenized.json')

		"""
		Assert that all items in the list are words.
		"""
		candidates = bootstrap.generate_candidates(file, cutoff=500)
		self.assertTrue('goal' in candidates)

	def test_filter_candidates_empty_seed_bootstrapped(self):
		"""
		Test that when empty seed set and bootstrapped keywords are given, the original dictionary is returned.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'seed.txt')
		seed = bootstrap.load_seed(file)
		candidates = { word: i for i, word in enumerate(seed) }

		self.assertEqual(candidates, bootstrap.filter_candidates(candidates, [ ], [ ]))

	def test_filter_candidates_copy(self):
		"""
		Test that the filtered candidate dictionary is a copy.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'seed.txt')
		seed = bootstrap.load_seed(file)
		candidates = { word: i for i, word in enumerate(seed) }

		filtered = bootstrap.filter_candidates(candidates, seed, [ ])
		self.assertEqual(30, len(candidates))
		self.assertEqual(0, len(filtered))

	def test_filter_candidates_all(self):
		"""
		Test that when all candidates are filtered, an empty dictionary is returned.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'seed.txt')
		seed = bootstrap.load_seed(file)
		candidates = { word: i for i, word in enumerate(seed) }

		filtered = bootstrap.filter_candidates(candidates, seed, [ ])
		self.assertEqual({ }, filtered)

	def test_filter_candidates_seed(self):
		"""
		Test filtering by the seed set.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'seed.txt')
		seed = bootstrap.load_seed(file)
		candidates = { word: i for i, word in enumerate(seed) }

		filtered = bootstrap.filter_candidates(candidates, seed[:10], [ ])
		self.assertTrue(all( word not in filtered for word in seed[:10] ))

	def test_filter_candidates_bootstrapped(self):
		"""
		Test filtering by the bootstrapped keywords.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'seed.txt')
		seed = bootstrap.load_seed(file)
		candidates = { word: i for i, word in enumerate(seed) }

		filtered = bootstrap.filter_candidates(candidates, [ ], seed[:10])
		self.assertTrue(all( word not in filtered for word in seed[:10] ))

	def test_filter_candidates_combination(self):
		"""
		Test filtering by the seed set and bootstrapped keywords.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'seed.txt')
		seed = bootstrap.load_seed(file)
		candidates = { word: i for i, word in enumerate(seed) }

		filtered = bootstrap.filter_candidates(candidates, seed[:10], seed[10:20])
		self.assertTrue(all( word not in filtered for word in seed[:20] ))

	def test_filter_candidates_scores_retained(self):
		"""
		Test that when filtering candidates, the scores are retained.
		"""

		file = os.path.join(os.path.dirname(__file__), 'corpora', 'seed.txt')
		seed = bootstrap.load_seed(file)
		candidates = { word: i for i, word in enumerate(seed) }

		filtered = bootstrap.filter_candidates(candidates, seed[:10], [ ])
		for i, word in enumerate(seed[10:]):
			self.assertEqual(i + 10, filtered[word])

	def test_update_scores_lower(self):
		"""
		Test that when updating the scores, lower scores are not considered.
		"""

		candidates = { 'ff': 2 }
		scores = { ('goal', 'ff'): 1 }
		self.assertEqual(candidates, bootstrap.update_scores(candidates, scores))

	def test_update_scores_higher(self):
		"""
		Test that when updating the scores, higher scores replace lower scores.
		"""

		candidates = { 'ff': 2 }
		scores = { ('goal', 'ff'): 3 }
		self.assertEqual({ 'ff': 3 }, bootstrap.update_scores(candidates, scores))

	def test_update_scores_same(self):
		"""
		Test that when updating the scores, scores where the seed and candidate words are the same are ignored.
		"""

		candidates = { 'ff': 2 }
		scores = { ('ff', 'ff'): 3 }
		self.assertEqual(candidates, bootstrap.update_scores(candidates, scores))

	def test_update_scores_missing_candidate(self):
		"""
		Test that when updating the scores, new terms are added to the candidate list.
		"""

		candidates = { 'ff': 2 }
		scores = { ('goal', 'wtf'): 3 }
		self.assertEqual({ 'ff': 2, 'wtf': 3 }, bootstrap.update_scores(candidates, scores))

	def test_update_scores_missing_score(self):
		"""
		Test that when updating the scores, existing terms without a new score are not touched
		"""

		candidates = { 'ff': 2 }
		scores = { ('goal', 'wtf'): 3 }
		self.assertEqual({ 'ff': 2, 'wtf': 3 }, bootstrap.update_scores(candidates, scores))

	def test_update_scores_empty_candidates(self):
		"""
		Test that when updating the scores of no candidates, the new scores are returned.
		"""

		candidates = { }
		scores = { ('goal', 'wtf'): 3 }
		self.assertEqual({ 'wtf': 3 }, bootstrap.update_scores(candidates, scores))

	def test_update_scores_empty_scores(self):
		"""
		Test that when updating the scores with no scores, the candidates are returned.
		"""

		candidates = { 'ff': 2 }
		scores = { }
		self.assertEqual(candidates, bootstrap.update_scores(candidates, scores))

	def test_update_scores_copy(self):
		"""
		Test that when updating the scores, the original candidates are not changed.
		"""

		candidates = { 'ff': 2 }
		scores = { ('goal', 'ff'): 3 }
		updated = bootstrap.update_scores(candidates, scores)
		self.assertEqual({ 'ff': 2 }, candidates)
		self.assertEqual({ 'ff': 3 }, updated)
