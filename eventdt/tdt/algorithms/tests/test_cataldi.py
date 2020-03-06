"""
Run unit tests on Cataldi et al. (2014)'s algorithm.
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

from algorithms import Cataldi
from nutrition.memory import MemoryNutritionStore
class TestCataldi(unittest.TestCase):
	"""
	Test Cataldi et al. (2014)'s' algorithm.
	"""

	z = x.copy()
	z.update(y)
	return z

class TestCataldi(unittest.TestCase):
	"""
	Test Cataldi et al.'s algorithm.
	"""

	def test_topic_detection(self):
		"""
		Test the topic detection component
		"""

		nutrition_store = MemoryNutritionStore()
		nutrition_store.add_nutrition_set(1532783836 + 60 * 0, { "a": 2 , 	"b": 8 , 				"d": 20 , 				"f": 7 })
		nutrition_store.add_nutrition_set(1532783836 + 60 * 1, { 			"b": 7 , 				"d": 22 , 				"f": 2 })
		nutrition_store.add_nutrition_set(1532783836 + 60 * 2, { "a": 4 , 	"b": 8 , 	"c": 1 , 	"d": 23 , 				"f": 1 })
		nutrition_store.add_nutrition_set(1532783836 + 60 * 3, { "a": 3 , 	"b": 8 , 	"c": 1 , 	"d": 23 , 				"f": 8 })
		nutrition_store.add_nutrition_set(1532783836 + 60 * 4, { "a": 7 , 	"b": 10 , 	"c": 2 , 	"d": 26 , 	"e": 15 , 	"f": 7 })
		nutrition_store.add_nutrition_set(1532783836 + 60 * 5, { "a": 10 , 	"b": 9 , 	"c": 7 , 	"d": 20 , 	"e": 5 , 	"f": 5 })

		self.assertEqual(cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 1), ["d"])
		self.assertEqual(cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 2), ["d"])
		self.assertEqual(cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 3), ["f"])
		self.assertEqual(cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 4), ["e"])
		self.assertEqual(cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 5), ["a", "c"])

	def test_filtered_topic_detection(self):
		"""
		Test the filtered implementation of the algorithm by Cataldi et al.
		"""

		alphabet = ["g", "h", "i", "j", "k", "l", "m", "n", "o", "p"]

		nutrition_store = MemoryNutritionStore()
		random.seed(2320)
		nutrition_store.add_nutrition_set(1532783836 + 60 * 0, concatenate_dicts({ "a": 2 , 	"b": 8 , 				"d": 10 , 				"f": 7 }, zip(alphabet, [ random.gauss(7, 0.1) for i in range(0, len(alphabet)) ])))
		nutrition_store.add_nutrition_set(1532783836 + 60 * 1, concatenate_dicts({ 				"b": 7 , 				"d": 11 , 				"f": 2 }, zip(alphabet, [ random.gauss(7, 0.1) for i in range(0, len(alphabet)) ])))
		nutrition_store.add_nutrition_set(1532783836 + 60 * 2, concatenate_dicts({ "a": 4 , 	"b": 8 , 	"c": 1 , 	"d": 13 , 				"f": 1 }, zip(alphabet, [ random.gauss(7, 0.1) for i in range(0, len(alphabet)) ])))
		nutrition_store.add_nutrition_set(1532783836 + 60 * 3, concatenate_dicts({ "a": 7 , 	"b": 8 , 	"c": 1 , 	"d": 13 , 				"f": 8 }, zip(alphabet, [ random.gauss(7, 0.1) for i in range(0, len(alphabet)) ])))
		nutrition_store.add_nutrition_set(1532783836 + 60 * 4, concatenate_dicts({ "a": 10 , 	"b": 10 , 	"c": 2 , 	"d": 15 , 	"e": 15 , 	"f": 7 }, zip(alphabet, [ random.gauss(7, 0.1) for i in range(0, len(alphabet)) ])))
		nutrition_store.add_nutrition_set(1532783836 + 60 * 5, concatenate_dicts({ "a": 25 , 	"b": 9 , 	"c": 7 , 	"d": 10 , 	"e": 5 , 	"f": 5 }, zip(alphabet, [ random.gauss(7, 0.1) for i in range(0, len(alphabet)) ])))
	def test_compute_burst_non_existent_term(self):
		"""
		Test that when computing the burst of a term that does not exist, 0 is returned.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		store.add(60, { 'a': 0 })
		store.add(50, { 'a': 0 })
		store.add(40, { 'a': 0 })
		self.assertEqual(0, algo._compute_burst('b', store.get(60), store.until(60)))

	def test_compute_burst_term_zero_nutrition(self):
		"""
		Test that when computing the burst of a term that has a nutrition of 0, 0 is returned.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		store.add(60, { 'a': 0 })
		store.add(50, { 'a': 0 })
		store.add(40, { 'a': 0 })
		self.assertEqual(0, algo._compute_burst('a', store.get(60), store.until(60)))

	def test_compute_burst_empty_historic(self):
		"""
		Test that when computing the burst when the historic data is empty, 0 is returned.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		store.add(60, { 'a': 0 })
		self.assertEqual(0, algo._compute_burst('a', store.get(60), store.until(60)))

	def test_compute_burst_recency(self):
		"""
		Test that when computing burst, recent historical data has more importance.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		store.add(60, { 'a': 30, 'b': 30 })
		store.add(50, { 'a': 20, 'b': 10 })
		store.add(40, { 'a': 10, 'b': 20 })
		self.assertGreater(algo._compute_burst('b', store.get(60), store.until(60)),
						   algo._compute_burst('a', store.get(60), store.until(60)))

	def test_compute_burst(self):
		"""
		Test the burst computation.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		store.add(60, { 'a': 30 })
		store.add(50, { 'a': 20 })
		store.add(40, { 'a': 10 })

		"""
		Formula: (30^2 - 20^2) 1/(log(3 - 2 + 1)) + (30^2 - 10^2) 1/(log(3 - 1 + 1))
		"""
		self.assertEqual(round(3337.6866668751888215, 10),
						 round(algo._compute_burst('a', store.get(60), store.until(60)), 10))

	def test_compute_burst_unchanged_nutrition(self):
		"""
		Test that when giving a dictionary of nutrition to compute the drops, the dictionary is unchanged.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		store.add(60, { 'a': 30 })
		store.add(50, { 'a': 20 })
		store.add(40, { 'a': 10 })
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
		algo = Cataldi(store)
		store.add(60, { 'a': 30 })
		store.add(50, { 'a': 20 })
		store.add(40, { 'a': 10 })
		nutrition = store.get(60)
		historic = store.until(60)
		historic_copy = dict(historic)
		algo._compute_burst('a', nutrition, historic)
		self.assertEqual(historic_copy, historic)

	def test_compute_drops_empty(self):
		"""
		Test that when computing the drops and there are no burst values, an empty list is returned.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		self.assertEqual([ ], algo._compute_burst_drops({ }))

	def test_compute_drops_one(self):
		"""
		Test that when computing the drops and there is only one burst value, an empty list is returned.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		self.assertEqual([ ], algo._compute_burst_drops({ 'a': 10 }))

	def test_compute_drops_sorted(self):
		"""
		Thest that when computing the drops, the burst values are sorted.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		drops = algo._compute_burst_drops({ 'a': 10 , 'b': 25, 'c': 15, 'd': 40 })
		self.assertEqual([ 15, 10, 5 ], drops)
		self.assertTrue(all( drop > 0 for drop in drops))

	def test_compute_drops_n(self):
		"""
		Test that when computing the drops, the number of drops is equivalent to N-1.
		N is the number of burst values.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		bursts = { letter: random.randint(0, 100) for letter in string.ascii_uppercase }
		drops = algo._compute_burst_drops(bursts)
		self.assertEqual(len(string.ascii_uppercase), len(drops) + 1)
		self.assertTrue(all( drop >= 0 for drop in drops))

	def test_compute_drops_burst_unchanged(self):
		"""
		Test that when giving a dictionary of bursts to compute the drops, the dictionary is unchanged.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		bursts = { letter: random.randint(0, 100) for letter in string.ascii_uppercase }
		bursts_copy = dict(bursts)
		drops = algo._compute_burst_drops(bursts)
		self.assertEqual(bursts_copy, bursts)

	def test_critical_drop_index_empty(self):
		"""
		Test that when getting the critical drop index from an empty list, 0 is returned.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		self.assertEqual(0, algo._get_critical_drop_index([ ]))

	def test_critical_drop_index_single_value(self):
		"""
		Test that when getting the critical drop index from an list with one value, 2 is returned.
		If there is one drop value, there are two terms.
		This is a special case of all burst drop values being the same.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		self.assertEqual(2, algo._get_critical_drop_index([ 1 ]))

	def test_critical_drop_index(self):
		"""
		Test that when getting the critical drop index, the correct drop is returned.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		drops = [ 1, 1, 3, 3, 5, 4, 2 ]
		self.assertEqual(3, algo._get_critical_drop_index(drops))

	def test_critical_drop_equal_drops(self):
		"""
		Test that when getting the critical drop index from a list with equal drops, the critical index includes all values.
		In this example, there are 5 equal drops, indicating 6 terms with the same difference in burst.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		drops = [ 1 ] * 5
		self.assertEqual(6, algo._get_critical_drop_index(drops))

	def test_critical_drop_equal_drops_interval(self):
		"""
		Test that when getting the critical drop index from a list with an interval of equal drops, the critical index includes all values.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		bursts = { 'a': 20, 'b': 18, 'c': 16, 'd': 14, 'e': 12, 'f': 10, 'g': 5, 'h': 1 }
		drops = [ 2 ] * 5 + list(range(5, 3, -1))
		self.assertEqual(drops, algo._compute_burst_drops(bursts))
		self.assertEqual(6, algo._get_critical_drop_index(drops))
		self.assertEqual([ 'a', 'b', 'c', 'd', 'e', 'f' ],
						 sorted(bursts, key=bursts.get, reverse=True)[:algo._get_critical_drop_index(drops)])

	def test_critical_drop_index_drops_unchanged(self):
		"""
		Test that when giving a list of drops to the critical index function, the list is unchanged.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		drops = [ 1 ] * 5
		drops_copy = list(drops)
		algo._get_critical_drop_index(drops)
		self.assertEqual(drops_copy, drops)

	def test_bursty_terms_empty(self):
		"""
		Test that when the bursty terms is empty, an empty list is returned.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		self.assertEqual([ ], algo._get_bursty_terms({ }, 0))

	def test_bursty_terms_large_critical_drop_index(self):
		"""
		Test that when the critical index is larger than the number of bursty terms, a ValueError is raised.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		self.assertRaises(ValueError, algo._get_bursty_terms, { }, 1)

	def test_bursty_terms_all(self):
		"""
		Test that when the critical drop index is equal to the bursty terms, all terms are returned.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		drops = [ 1 ] * 5
		burst = { 'a': 10, 'b': 10, 'c': 10, 'd': 10, 'e': 10, 'f': 10, 'g': 10, 'h': 10 }
		critical_index = algo._get_critical_drop_index(algo._compute_burst_drops(burst))
		self.assertEqual(set(burst.keys()), set(algo._get_bursty_terms(burst, critical_index)))

	def test_bursty_terms_sorted(self):
		"""
		Test that the bursty terms are sorted in descending order of their burst.
		"""

		store = MemoryNutritionStore()
		algo = Cataldi(store)
		drops = [ 1 ] * 5
		burst = { 'a': 4, 'b': 2, 'c': 6, 'd': 12, 'e': 10, 'f': 8, 'g': 16, 'h': 14 }
		critical_index = algo._get_critical_drop_index(algo._compute_burst_drops(burst))
		self.assertEqual([ 'g', 'h', 'd', 'e', 'f', 'c', 'a', 'b' ], algo._get_bursty_terms(burst, critical_index))

	def test_bursty_terms_unchanged(self):
		"""
		Test that the bursty terms are unchanged when given to the bursty terms function.
		"""

		self.assertEqual(filtered_cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 1, p=1e-2), [])
		self.assertEqual(filtered_cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 2, p=1e-2), ["d"])
		self.assertEqual(filtered_cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 3, p=1e-2), ["f"])
		self.assertEqual(filtered_cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 4, p=1e-2), ["e"])
		self.assertEqual(filtered_cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 5, p=1e-2), ["a"])
		store = MemoryNutritionStore()
		algo = Cataldi(store)
		drops = [ 1 ] * 5
		burst = { 'a': 4, 'b': 2, 'c': 6, 'd': 12, 'e': 10, 'f': 8, 'g': 16, 'h': 14 }
		burst_copy = dict(burst)
		critical_index = algo._get_critical_drop_index(algo._compute_burst_drops(burst))
		self.assertEqual(burst_copy, burst)
