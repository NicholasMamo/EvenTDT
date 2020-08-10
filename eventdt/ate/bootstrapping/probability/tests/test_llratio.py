"""
Test the functionality of the log-likelihood ratio bootstrapper.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

import ate
from ate.bootstrapping.probability import LogLikelihoodRatioBootstrapper
from ate.stat import probability

class TestLogLikelihoodRatioBootstrapper(unittest.TestCase):
	"""
	Test the functionality of the log-likelihood ratio bootstrapper.
	"""

	def test_contingency_table_empty_corpus(self):
		"""
		Test that when creating the contingency table of an empty corpus results in all zeroes.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'empty.json')
		bootstrapper = LogLikelihoodRatioBootstrapper()
		bootstrapper = LogLikelihoodRatioBootstrapper()
		tables = bootstrapper._contingency_table(path, 'a', 'b')
		self.assertEqual(0, sum(tables[('a', 'b')]))

	def test_contingency_table_single_corpus(self):
		"""
		Test that when creating the contingency table from a single corpus, the total of each contingency table adds up to the total number of documents in that corpus.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		bootstrapper = LogLikelihoodRatioBootstrapper()
		tables = bootstrapper._contingency_table(path, 'a', 'b')
		self.assertEqual(ate.total_documents(path), sum(tables[('a', 'b')]))

	def test_contingency_table_multiple_corpora(self):
		"""
		Test that when creating the contingency table from multiple corpora, the total of each contingency table adds up to the total number of documents in all corpora.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
		total = ate.total_documents(paths)
		bootstrapper = LogLikelihoodRatioBootstrapper()
		tables = bootstrapper._contingency_table(paths, 'a', 'b')
		self.assertEqual(total, sum(tables[('a', 'b')]))

	def test_contingency_table_str_seed(self):
		"""
		Test that when creating the contingency table with one `seed`, the contingency table treats it correctly as a string.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		bootstrapper = LogLikelihoodRatioBootstrapper()
		tables = bootstrapper._contingency_table(path, 'yellow', [ 'foul', 'tackl' ])
		self.assertEqual({ ('yellow', 'foul'), ('yellow', 'tackl') }, tables.keys())

	def test_contingency_table_str_candidates(self):
		"""
		Test that when creating the contingency table with one `candidates`, the contingency table treats it correctly as a string.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		bootstrapper = LogLikelihoodRatioBootstrapper()
		tables = bootstrapper._contingency_table(path, [ 'foul', 'tackl' ], 'yellow')
		self.assertEqual({ ('foul', 'yellow'), ('tackl', 'yellow') }, tables.keys())

	def test_contingency_table_list_seed(self):
		"""
		Test that when creating the contingency table with multiple `seed`, the contingency table treats it correctly as a list.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		bootstrapper = LogLikelihoodRatioBootstrapper()
		tables = bootstrapper._contingency_table(path, [ 'yellow', 'red' ], [ 'foul', 'tackl' ])
		self.assertEqual({ ('yellow', 'foul'), ('yellow', 'tackl'),
						   ('red', 'foul'), ('red', 'tackl') },
						 tables.keys())

	def test_contingency_table_list_candidates(self):
		"""
		Test that when creating the contingency table with multiple `candidates`, the contingency table treats it correctly as a list.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		bootstrapper = LogLikelihoodRatioBootstrapper()
		tables = bootstrapper._contingency_table(path, [ 'foul', 'tackl' ], [ 'yellow', 'red' ])
		self.assertEqual({ ('foul', 'yellow'), ('foul', 'red'),
						   ('tackl', 'yellow'), ('tackl', 'red') },
						 tables.keys())

	def test_contingency_table_token_not_found(self):
		"""
		Test that even if a token is not found, a contingency table is created for it.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		total = ate.total_documents(path)
		bootstrapper = LogLikelihoodRatioBootstrapper()
		tables = bootstrapper._contingency_table(path, [ 'foul', 'tackl' ], [ 'superlongword' ])
		self.assertEqual({ ('foul', 'superlongword'), ('tackl', 'superlongword') },
						 tables.keys())
		self.assertTrue(all( total == sum(table) for table in tables.values() ))

	def test_contingency_table_row_total(self):
		"""
		Test that the row totals are correct.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
		bootstrapper = LogLikelihoodRatioBootstrapper()
		tables = bootstrapper._contingency_table(paths, [ 'foul', 'tackl' ], 'yellow')
		counts = { token: len(probability.cached(paths, token)) for token in [ 'foul', 'tackl' ] }
		for pair, table in tables.items():
			expected = counts['foul'] if 'foul' in pair else counts['tackl']
			self.assertEqual(expected, table[0] + table[1])

	def test_contingency_table_column_total(self):
		"""
		Test that the column totals are correct.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
		bootstrapper = LogLikelihoodRatioBootstrapper()
		tables = bootstrapper._contingency_table(paths, [ 'foul', 'tackl' ], [ 'yellow', 'red' ])
		counts = { token: len(probability.cached(paths, token)) for token in [ 'yellow', 'red' ] }
		for pair, table in tables.items():
			expected = counts['yellow'] if 'yellow' in pair else counts['red']
			self.assertEqual(expected, table[0] + table[2])

	def test_contingency_table_totals(self):
		"""
		Test that the contingency table totals add up to the number of documents in the corpora.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
		bootstrapper = LogLikelihoodRatioBootstrapper()
		tables = bootstrapper._contingency_table(paths, [ 'foul', 'tackl' ], [ 'yellow', 'red' ])
		total = ate.total_documents(paths)
		self.assertTrue(all( total == sum(table) for table in tables.values() ))

	def test_contingency_table_joint_count(self):
		"""
		Test that the joint counts are correct.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]

		seed, candidates = [ 'foul', 'tackl' ], 'yellow'
		freq = dict.fromkeys(probability.joint_vocabulary(seed, candidates), 0)
		for corpus in paths:
			with open(corpus, 'r') as f:
				for line in f:
					document = json.loads(line)
					for pair in freq:
						if pair[0] in document['tokens'] and pair[1] in document['tokens']:
							freq[pair] += 1

		bootstrapper = LogLikelihoodRatioBootstrapper()
		tables = bootstrapper._contingency_table(paths, seed, candidates)
		for pair in tables:
			self.assertEqual(freq[pair], tables[pair][0])

	def test_contingency_table_symmetric(self):
		"""
		Test that the contingency table is symmetric, but otherwise all counts are the same.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]

		seed, candidates = [ 'foul', 'tackl' ], 'yellow'
		bootstrapper = LogLikelihoodRatioBootstrapper()
		t1, t2 = bootstrapper._contingency_table(paths, seed, candidates), bootstrapper._contingency_table(paths, candidates, seed)
		for t1, t2 in zip(t1.values(), t2.values()):
			self.assertEqual(t1[0], t2[0])
			self.assertEqual(t1[1], t2[2])
			self.assertEqual(t1[2], t2[1])
			self.assertEqual(t1[3], t2[3])

	def test_contingency_table_cache(self):
		"""
		Test that the contingency table's cache results in the same table as without cache.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]

		seed, candidates = [ 'yellow', 'red' ], [ 'foul', 'tackl' ]
		bootstrapper = LogLikelihoodRatioBootstrapper()
		cached = bootstrapper._contingency_table(paths, seed, candidates, cache=seed)
		not_cached = bootstrapper._contingency_table(paths, seed, candidates)
		self.assertEqual(cached, not_cached)

	def test_contingency_table_example(self):
		"""
		Test the creation of a contingency table from an example corpus.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'example-1.json')

		seed, candidates = 'x', '!y'
		bootstrapper = LogLikelihoodRatioBootstrapper()
		table = list(bootstrapper._contingency_table(path, seed, candidates).values())[0]
		self.assertEqual(3, table[0])
		self.assertEqual(1, table[1])
		self.assertEqual(2, table[2])
		self.assertEqual(14, table[3])

	def test_contingency_table_seed_candidates_cached(self):
		"""
		Test that when both `seed` and `candidates` are cached, their document frequencies are created immediately.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')

		seed, candidates = 'x', 'y'
		bootstrapper = LogLikelihoodRatioBootstrapper()
		table = bootstrapper._contingency_table(path, seed, candidates, cache=[ seed, candidates ])
		self.assertTrue(table)
