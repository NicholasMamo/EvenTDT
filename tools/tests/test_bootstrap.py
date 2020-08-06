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
from eventdt.ate.bootstrapping.probability import PMIBootstrapper
from logger import logger

logger.set_logging_level(logger.LogLevel.ERROR)

class TestBootstrap(unittest.TestCase):
	"""
	Test the functionality of the bootstrap tool.
	"""

	def test_bootstrap_list(self):
		"""
		Test that bootstrapping returns a list of keywords.
		"""

		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
		candidates = bootstrap.generate_candidates(files, generate=200)

		bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 1, 5, candidates)
		self.assertEqual(list, type(bootstrapped))

	def test_bootstrap_iterations(self):
		"""
		Test that bootstrapping repeats for a number of iterations.
		"""

		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
		candidates = bootstrap.generate_candidates(files, generate=200)

		bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 1, 1, candidates)
		self.assertEqual(1, len(bootstrapped))
		bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 2, 1, candidates)
		self.assertEqual(2, len(bootstrapped))

	def test_bootstrap_keep(self):
		"""
		Test that bootstrapping keeps only a number of terms at each iteration
		"""

		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
		candidates = bootstrap.generate_candidates(files, generate=200)

		bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 1, 2, candidates)
		self.assertEqual(2, len(bootstrapped))
		bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 2, 2, candidates)
		self.assertEqual(4, len(bootstrapped))

	def test_bootstrap_unique(self):
		"""
		Test that bootstrapping returns a unique list of terms.
		"""

		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
		candidates = bootstrap.generate_candidates(files, generate=200)

		bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 2, 5, candidates)
		self.assertEqual(sorted(list(set(bootstrapped))), sorted(bootstrapped))

	def test_bootstrap(self):
		"""
		Test that bootstrapping results make sense.
		"""

		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
		candidates = bootstrap.generate_candidates(files, generate=200)

		bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 1, 5, candidates)
		self.assertTrue('second' in bootstrapped)
		self.assertTrue('first' in bootstrapped)

	def test_load_seed_all_words(self):
		"""
		Test that when loading the seed words, all words are returned.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
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

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		seed = bootstrap.load_seed(file)

		"""
		Assert that the seed list is returned as a list.
		"""
		self.assertEqual(list, type(seed))

	def test_load_seed_from_terms(self):
		"""
		Test that when loading the seed words from the terms tool's output, they are returned as a list.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json')
		seed = bootstrap.load_seed(file)

		"""
		Assert that the seed list is returned as a list.
		"""
		self.assertEqual(list, type(seed))
		self.assertTrue(len(seed))

	def test_load_seed_no_newlines(self):
		"""
		Test that when loading the seed words, the newline symbol is removed.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		seed = bootstrap.load_seed(file)

		"""
		Assert that the seed list is returned as a list.
		"""
		self.assertTrue(all( '\n' not in word for word in seed ))

	def test_load_seed_max_seed_zero(self):
		"""
		Test that when loading the seed words and keeping zero words, a ValueError is raised.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		self.assertRaises(ValueError, bootstrap.load_seed, file, 0)

	def test_load_seed_max_seed_negative(self):
		"""
		Test that when loading the seed words and keeping negative words, a ValueError is raised.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		self.assertRaises(ValueError, bootstrap.load_seed, file, -1)

	def test_load_seed_max_seed_respected(self):
		"""
		Test that when loading the seed words, the specified number of words are returned.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		seed = bootstrap.load_seed(file, 10)
		self.assertEqual(10, len(seed))

	def test_load_seed_max_seed_top_words(self):
		"""
		Test that when loading the seed words with a cutoff, the top words are returned.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		all = bootstrap.load_seed(file)
		seed = bootstrap.load_seed(file, 10)
		self.assertEqual(all[:10], seed)

	def test_load_seed_max_seed_very_large(self):
		"""
		Test that when loading the seed words with a large cutoff, all words are retained.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		seed = bootstrap.load_seed(file, 50)
		self.assertEqual(30, len(seed))

	def test_load_seed_max_seed_none(self):
		"""
		Test that when loading the seed words with no specified cutoff, all words are retained.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		seed = bootstrap.load_seed(file, None)
		self.assertEqual(30, len(seed))

	def test_load_candidates_all_words(self):
		"""
		Test that when loading the candidates words, all words are returned.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.txt')
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

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.txt')
		candidates = bootstrap.load_candidates(file)

		"""
		Assert that the candidates list is returned as a list.
		"""
		self.assertEqual(list, type(candidates))

	def test_load_candidates_from_terms(self):
		"""
		Test that when loading the candidate words from the terms tool's output, they are returned as a list.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.json')
		candidates = bootstrap.load_candidates(file)

		"""
		Assert that the candidates list is returned as a list.
		"""
		self.assertEqual(list, type(candidates))
		self.assertTrue(len(candidates))

	def test_load_candidates_no_newlines(self):
		"""
		Test that when loading the candidates words, the newline symbol is removed.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.txt')
		candidates = bootstrap.load_candidates(file)

		"""
		Assert that the candidates list is returned as a list.
		"""
		self.assertTrue(all( '\n' not in word for word in candidates ))

	def test_generate_candidates_cutoff(self):
		"""
		Test that when generating candidates, the cutoff is respected.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')

		"""
		Assert that the number of candidates is correct.
		"""
		candidates = bootstrap.generate_candidates(file, generate=100)
		self.assertEqual(100, len(candidates))

		candidates = bootstrap.generate_candidates(file, generate=250)
		self.assertEqual(250, len(candidates))

	def test_generate_candidates_words_only(self):
		"""
		Test that when generating candidates, only words are returned.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')

		"""
		Assert that all items in the list are words.
		"""
		candidates = bootstrap.generate_candidates(file, generate=100)
		self.assertEqual(list, type(candidates))
		self.assertTrue(all(str == type(word) for word in candidates))

	def test_generate_candidates(self):
		"""
		Test that when generating candidates, the returned candidates make sense
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')

		"""
		Assert that all items in the list are words.
		"""
		candidates = bootstrap.generate_candidates(file, generate=500)
		self.assertTrue('goal' in candidates)

	def test_filter_candidates_empty_seed_bootstrapped(self):
		"""
		Test that when empty seed set and bootstrapped keywords are given, the original dictionary is returned.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		seed = bootstrap.load_seed(file)
		candidates = { word: i for i, word in enumerate(seed) }

		self.assertEqual(candidates, bootstrap.filter_candidates(candidates, [ ], [ ]))

	def test_filter_candidates_copy(self):
		"""
		Test that the filtered candidate dictionary is a copy.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		seed = bootstrap.load_seed(file)
		candidates = { word: i for i, word in enumerate(seed) }

		filtered = bootstrap.filter_candidates(candidates, seed, [ ])
		self.assertEqual(30, len(candidates))
		self.assertEqual(0, len(filtered))

	def test_filter_candidates_all(self):
		"""
		Test that when all candidates are filtered, an empty dictionary is returned.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		seed = bootstrap.load_seed(file)
		candidates = { word: i for i, word in enumerate(seed) }

		filtered = bootstrap.filter_candidates(candidates, seed, [ ])
		self.assertEqual({ }, filtered)

	def test_filter_candidates_seed(self):
		"""
		Test filtering by the seed set.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		seed = bootstrap.load_seed(file)
		candidates = { word: i for i, word in enumerate(seed) }

		filtered = bootstrap.filter_candidates(candidates, seed[:10], [ ])
		self.assertTrue(all( word not in filtered for word in seed[:10] ))

	def test_filter_candidates_bootstrapped(self):
		"""
		Test filtering by the bootstrapped keywords.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		seed = bootstrap.load_seed(file)
		candidates = { word: i for i, word in enumerate(seed) }

		filtered = bootstrap.filter_candidates(candidates, [ ], seed[:10])
		self.assertTrue(all( word not in filtered for word in seed[:10] ))

	def test_filter_candidates_combination(self):
		"""
		Test filtering by the seed set and bootstrapped keywords.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
		seed = bootstrap.load_seed(file)
		candidates = { word: i for i, word in enumerate(seed) }

		filtered = bootstrap.filter_candidates(candidates, seed[:10], seed[10:20])
		self.assertTrue(all( word not in filtered for word in seed[:20] ))

	def test_filter_candidates_scores_retained(self):
		"""
		Test that when filtering candidates, the scores are retained.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
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
