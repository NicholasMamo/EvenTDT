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
	def test_compute_burst_non_existent_term(self):
		"""
		Test that when computing the burst of a term that does not exist, 0 is returned.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 0 })
		store.add(50, { 'a': 0 })
		store.add(40, { 'a': 0 })
		self.assertEqual(0, algo._compute_burst('d', store.get(60), store.until(60)))

	def test_compute_burst_term_zero_nutrition(self):
		"""
		Test that when computing the burst of a term that has a nutrition of 0, 0 is returned.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 0 })
		store.add(50, { 'a': 0 })
		store.add(40, { 'a': 0 })
		self.assertEqual(0, algo._compute_burst('a', store.get(60), store.until(60)))

	def test_compute_burst_empty_historic(self):
		"""
		Test that when computing the burst when the historic data is empty, 0 is returned.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 0 })
		self.assertEqual(0, algo._compute_burst('a', store.get(60), store.until(60)))

	def test_compute_burst_recency(self):
		"""
		Test that when computing burst, recent historical data has more importance.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 1, 'b': 1 })
		store.add(50, { 'a': 0.67, 'b': 0.33 })
		store.add(40, { 'a': 0.33, 'b': 0.67 })
		self.assertGreater(algo._compute_burst('b', store.get(60), store.until(60)),
						   algo._compute_burst('a', store.get(60), store.until(60)))

	def test_compute_burst(self):
		"""
		Test the burst computation.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 1 })
		store.add(50, { 'a': 0.67 })
		store.add(40, { 'a': 0.33 })

		"""
		Formula: ((1 - 0.67) 1/(sqrt(e^1)) + (1 - 0.33) 1/(sqrt(e^2)))/(1/sqrt(e^1) + 1/sqrt(e^2))
		"""
		self.assertEqual(round(0.458363827391369, 10),
						 round(algo._compute_burst('a', store.get(60), store.until(60)), 10))

	def test_compute_burst_unchanged_nutrition(self):
		"""
		Test that when giving a dictionary of nutrition to compute the drops, the dictionary is unchanged.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 1 })
		store.add(50, { 'a': 0.67 })
		store.add(40, { 'a': 0.33 })
		nutrition = store.get(60)
		historic = store.until(60)
		nutrition_copy = dict(nutrition)
		algo._compute_burst('a', nutrition, historic)
		self.assertEqual(nutrition_copy, nutrition)

	def test_compute_burst_unchanged_historical(self):
		"""
		Test that when giving a dictionary of historic nutrition to compute the drops, the dictionary is unchanged.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 1 })
		store.add(50, { 'a': 0.67 })
		store.add(40, { 'a': 0.33 })
		nutrition = store.get(60)
		historic = store.until(60)
		historic_copy = dict(historic)
		algo._compute_burst('a', nutrition, historic)
		self.assertEqual(historic_copy, historic)

	def test_compute_burst_upper_bound(self):
		"""
		Test that the upper bound of the burst is 1 when the maximum nutrition is 1.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 1 })
		store.add(50, { 'a': 0 })
		store.add(40, { 'a': 0 })
		self.assertEqual(1, algo._compute_burst('a', store.get(60), store.until(60)))

	def test_compute_burst_lower_bound(self):
		"""
		Test that the lower bound of the burst is -1 when the maximum nutrition is 1.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 0 })
		store.add(50, { 'a': 1 })
		store.add(40, { 'a': 1 })
		self.assertEqual(-1, algo._compute_burst('a', store.get(60), store.until(60)))

	def test_compute_burst_unchanged(self):
		"""
		Test that when the nutrition is unchanged, the burst is 0.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 1 })
		store.add(50, { 'a': 1 })
		store.add(40, { 'a': 1 })
		self.assertEqual(0, algo._compute_burst('a', store.get(60), store.until(60)))

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
