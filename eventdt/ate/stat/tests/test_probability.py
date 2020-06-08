"""
Test the functionality of the probability functions.
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
from ate.stat import probability
from ate.stat.probability import *

class TestProbability(unittest.TestCase):
	"""
	Test the functionality of the probability functions.
	"""

	def test_probability_empty_corpus(self):
		"""
		Test that computing the probability on an empty corpus returns an empty probability dictionary.
		"""

		path = os.path.join(os.path.dirname(__file__), 'empty.json')
		self.assertEqual({ }, p(path))

	def test_probability_sums_one(self):
		"""
		Test that the probability sums up to one.
		"""

		path = os.path.join(os.path.dirname(__file__), 'c1.json')
		self.assertEqual(1, round(sum(p(path).values()), 10))

	def test_probability_corpora_sums_one(self):
		"""
		Test that the probability from multiple corpora sums up to one.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		self.assertEqual(1, round(sum(p(paths).values()), 10))

	def test_probability_nonzero(self):
		"""
		Test that all probabilities are non-zero.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		self.assertTrue(all( probability > 0 for probability in p(paths).values() ))

	def test_probability_less_than_one(self):
		"""
		Test that all probabilities are less than or equal to one.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		self.assertTrue(all( probability <= 1 for probability in p(paths).values() ))

	def test_probability_all_vocabulary(self):
		"""
		Test that probability is computed for the entire vocabulary.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]

		vocabulary = [ ]
		for path in paths:
			with open(path, 'r') as f:
				for line in f:
					vocabulary.extend(json.loads(line)['tokens'])

		self.assertEqual(set(vocabulary), set(p(paths).keys()))

	def test_probability_token(self):
		"""
		Test that when computing the probability of one token, its probability is correct.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]

		"""
		Compute the probability for all tokens in the corpora first.
		"""
		probability = p(paths)

		"""
		Compute the probability for one token.
		"""
		subset = p(paths, focus='yellow')
		self.assertEqual(1, len(subset))
		self.assertEqual({ 'yellow' }, set(subset.keys()))
		self.assertLess(0, sum(subset.values()))
		self.assertGreater(1, sum(subset.values()))
		for token in subset:
			self.assertEqual(probability[token], subset[token])

	def test_probability_multiple_tokens(self):
		"""
		Test that when computing the probability of multiple tokens, their probabilities are correct.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]

		"""
		Compute the probability for all tokens in the corpora first.
		"""
		probability = p(paths)

		"""
		Compute the probability for a few tokens.
		"""
		subset = p(paths, focus=[ 'yellow', 'card' ])
		self.assertEqual(2, len(subset))
		self.assertEqual({ 'yellow', 'card' }, set(subset.keys()))
		self.assertLess(0, sum(subset.values()))
		self.assertGreater(1, sum(subset.values()))
		for token in subset:
			self.assertEqual(probability[token], subset[token])

	def test_probability_joint(self):
		"""
		Test that when computing the joint probability, they are returned correctly.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]

		"""
		Compute the probability for all tokens in the corpora first.
		"""
		probability = p(paths)

		"""
		Compute the probability for a few tokens.
		"""
		subset = p(paths, focus=( 'yellow', 'card' ))
		self.assertEqual(1, len(subset))
		self.assertEqual({ ('yellow', 'card') }, set(subset.keys()))
		self.assertLess(0, sum(subset.values()))
		self.assertGreater(1, sum(subset.values()))

		"""
		Ensure that the total probability for the tuple's components exceeds or is equal to the joint probability.
		"""
		for tuple in subset:
			total_probability = sum( probability[token] for token in tuple )
			self.assertGreater(total_probability, subset[tuple])

	def test_probability_multiple_joint(self):
		"""
		Test that when computing the joint probability for multiple tuples, they are returned correctly.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]

		"""
		Compute the probability for all tokens in the corpora first.
		"""
		probability = p(paths)

		"""
		Compute the probability for a few tokens.
		"""
		subset = p(paths, focus=[ ( 'yellow', 'card' ), ( 'free', 'kick' ) ])
		self.assertEqual(2, len(subset))
		self.assertEqual({ ('yellow', 'card'), ( 'free', 'kick' ) }, set(subset.keys()))
		self.assertLess(0, sum(subset.values()))
		self.assertGreater(1, sum(subset.values()))

		"""
		Ensure that the total probability for the tuple's components exceeds or is equal to the joint probability.
		"""
		for tuple in subset:
			total_probability = sum( probability[token] for token in tuple )
			self.assertGreater(total_probability, subset[tuple])

	def test_probability_token_joint_mix(self):
		"""
		Test that when computing the probability for a mix of tuples and tokens, they are returned correctly.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]

		"""
		Compute the probability for all tokens in the corpora first.
		"""
		probability = p(paths)

		"""
		Compute the probability for a few tokens.
		"""
		subset = p(paths, focus=[ ( 'yellow', 'card' ), 'kick' ])
		self.assertEqual(2, len(subset))
		self.assertEqual({ ('yellow', 'card'), 'kick' }, set(subset.keys()))
		self.assertLess(0, sum(subset.values()))
		self.assertGreater(1, sum(subset.values()))

		self.assertEqual(probability['kick'], subset['kick'])

		"""
		Ensure that the total probability for the tuple's components exceeds or is equal to the joint probability.
		"""
		for tokens in subset:
			if type(tokens) is str:
				continue

			total_probability = sum( probability[token] for token in tokens )
			self.assertGreater(total_probability, subset[tokens])

	def test_probability_missing_token(self):
		"""
		Test that the probability of a missing token is recorded correctly.
		"""

		path = os.path.join(os.path.dirname(__file__), 'e.json')
		probability = p(path, focus='z')
		self.assertEqual(0, probability['z'])

	def test_probability_missing_tuple(self):
		"""
		Test that the probability of a missing tuple is recorded correctly.
		"""

		path = os.path.join(os.path.dirname(__file__), 'e.json')
		probability = p(path, focus=('x', 'z'))
		self.assertEqual(0, probability[('x', 'z')])

	def test_probability_cache(self):
		"""
		Test that the probability using cache is the same as the probability without cache.
		"""

		path = os.path.join(os.path.dirname(__file__), 'c1.json')
		focus = [ 'yellow', 'card', ('yellow', 'foul') ]
		self.assertEqual(p(path, focus=focus), p(path, focus=focus, cache='yellow'))

	def test_PMI_example(self):
		"""
		Test the PMI calculation using `example from Wikipedia <https://en.wikipedia.org/wiki/Pointwise_mutual_information>`_.
		Note that the results aren't quite the same because the original probabilities don't add up to 1.
		"""

		path = os.path.join(os.path.dirname(__file__), 'e.json')
		vocab = [ '!x', 'x', '!y', 'y', ('!x', '!y'), ('!x', 'y'), ('x', '!y'), ('x', 'y') ]
		pmi = PMI(path, x=[ '!x', 'x' ], y=[ '!y', 'y' ], base=2)

		prob = p(path, focus=vocab)
		self.assertEqual(probability._pmi(prob, '!x', '!y', 2), pmi[('!x', '!y')])
		self.assertEqual(probability._pmi(prob, '!x', 'y', 2), pmi[('!x', 'y')])
		self.assertEqual(probability._pmi(prob, 'x', '!y', 2), pmi[('x', '!y')])
		self.assertEqual(probability._pmi(prob, 'x', 'y', 2), pmi[('x', 'y')])

	def test_PMI_no_x(self):
		"""
		Text that when the `x` is not given, the entire vocabulary is used instead.
		"""

		path = os.path.join(os.path.dirname(__file__), 'e.json')
		pmi = PMI(path, x=None, y=[ '!y', 'y' ])
		self.assertEqual({ ('!x', '!y'), ('!x', 'y'),
		 				   ('x', '!y'), ('x', 'y'),
		 				   ('!y', '!y'), ('!y', 'y'),
		 				   ('y', '!y'), ('y', 'y') },
						 set(pmi.keys()))

		vocab = [ '!x', 'x', '!y', 'y', ('!x', '!y'), ('!x', 'y'), ('x', '!y'), ('x', 'y') ]
		prob = p(path, focus=vocab)
		self.assertEqual(probability._pmi(prob, '!x', '!y', 2), pmi[('!x', '!y')])
		self.assertEqual(probability._pmi(prob, '!x', 'y', 2), pmi[('!x', 'y')])
		self.assertEqual(probability._pmi(prob, 'x', '!y', 2), pmi[('x', '!y')])
		self.assertEqual(probability._pmi(prob, 'x', 'y', 2), pmi[('x', 'y')])

	def test_PMI_no_y(self):
		"""
		Text that when the `y` is not given, the entire vocabulary is used instead.
		"""

		path = os.path.join(os.path.dirname(__file__), 'e.json')
		pmi = PMI(path, x=[ '!x', 'x' ], y=None)
		self.assertEqual({ ('!x', '!x'), ('!x', 'x'),
		 				   ('x', '!x'), ('x', 'x'),
		 				   ('!x', '!y'), ('!x', 'y'),
				   		   ('x', '!y'), ('x', 'y'), },
						 set(pmi.keys()))

		vocab = [ '!x', 'x', '!y', 'y', ('!x', '!y'), ('!x', 'y'), ('x', '!y'), ('x', 'y') ]
		prob = p(path, focus=vocab)
		self.assertEqual(probability._pmi(prob, '!x', '!y', 2), pmi[('!x', '!y')])
		self.assertEqual(probability._pmi(prob, '!x', 'y', 2), pmi[('!x', 'y')])
		self.assertEqual(probability._pmi(prob, 'x', '!y', 2), pmi[('x', '!y')])
		self.assertEqual(probability._pmi(prob, 'x', 'y', 2), pmi[('x', 'y')])

	def test_PMI_no_x_y(self):
		"""
		Text that when the `x` and `y` are not given, the entire vocabulary is used instead.
		"""

		path = os.path.join(os.path.dirname(__file__), 'e.json')
		pmi = PMI(path, x=None, y=None)
		self.assertEqual({ ('!x', '!x'), ('!x', 'x'),
		 				   ('x', '!x'), ('x', 'x'),
		 				   ('!x', '!y'), ('!x', 'y'),
				   		   ('x', '!y'), ('x', 'y'),
						   ('!y', '!x'), ('!y', 'x'),
   		 				   ('y', '!x'), ('y', 'x'),
   		 				   ('!y', '!y'), ('!y', 'y'),
   				   		   ('y', '!y'), ('y', 'y'), },
						 set(pmi.keys()))

		vocab = [ '!x', 'x', '!y', 'y', ('!x', '!y'), ('!x', 'y'), ('x', '!y'), ('x', 'y') ]
		prob = p(path, focus=vocab)
		self.assertEqual(probability._pmi(prob, '!x', '!y', 2), pmi[('!x', '!y')])
		self.assertEqual(probability._pmi(prob, '!x', 'y', 2), pmi[('!x', 'y')])
		self.assertEqual(probability._pmi(prob, 'x', '!y', 2), pmi[('x', '!y')])
		self.assertEqual(probability._pmi(prob, 'x', 'y', 2), pmi[('x', 'y')])

	def test_pmi_zero_x(self):
		"""
		Test that when calculating the PMI and `x` has a probability of 0, 0 is returned.
		"""

		prob = { 'x': 0, 'y': 0.2, ('x', 'y'): 0.1 }
		self.assertEqual(0, probability._pmi(prob, 'x', 'y', base=2))

	def test_pmi_zero_y(self):
		"""
		Test that when calculating the PMI and `y` has a probability of 0, 0 is returned.
		"""

		prob = { 'x': 0.2, 'y': 0, ('x', 'y'): 0.1 }
		self.assertEqual(0, probability._pmi(prob, 'x', 'y', base=2))

	def test_pmi_zero_joint(self):
		"""
		Test that when calculating the PMI and the joint probability of `x` and `y` is 0, 0 is returned.
		"""

		prob = { 'x': 0.3, 'y': 0.2, ('x', 'y'): 0 }
		self.assertEqual(0, probability._pmi(prob, 'x', 'y', base=2))

	def test_pmi_example(self):
		"""
		Test the PMI calculation using `example from Wikipedia <https://en.wikipedia.org/wiki/Pointwise_mutual_information>`_.
		"""

		prob = {
			'!x': 0.8,
			'x' : 0.2,
			'!y': 0.25,
			'y' : 0.75,

			('!x', '!y'): 0.1,
			('!x', 'y') : 0.7,
			('x', '!y') : 0.15,
			('x', 'y')  : 0.05,
		}

		self.assertEqual(-1, probability._pmi(prob, '!x', '!y', base=2))
		self.assertEqual(0.222392, round(probability._pmi(prob, '!x', 'y', base=2), 6))
		self.assertEqual(1.584963, round(probability._pmi(prob, 'x', '!y', base=2), 6))
		self.assertEqual(-1.584963, round(probability._pmi(prob, 'x', 'y', base=2), 6))

	def test_pmi_example_symmetric(self):
		"""
		Test that the PMI calculation is symmetric using `example from Wikipedia <https://en.wikipedia.org/wiki/Pointwise_mutual_information>`_.
		"""

		prob = {
			'!x': 0.8,
			'x' : 0.2,
			'!y': 0.25,
			'y' : 0.75,

			('!y', '!x'): 0.1,
			('y', '!x') : 0.7,
			('!y', 'x') : 0.15,
			('y', 'x')  : 0.05,
		}

		self.assertEqual(-1, probability._pmi(prob, '!y', '!x', base=2))
		self.assertEqual(0.222392, round(probability._pmi(prob, 'y', '!x', base=2), 6))
		self.assertEqual(1.584963, round(probability._pmi(prob, '!y', 'x', base=2), 6))
		self.assertEqual(-1.584963, round(probability._pmi(prob, 'y', 'x', base=2), 6))

	def test_CHI_empty_corpus(self):
		"""
		Test that when calculating the chi-square statistic on an empty corpus, all statistics are zero.
		"""

		path = os.path.join(os.path.dirname(__file__), 'empty.json')
		x, y = [ 'yellow' ], [ 'foul', 'tackl' ]
		chi = probability.CHI(path, x, y)
		self.assertTrue(all( 0 == value for value in chi.values() ))

	def test_CHI_str_x(self):
		"""
		Test that when `x` is a string, it is treated as such.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
				  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		x, y = 'yellow', [ 'foul', 'tackl' ]
		chi = probability.CHI(paths, x, y)
		self.assertTrue(('yellow', 'foul') in chi)
		self.assertTrue(('yellow', 'tackl') in chi)

	def test_CHI_str_y(self):
		"""
		Test that when `y` is a string, it is treated as such.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
				  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		x, y = [ 'foul', 'tackl' ], 'yellow'
		chi = probability.CHI(paths, x, y)
		self.assertTrue(('foul', 'yellow') in chi)
		self.assertTrue(('tackl', 'yellow') in chi)

	def test_CHI_list_x(self):
		"""
		Test that when `x` is a list, it is treated as such.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
				  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		x, y = [ 'foul', 'tackl' ], 'yellow'
		chi = probability.CHI(paths, x, y)
		self.assertTrue(('foul', 'yellow') in chi)
		self.assertTrue(('tackl', 'yellow') in chi)

	def test_CHI_list_y(self):
		"""
		Test that when `y` is a list, it is treated as such.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
				  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		x, y = 'yellow', [ 'foul', 'tackl' ]
		chi = probability.CHI(paths, x, y)
		self.assertTrue(('yellow', 'foul') in chi)
		self.assertTrue(('yellow', 'tackl') in chi)

	def test_CHI_str_x_y(self):
		"""
		Test that when `x` and `y` are strings, only one pair is returned.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
				  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		x, y = 'yellow', 'foul'
		chi = probability.CHI(paths, x, y)
		self.assertEqual({ ('yellow', 'foul') }, set(chi.keys()))

	def test_CHI_list_x_y(self):
		"""
		Test that when `x` and `y` are lists, their cross-product is returned.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
				  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		x, y = [ 'yellow', 'red' ], [ 'foul', 'tackl' ]
		chi = probability.CHI(paths, x, y)
		self.assertEqual({ ('yellow', 'foul'), ('yellow', 'tackl'),
		 				   ('red', 'foul'), ('red', 'tackl') },
						 set(chi.keys()))

	def test_CHI_nonexisting_word(self):
		"""
		Test that non-existing words are also included in the chi-statistic.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
				  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		x, y = 'yellow', 'superlongword'
		chi = probability.CHI(paths, x, y)
		self.assertTrue(('yellow', 'superlongword') in chi)
		self.assertEqual(0, chi[('yellow', 'superlongword')])

	def test_CHI_example(self):
		"""
		Test with an example chi-square value.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
				  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		x, y = [ 'yellow', 'shoot' ], [ 'foul', 'tackl', 'save' ]
		chi = probability.CHI(paths, x, y)
		self.assertGreater(chi[('yellow', 'tackl')], chi['shoot', 'tackl'])
		self.assertGreater(chi[('yellow', 'foul')], chi['shoot', 'foul'])
		self.assertGreater(chi[('shoot', 'save')], chi['yellow', 'save'])

	def test_contingency_table_empty_corpus(self):
		"""
		Test that when creating the contingency table of an empty corpus results in all zeroes.
		"""

		path = os.path.join(os.path.dirname(__file__), 'empty.json')
		tables = probability._contingency_table(path, 'a', 'b')
		self.assertEqual(0, sum(tables[('a', 'b')]))

	def test_contingency_table_single_corpus(self):
		"""
		Test that when creating the contingency table from a single corpus, the total of each contingency table adds up to the total number of documents in that corpus.
		"""

		path = os.path.join(os.path.dirname(__file__), 'c1.json')
		tables = probability._contingency_table(path, 'a', 'b')
		self.assertEqual(ate.total_documents(path), sum(tables[('a', 'b')]))

	def test_contingency_table_multiple_corpora(self):
		"""
		Test that when creating the contingency table from multiple corpora, the total of each contingency table adds up to the total number of documents in all corpora.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		total = ate.total_documents(paths)
		tables = probability._contingency_table(paths, 'a', 'b')
		self.assertEqual(total, sum(tables[('a', 'b')]))

	def test_contingency_table_str_x(self):
		"""
		Test that when creating the contingency table with one `x`, the contingency table treats it correctly as a string.
		"""

		path = os.path.join(os.path.dirname(__file__), 'c1.json')
		tables = probability._contingency_table(path, 'yellow', [ 'foul', 'tackl' ])
		self.assertEqual({ ('yellow', 'foul'), ('yellow', 'tackl') }, tables.keys())

	def test_contingency_table_str_y(self):
		"""
		Test that when creating the contingency table with one `y`, the contingency table treats it correctly as a string.
		"""

		path = os.path.join(os.path.dirname(__file__), 'c1.json')
		tables = probability._contingency_table(path, [ 'foul', 'tackl' ], 'yellow')
		self.assertEqual({ ('foul', 'yellow'), ('tackl', 'yellow') }, tables.keys())

	def test_contingency_table_list_x(self):
		"""
		Test that when creating the contingency table with multiple `x`, the contingency table treats it correctly as a list.
		"""

		path = os.path.join(os.path.dirname(__file__), 'c1.json')
		tables = probability._contingency_table(path, [ 'yellow', 'red' ], [ 'foul', 'tackl' ])
		self.assertEqual({ ('yellow', 'foul'), ('yellow', 'tackl'),
						   ('red', 'foul'), ('red', 'tackl') },
						 tables.keys())

	def test_contingency_table_list_y(self):
		"""
		Test that when creating the contingency table with multiple `y`, the contingency table treats it correctly as a list.
		"""

		path = os.path.join(os.path.dirname(__file__), 'c1.json')
		tables = probability._contingency_table(path, [ 'foul', 'tackl' ], [ 'yellow', 'red' ])
		self.assertEqual({ ('foul', 'yellow'), ('foul', 'red'),
						   ('tackl', 'yellow'), ('tackl', 'red') },
						 tables.keys())

	def test_contingency_table_token_not_found(self):
		"""
		Test that even if a token is not found, a contingency table is created for it.
		"""

		path = os.path.join(os.path.dirname(__file__), 'c1.json')
		total = ate.total_documents(path)
		tables = probability._contingency_table(path, [ 'foul', 'tackl' ], [ 'superlongword' ])
		self.assertEqual({ ('foul', 'superlongword'), ('tackl', 'superlongword') },
						 tables.keys())
		self.assertTrue(all( total == sum(table) for table in tables.values() ))

	def test_contingency_table_row_total(self):
		"""
		Test that the row totals are correct.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		tables = probability._contingency_table(paths, [ 'foul', 'tackl' ], 'yellow')
		counts = { token: len(probability._cache(paths, token)) for token in [ 'foul', 'tackl' ] }
		for pair, table in tables.items():
			expected = counts['foul'] if 'foul' in pair else counts['tackl']
			self.assertEqual(expected, table[0] + table[1])

	def test_contingency_table_column_total(self):
		"""
		Test that the column totals are correct.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		tables = probability._contingency_table(paths, [ 'foul', 'tackl' ], [ 'yellow', 'red' ])
		counts = { token: len(probability._cache(paths, token)) for token in [ 'yellow', 'red' ] }
		for pair, table in tables.items():
			expected = counts['yellow'] if 'yellow' in pair else counts['red']
			self.assertEqual(expected, table[0] + table[2])

	def test_contingency_table_totals(self):
		"""
		Test that the contingency table totals add up to the number of documents in the corpora.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		tables = probability._contingency_table(paths, [ 'foul', 'tackl' ], [ 'yellow', 'red' ])
		total = ate.total_documents(paths)
		self.assertTrue(all( total == sum(table) for table in tables.values() ))

	def test_contingency_table_joint_count(self):
		"""
		Test that the joint counts are correct.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]

		x, y = [ 'foul', 'tackl' ], 'yellow'
		freq = dict.fromkeys(probability.joint_vocabulary(x, y), 0)
		for corpus in paths:
			with open(corpus, 'r') as f:
				for line in f:
					document = json.loads(line)
					for pair in freq:
						if pair[0] in document['tokens'] and pair[1] in document['tokens']:
							freq[pair] += 1

		tables = probability._contingency_table(paths, x, y)
		for pair in tables:
			self.assertEqual(freq[pair], tables[pair][0])

	def test_contingency_table_symmetric(self):
		"""
		Test that the contingency table is symmetric, but otherwise all counts are the same.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]

		x, y = [ 'foul', 'tackl' ], 'yellow'
		t1, t2 = probability._contingency_table(paths, x, y), probability._contingency_table(paths, y, x)
		for t1, t2 in zip(t1.values(), t2.values()):
			self.assertEqual(t1[0], t2[0])
			self.assertEqual(t1[1], t2[2])
			self.assertEqual(t1[2], t2[1])
			self.assertEqual(t1[3], t2[3])

	def test_contingency_table_cache(self):
		"""
		Test that the contingency table's cache results in the same table as without cache.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]

		x, y = [ 'yellow', 'red' ], [ 'foul', 'tackl' ]
		cached = probability._contingency_table(paths, x, y, cache=x)
		not_cached = probability._contingency_table(paths, x, y)
		self.assertEqual(cached, not_cached)

	def test_contingency_table_example(self):
		"""
		Test the creation of a contingency table from an example corpus.
		"""

		path = os.path.join(os.path.dirname(__file__), 'e.json')

		x, y = 'x', '!y'
		table = list(probability._contingency_table(path, x, y).values())[0]
		self.assertEqual(3, table[0])
		self.assertEqual(1, table[1])
		self.assertEqual(2, table[2])
		self.assertEqual(14, table[3])

	def test_chi(self):
		"""
		Test the chi-square calculation.
		"""

		table = (600, 200, 300, 1000)
		self.assertEqual(545.1923, round(probability._chi(table), 4))

		table = (30, 20, 331, 3218)
		self.assertEqual(140.2925, round(probability._chi(table), 4))

	def test_chi_empty(self):
		"""
		Test that the chi-square statistic of an empty table is 0.
		"""

		table = (0, 0, 0, 0)
		self.assertEqual(0, probability._chi(table))

	def test_chi_empty_combinations(self):
		"""
		Test that the chi-square statistic of a table that is not empty, except for a few combinations, is 0.
		"""

		table = (0, 1, 0, 1) # A + C = 0
		self.assertEqual(0, probability._chi(table))

		table = (1, 0, 1, 0) # B + D = 0
		self.assertEqual(0, probability._chi(table))

		table = (0, 0, 1, 1) # A + B = 0
		self.assertEqual(0, probability._chi(table))

		table = (1, 1, 0, 0) # C + D = 0
		self.assertEqual(0, probability._chi(table))

		table = (1, 0, 0, 1) # B + C = 0
		self.assertLess(0, probability._chi(table))

		table = (0, 1, 1, 0) # A + D = 0
		self.assertLess(0, probability._chi(table))

	def test_cache_invalid_token(self):
		"""
		Test that when caching with a token that does not appear in the corpora, an empty list is returned.
		"""

		path = os.path.join(os.path.dirname(__file__), 'e.json')
		cache = probability._cache(path, 'yellow')
		self.assertFalse(cache)

	def test_cache_empty_corpus(self):
		"""
		Test that generating the cache from an empty corpus returns an empty list of documents.
		"""

		path = os.path.join(os.path.dirname(__file__), 'empty.json')
		cache = probability._cache(path, 'yellow')
		self.assertFalse(cache)

	def test_cache_one_corpus(self):
		"""
		Test that generating the cache from one corpus returns only the documents from that corpus.
		"""

		path = os.path.join(os.path.dirname(__file__), 'c1.json')
		cache = probability._cache(path, 'yellow')
		self.assertTrue(cache)

	def test_cache_multiple_corppra(self):
		"""
		Test that generating the cache from multiple corppra returns all the documents from all corpora.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		cache = probability._cache(paths, 'yellow')
		self.assertTrue(cache)

	def test_cache_all_contain_token(self):
		"""
		Test that all documents in the cache contain the given token.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		cache = probability._cache(paths, 'yellow')
		self.assertTrue(all( 'yellow' in document['tokens'] for document in cache ))

	def test_cache_all_valid_retrieved(self):
		"""
		Test that all documents containing the token are retrieved.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'c1.json'),
		 		  os.path.join(os.path.dirname(__file__), 'c2.json') ]
		cache = probability._cache(paths, 'yellow')

		"""
		Go over all the documents in the corpora.
		"""
		read = 0
		for path in paths:
			with open(path, 'r') as f:
				for line in f:
					document = json.loads(line)
					if 'yellow' in document['tokens']:
						self.assertTrue(document in cache)
						read += 1

		self.assertGreater(read, 0)
		self.assertEqual(read, len(cache))

	def test_joint_vocabulary_empty_x_y(self):
		"""
		Test that when `x` and `y` are empty, the joint vocabulary is also empty.
		"""

		self.assertEqual([ ], joint_vocabulary([ ], [ ]))

	def test_joint_vocabulary_empty_x(self):
		"""
		Test that when `x` is empty, the joint vocabulary is also made up of `y`.
		"""

		x = [ ]
		y = [ 'ab', 'cd' ]
		self.assertEqual([ ('ab', ), ('cd', ) ], joint_vocabulary(x, y))

	def test_joint_vocabulary_empty_y(self):
		"""
		Test that when `y` is empty, the joint vocabulary is also made up of `x`.
		"""

		x = [ 'ab', 'cd' ]
		y = [ ]
		self.assertEqual([ ('ab', ), ('cd', ) ], joint_vocabulary(x, y))

	def test_joint_vocabulary_strings_only(self):
		"""
		Test that both `x` and `y` are strings, they are converted into a list.
		"""

		x = 'ab'
		y = 'cd'
		self.assertEqual([ ( 'ab', 'cd' ) ], joint_vocabulary(x, y))

	def test_joint_vocabulary_tuple_only(self):
		"""
		Test that both `x` and `y` are tuples, they are converted into a list.
		"""

		x = ('a', )
		y = ('b', )
		self.assertEqual([ ( 'a', 'b' ) ], joint_vocabulary(x, y))

	def test_joint_vocabulary_multiple_tuple(self):
		"""
		Test that both `x` and `y` are tuples with multiple elements, they are converted into a list.
		"""

		x = ('ab', 'cd' )
		y = ('ef', 'gh' )
		self.assertEqual([ ( 'ab', 'cd', 'ef', 'gh' ) ], joint_vocabulary(x, y))

	def test_joint_vocabulary_cross(self):
		"""
		Test that the cross-product is returned in the joint vocabulary.
		"""

		x = [ 'ab', 'cd' ]
		y = [ 'ef', 'gh' ]
		self.assertEqual([ ( 'ab', 'ef' ), ( 'ab', 'gh' ),
		 				   ( 'cd', 'ef' ), ( 'cd', 'gh' ) ], joint_vocabulary(x, y))

		x = list(string.ascii_letters)
		y = list(string.digits)
		self.assertEqual(len(x) * len(y), len(joint_vocabulary(x, y)))

	def test_joint_vocabulary_empty_x_returns_tuples(self):
		"""
		Test that when creating the joint vocabulary, each item is a tuple when `x` is empty.
		"""

		x = [ ]
		y = list(string.digits)
		self.assertTrue(all(type(item) is tuple for item in joint_vocabulary(x, y)))

	def test_joint_vocabulary_empty_y_returns_tuples(self):
		"""
		Test that when creating the joint vocabulary, each item is a tuple when `y` is empty.
		"""

		x = list(string.ascii_letters)
		y = [ ]
		self.assertTrue(all(type(item) is tuple for item in joint_vocabulary(x, y)))

	def test_joint_vocabulary_returns_tuples(self):
		"""
		Test that when creating the joint vocabulary, each item is a tuple.
		"""

		x = list(string.ascii_letters)
		y = list(string.digits)
		self.assertTrue(all(type(item) is tuple for item in joint_vocabulary(x, y)))
