"""
Test the functionality of the probability functions.
"""

import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

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
		subset = p(paths, only='yellow')
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
		subset = p(paths, only=[ 'yellow', 'card' ])
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
		subset = p(paths, only=( 'yellow', 'card' ))
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
		subset = p(paths, only=[ ( 'yellow', 'card' ), ( 'free', 'kick' ) ])
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
		subset = p(paths, only=[ ( 'yellow', 'card' ), 'kick' ])
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
