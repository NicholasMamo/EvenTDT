"""
Test the functionality of the PMI bootstrapper.
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
from ate.bootstrapping.probability import PMIBootstrapper
from ate.stat import probability

class TestPMIBootstrapper(unittest.TestCase):
	"""
	Test the functionality of the PMI bootstrapper.
	"""

	def test_bootstrap_example(self):
		"""
		Test the PMI calculation using `example from Wikipedia <https://en.wikipedia.org/wiki/Pointwise_mutual_information>`_.
		Note that the results aren't quite the same because the original probabilities don't add up to 1.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'example-1.json')
		vocab = [ '!x', 'x', '!y', 'y', ('!x', '!y'), ('!x', 'y'), ('x', '!y'), ('x', 'y') ]
		bootstrapper = PMIBootstrapper(base=2)
		pmi = bootstrapper.bootstrap(path, seed=[ '!x', 'x' ], candidates=[ '!y', 'y' ])

		prob = probability.p(path, focus=vocab)
		self.assertEqual(bootstrapper._pmi(prob, '!x', '!y'), pmi[('!x', '!y')])
		self.assertEqual(bootstrapper._pmi(prob, '!x', 'y'), pmi[('!x', 'y')])
		self.assertEqual(bootstrapper._pmi(prob, 'x', '!y'), pmi[('x', '!y')])
		self.assertEqual(bootstrapper._pmi(prob, 'x', 'y'), pmi[('x', 'y')])

	def test_bootstrap_no_seed(self):
		"""
		Test that when the `seed` is not given, the entire vocabulary is used instead.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'example-1.json')
		bootstrapper = PMIBootstrapper(base=2)
		pmi = bootstrapper.bootstrap(path, seed=None, candidates=[ '!y', 'y' ])
		self.assertEqual({ ('!x', '!y'), ('!x', 'y'),
		 				   ('x', '!y'), ('x', 'y'),
		 				   ('!y', '!y'), ('!y', 'y'),
		 				   ('y', '!y'), ('y', 'y') },
						 set(pmi.keys()))

		vocab = [ '!x', 'x', '!y', 'y', ('!x', '!y'), ('!x', 'y'), ('x', '!y'), ('x', 'y') ]
		prob = probability.p(path, focus=vocab)
		self.assertEqual(bootstrapper._pmi(prob, '!x', '!y'), pmi[('!x', '!y')])
		self.assertEqual(bootstrapper._pmi(prob, '!x', 'y'), pmi[('!x', 'y')])
		self.assertEqual(bootstrapper._pmi(prob, 'x', '!y'), pmi[('x', '!y')])
		self.assertEqual(bootstrapper._pmi(prob, 'x', 'y'), pmi[('x', 'y')])

	def test_bootstrap_no_candidates(self):
		"""
		Test that when the `candidates` is not given, the entire vocabulary is used instead.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'example-1.json')
		bootstrapper = PMIBootstrapper(base=2)
		pmi = bootstrapper.bootstrap(path, seed=[ '!x', 'x' ], candidates=None)
		self.assertEqual({ ('!x', '!x'), ('!x', 'x'),
		 				   ('x', '!x'), ('x', 'x'),
		 				   ('!x', '!y'), ('!x', 'y'),
				   		   ('x', '!y'), ('x', 'y'), },
						 set(pmi.keys()))

		vocab = [ '!x', 'x', '!y', 'y', ('!x', '!y'), ('!x', 'y'), ('x', '!y'), ('x', 'y') ]
		prob = probability.p(path, focus=vocab)
		self.assertEqual(bootstrapper._pmi(prob, '!x', '!y'), pmi[('!x', '!y')])
		self.assertEqual(bootstrapper._pmi(prob, '!x', 'y'), pmi[('!x', 'y')])
		self.assertEqual(bootstrapper._pmi(prob, 'x', '!y'), pmi[('x', '!y')])
		self.assertEqual(bootstrapper._pmi(prob, 'x', 'y'), pmi[('x', 'y')])

	def test_bootstrap_no_seed_candidates(self):
		"""
		Test that when the `seed` and `candidates` are not given, the entire vocabulary is used instead.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'example-1.json')
		bootstrapper = PMIBootstrapper(base=2)
		pmi = bootstrapper.bootstrap(path, seed=None, candidates=None)
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
		prob = probability.p(path, focus=vocab)
		self.assertEqual(bootstrapper._pmi(prob, '!x', '!y'), pmi[('!x', '!y')])
		self.assertEqual(bootstrapper._pmi(prob, '!x', 'y'), pmi[('!x', 'y')])
		self.assertEqual(bootstrapper._pmi(prob, 'x', '!y'), pmi[('x', '!y')])
		self.assertEqual(bootstrapper._pmi(prob, 'x', 'y'), pmi[('x', 'y')])

	def test_pmi_zero_x(self):
		"""
		Test that when calculating the PMI and `seed` has a probability of 0, 0 is returned.
		"""

		bootstrapper = PMIBootstrapper(base=2)
		prob = { 'x': 0, 'y': 0.2, ('x', 'y'): 0.1 }
		self.assertEqual(0, bootstrapper._pmi(prob, 'x', 'y'))

	def test_pmi_zero_y(self):
		"""
		Test that when calculating the PMI and `candidates` has a probability of 0, 0 is returned.
		"""

		bootstrapper = PMIBootstrapper(base=2)
		prob = { 'x': 0.2, 'y': 0, ('x', 'y'): 0.1 }
		self.assertEqual(0, bootstrapper._pmi(prob, 'x', 'y'))

	def test_pmi_zero_joint(self):
		"""
		Test that when calculating the PMI and the joint probability of `seed` and `candidates` is 0, 0 is returned.
		"""

		bootstrapper = PMIBootstrapper(base=2)
		prob = { 'x': 0.3, 'y': 0.2, ('x', 'y'): 0 }
		self.assertEqual(0, bootstrapper._pmi(prob, 'x', 'y'))

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

		bootstrapper = PMIBootstrapper(base=2)
		self.assertEqual(-1, bootstrapper._pmi(prob, '!x', '!y'))
		self.assertEqual(0.222392, round(bootstrapper._pmi(prob, '!x', 'y'), 6))
		self.assertEqual(1.584963, round(bootstrapper._pmi(prob, 'x', '!y'), 6))
		self.assertEqual(-1.584963, round(bootstrapper._pmi(prob, 'x', 'y'), 6))

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

		bootstrapper = PMIBootstrapper(base=2)
		self.assertEqual(-1, bootstrapper._pmi(prob, '!y', '!x'))
		self.assertEqual(0.222392, round(bootstrapper._pmi(prob, 'y', '!x'), 6))
		self.assertEqual(1.584963, round(bootstrapper._pmi(prob, '!y', 'x'), 6))
		self.assertEqual(-1.584963, round(bootstrapper._pmi(prob, 'y', 'x'), 6))
