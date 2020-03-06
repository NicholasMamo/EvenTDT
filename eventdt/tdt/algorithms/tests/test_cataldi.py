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

		self.assertEqual(filtered_cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 1, p=1e-2), [])
		self.assertEqual(filtered_cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 2, p=1e-2), ["d"])
		self.assertEqual(filtered_cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 3, p=1e-2), ["f"])
		self.assertEqual(filtered_cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 4, p=1e-2), ["e"])
		self.assertEqual(filtered_cataldi.detect_topics(nutrition_store, 1532783836 + 60 * 5, p=1e-2), ["a"])
