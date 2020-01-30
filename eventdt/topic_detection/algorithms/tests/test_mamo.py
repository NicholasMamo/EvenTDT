"""
Run unit tests on Mamo et al.'s algorithms
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.append(path)

from libraries.topic_detection.algorithms import mamo_eld
from libraries.topic_detection.nutrition_store.memory_nutrition_store import MemoryNutritionStore

import random

class TestMamo(unittest.TestCase):
	"""
	Test the Mamo et al. algorithms
	"""

	def test_eld(self):
		"""
		Test the ELD topic detection algorithm
		"""

		nutrition_store = MemoryNutritionStore()
		nutrition_store.add_nutrition_set(1532783836 + 60 * 0, { "a": 1 })
		nutrition_store.add_nutrition_set(1532783836 + 60 * 1, { "a": 0.4 })
		nutrition_store.add_nutrition_set(1532783836 + 60 * 2, { "a": 0.7 })
		nutrition_store.add_nutrition_set(1532783836 + 60 * 3, { "a": 0.65 })
		nutrition_store.add_nutrition_set(1532783836 + 60 * 4, { "a": 0.4 })
		nutrition_store.add_nutrition_set(1532783836 + 60 * 5, { "a": 0.5 })
		nutrition_store.add_nutrition_set(1532783836 + 60 * 6, { "a": 0.67 })

		min_nutrition_store = MemoryNutritionStore()
		min_nutrition_store.add_nutrition_set(1532783836 + 60 * 0, { "a": 0 })
		min_nutrition_store.add_nutrition_set(1532783836 + 60 * 1, { "a": 0 })
		min_nutrition_store.add_nutrition_set(1532783836 + 60 * 2, { "a": 0 })
		min_nutrition_store.add_nutrition_set(1532783836 + 60 * 3, { "a": 0 })
		min_nutrition_store.add_nutrition_set(1532783836 + 60 * 4, { "a": 0 })
		min_nutrition_store.add_nutrition_set(1532783836 + 60 * 5, { "a": 0 })
		min_nutrition_store.add_nutrition_set(1532783836 + 60 * 6, { "a": 0 })

		mid_nutrition_store = MemoryNutritionStore()
		mid_nutrition_store.add_nutrition_set(1532783836 + 60 * 0, { "a": 0.5 })
		mid_nutrition_store.add_nutrition_set(1532783836 + 60 * 1, { "a": 0.5 })
		mid_nutrition_store.add_nutrition_set(1532783836 + 60 * 2, { "a": 0.5 })
		mid_nutrition_store.add_nutrition_set(1532783836 + 60 * 3, { "a": 0.5 })
		mid_nutrition_store.add_nutrition_set(1532783836 + 60 * 4, { "a": 0.5 })
		mid_nutrition_store.add_nutrition_set(1532783836 + 60 * 5, { "a": 0.5 })
		mid_nutrition_store.add_nutrition_set(1532783836 + 60 * 6, { "a": 0.5 })

		max_nutrition_store = MemoryNutritionStore()
		max_nutrition_store.add_nutrition_set(1532783836 + 60 * 0, { "a": 1 })
		max_nutrition_store.add_nutrition_set(1532783836 + 60 * 1, { "a": 1 })
		max_nutrition_store.add_nutrition_set(1532783836 + 60 * 2, { "a": 1 })
		max_nutrition_store.add_nutrition_set(1532783836 + 60 * 3, { "a": 1 })
		max_nutrition_store.add_nutrition_set(1532783836 + 60 * 4, { "a": 1 })
		max_nutrition_store.add_nutrition_set(1532783836 + 60 * 5, { "a": 1 })
		max_nutrition_store.add_nutrition_set(1532783836 + 60 * 6, { "a": 1 })

		self.assertEqual(round(mamo_eld.detect_topics(nutrition_store, { "a": 0.7 }, -1, 7, term_only=False)[0][1], 7), 0.1146226)

		self.assertEqual(round(mamo_eld.detect_topics(max_nutrition_store, { "a": 0.7 }, -1, 7, term_only=False)[0][1], 7), -0.3)
		self.assertEqual(round(mamo_eld.detect_topics(mid_nutrition_store, { "a": 0.7 }, -1, 7, term_only=False)[0][1], 7), 0.2)
		self.assertEqual(round(mamo_eld.detect_topics(min_nutrition_store, { "a": 0.7 }, -1, 7, term_only=False)[0][1], 7), 0.7)

		self.assertEqual(round(mamo_eld.detect_topics(max_nutrition_store, { "a": 1 }, -1, 7, term_only=False)[0][1], 7), 0)
		self.assertEqual(round(mamo_eld.detect_topics(mid_nutrition_store, { "a": 1 }, -1, 7, term_only=False)[0][1], 7), 0.5)
		self.assertEqual(round(mamo_eld.detect_topics(min_nutrition_store, { "a": 1 }, -1, 7, term_only=False)[0][1], 7), 1)

		self.assertEqual(round(mamo_eld.detect_topics(max_nutrition_store, { "a": 0 }, -1, 7, term_only=False)[0][1], 7), -1)
		self.assertEqual(round(mamo_eld.detect_topics(mid_nutrition_store, { "a": 0 }, -1, 7, term_only=False)[0][1], 7), -0.5)
		self.assertEqual(round(mamo_eld.detect_topics(min_nutrition_store, { "a": 0 }, -1, 7, term_only=False)[0][1], 7), 0)

		# bounds

		self.assertEqual(round(mamo_eld.detect_topics(max_nutrition_store, { "a": 0.5 }, -1, 7, term_only=False)[0][1], 7), -0.5)
		self.assertEqual(round(mamo_eld.detect_topics(mid_nutrition_store, { "a": 0.5 }, -1, 7, term_only=False)[0][1], 7), 0)

		self.assertEqual(round(mamo_eld.detect_topics(max_nutrition_store, { "a": 1 }, -1, 7, term_only=False)[0][1], 7), 0)
		self.assertEqual(round(mamo_eld.detect_topics(mid_nutrition_store, { "a": 1 }, -1, 7, term_only=False)[0][1], 7), 0.5)
