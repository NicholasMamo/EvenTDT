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

	def test_detect(self):
		"""
		Test detecting bursty terms.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 0.67, 'b': 1, 'c': 1 })
		store.add(50, { 'a': 0.67, 'b': 0.33, 'c': 0.3 })
		store.add(40, { 'a': 1, 'b': 0.67, 'c': 0.67 })
		self.assertEqual(set([ 'c', 'b' ]), set(algo.detect(store.get(60), until=60)))

	def test_detect_recency(self):
		"""
		Test that when detecting bursty terms, recent time windows have more weight.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 1, 'b': 1, 'c': 1 })
		store.add(50, { 'a': 0.67, 'b': 0.3, 'c': 0.67 })
		store.add(40, { 'a': 0.33, 'b': 0.67, 'c': 0.3 })
		terms = algo.detect(store.get(60), until=60)
		self.assertGreater(terms.get('b'), terms.get('c'))

	def test_detect_since_inclusive(self):
		"""
		Test that when detecting bursty terms with a selection of time windows, only those time windows are used.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 1, 'b': 1, 'c': 1 })
		store.add(50, { 'a': 0.67, 'b': 1, 'c': 1 })
		store.add(40, { 'a': 0.33, 'b': 0.67, 'c': 1 })
		self.assertEqual(set([ 'a' ]), set(algo.detect(store.get(60), since=50, until=60)))
		self.assertEqual(set([ 'a', 'b' ]), set(algo.detect(store.get(60), since=40, until=60)))

	def test_detect_nutrition_store_unchanged(self):
		"""
		Test that when detecting bursty terms, the store itself is unchanged.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 1, 'b': 1, 'c': 1 })
		store.add(50, { 'a': 0.67, 'b': 0.3, 'c': 0.33 })
		store.add(40, { 'a': 0.33, 'b': 0.67, 'c': 0.3 })
		store_copy = dict(store.all())
		algo.detect(store.get(60))
		self.assertEqual(store_copy, store.all())

	def test_detect_empty_nutrition(self):
		"""
		Test that when detecting bursty terms with an empty nutrition, no terms are returned.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 1, 'b': 1, 'c': 1 })
		store.add(50, { 'a': 0.67, 'b': 0.3, 'c': 0.33 })
		store.add(40, { 'a': 0.33, 'b': 0.67, 'c': 0.3 })
		self.assertFalse(algo.detect({ }))

	def test_detect_empty_historic(self):
		"""
		Test that when detecting bursty terms with empty historic data, no terms are returned.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(60, { 'a': 0.95, 'b': 0.75, 'c': 1 })
		store.add(50, { 'a': 0.67, 'b': 0.3, 'c': 0.33 })
		store.add(40, { 'a': 0.33, 'b': 0.67, 'c': 0.3 })
		self.assertEqual(set([ ]), set(algo.detect(store.get(60), until=40)))

	def test_detect_all_terms(self):
		"""
		Test that when detecting bursty terms, the data is taken from both the historic data and the nutrition.
		For this test, the minimum burst is set such that it includes all burst values.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(50, { 'a': 0.67, 'b': 0.3, 'c': 0.33 })
		store.add(40, { 'a': 0.33, 'b': 0.67, 'c': 0.3 })
		store.add(30, { 'a': 1.00, 'b': 0.75 })

		self.assertEqual(set([ 'a', 'b', 'd' ]), set(algo.detect({ 'd': 1.00 }, until=40, min_burst=-1.1)))
		self.assertEqual(set([ 'a', 'b', 'c', 'd' ]), set(algo.detect({ 'd': 1.00 }, until=60, min_burst=-1.1)))
		self.assertEqual(set([ 'a', 'b', 'c', 'd' ]), set(algo.detect({ 'd': 1.00 }, until=60, min_burst=-1.)))
		self.assertEqual(set([ 'd' ]), set(algo.detect({ 'd': 1.00 }, until=60)))

	def test_get_terms_negative_minimum_burst(self):
		"""
		Test that when detecting bursty terms, all terms are returned when the minimum burst is negative.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(50, { 'a': 0.67, 'b': 0.3, 'c': 0.33 })
		store.add(40, { 'a': 0.33, 'b': 0.67, 'c': 0.3 })
		store.add(30, { 'a': 1.00, 'b': 0.75 })

		nutrition = { 'd': 1.00 }
		historic = store.until(60)
		self.assertEqual(set(algo._get_terms(-0.1, nutrition, historic)), { 'a', 'b', 'c', 'd' })

	def test_get_terms_zero_minimum_burst(self):
		"""
		Test that when detecting bursty terms, the data is only taken from the present nutrition when the minimum burst is zero.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(50, { 'a': 0.67, 'b': 0.3, 'c': 0.33 })
		store.add(40, { 'a': 0.33, 'b': 0.67, 'c': 0.3 })
		store.add(30, { 'a': 1.00, 'b': 0.75 })

		nutrition = { 'd': 1.00 }
		historic = store.until(60)
		self.assertEqual(algo._get_terms(0, nutrition, historic), [ 'd' ])

	def test_get_terms_positive_minimum_burst(self):
		"""
		Test that when detecting bursty terms, the data is only taken from the present nutrition when the minimum burst is positive.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(50, { 'a': 0.67, 'b': 0.3, 'c': 0.33 })
		store.add(40, { 'a': 0.33, 'b': 0.67, 'c': 0.3 })
		store.add(30, { 'a': 1.00, 'b': 0.75 })

		nutrition = { 'd': 1.00 }
		historic = store.until(60)
		self.assertEqual(algo._get_terms(0.5, nutrition, historic), [ 'd' ])

	def test_get_terms_positive_minimum_burst_filter(self):
		"""
		Test that when detecting bursty terms, the data is only taken from the present nutrition when the minimum burst is positive.
		Moreover, the terms should be filtered based on the minimum burst.
		"""

		store = MemoryNutritionStore()
		algo = ELD(store)
		store.add(50, { 'a': 0.67, 'b': 0.3, 'c': 0.33 })
		store.add(40, { 'a': 0.33, 'b': 0.67, 'c': 0.3 })
		store.add(30, { 'a': 1.00, 'b': 0.75 })

		nutrition = { 'd': 1.00, 'e': 0.5 }
		historic = store.until(60)
		self.assertEqual(algo._get_terms(0.5, nutrition, historic), [ 'd', 'e' ])
		self.assertEqual(algo._get_terms(0.6, nutrition, historic), [ 'd' ])

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
