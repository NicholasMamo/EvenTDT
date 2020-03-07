"""
Run unit tests on Mamo et al. (2019)'s ELD algorithm.
"""

import math
import os
import random
import string
import sys
import time
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from algorithms import ELD
from nutrition.memory import MemoryNutritionStore
class TestELD(unittest.TestCase):
	"""
	Test Mamo et al. (2019)'s ELD algorithm.
	"""
	def test_compute_decay(self):
		"""
		Test the decay computation with multiple time windows.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		self.assertEqual(round(0.2231301601484298, 10),
			round(algo._compute_decay(3), 10))

	def test_compute_decay_custom_rate(self):
		"""
		Test that when the decay rate is not default, it is used.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store, 1./3.)
		self.assertEqual(round(0.3678794411714424, 10),
			round(algo._compute_decay(3), 10))

	def test_compute_coefficient_negative(self):
		"""
		Test that the coefficient computation with negative time windows raises a ValueError.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		self.assertRaises(ValueError, algo._compute_coefficient, -1)

	def test_compute_coefficient_zero(self):
		"""
		Test that the coefficient computation with no time windows equals 1.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		self.assertEqual(1, algo._compute_coefficient(0))

	def test_compute_coefficient_one(self):
		"""
		Test the coefficient computation with one time window.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		self.assertEqual(round(0.6065306597126334, 10),
						 round(algo._compute_coefficient(1), 10))

	def test_compute_coefficient_multiple(self):
		"""
		Test the coefficient computation with multiple time windows.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		self.assertEqual(round(1.1975402610325056, 10),
						 round(algo._compute_coefficient(3), 10))
