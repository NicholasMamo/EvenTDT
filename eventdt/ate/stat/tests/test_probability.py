"""
Test the functionality of the probability functions.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

import probability
from probability import *

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
