"""
Run unit tests on the MemoryNutritionStore.
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.append(path)

from libraries.topic_detection.nutrition_store.memory_nutrition_store import MemoryNutritionStore

class TestMemoryNutritionStore(unittest.TestCase):
	"""
	Test the MemoryNutritionStore functionality.
	"""

	def test_add_nutrition_sets(self):
		"""
		Test adding nutrition sets.
		"""

		nutrition_store = MemoryNutritionStore()
		self.assertEqual(len(nutrition_store.get_all_nutrition_sets()), 0)
		self.assertEqual(nutrition_store.get_nutrition_set(1532783836), None)

		nutrition_store.add_nutrition_set("1532783836", ["a", "b"])
		self.assertEqual(len(nutrition_store.get_all_nutrition_sets()), 1)

		nutrition_store.add_nutrition_set(1532783896, ["c", "d"])
		self.assertEqual(len(nutrition_store.get_all_nutrition_sets()), 2)
		self.assertEqual(nutrition_store.get_nutrition_set(1532783836), ["a", "b"])
		self.assertEqual(nutrition_store.get_nutrition_set(1532783896), ["c", "d"])
		self.assertEqual(nutrition_store.get_all_nutrition_sets(), { 1532783836: ["a", "b"], 1532783896: ["c", "d"] })

	def test_recency(self):
		"""
		Test retrieving recent nutrition sets.
		"""

		nutrition_store = MemoryNutritionStore()
		nutrition_store.add_nutrition_set(1532783836, ["a", "b"])
		nutrition_store.add_nutrition_set("1532783896", ["c", "d"])
		nutrition_store.add_nutrition_set(1532783956, ["e", "f"])

		self.assertEqual(nutrition_store.get_recent_nutrition_sets(5), [
			["e", "f"],
			["c", "d"],
			["a", "b"]
		])

		self.assertEqual(nutrition_store.get_recent_nutrition_sets(1, 1532783956), [
			["c", "d"]
		])

		self.assertEqual(nutrition_store.get_recent_nutrition_sets(0, 1532783896), [])
		self.assertEqual(nutrition_store.get_recent_nutrition_sets(1, 1532783836), [])

	def test_retrieve(self):
		"""
		Test retrieving nutrition sets using timestamp filtering techniques.
		"""

		nutrition_store = MemoryNutritionStore()
		nutrition_store.add_nutrition_set(0, ["a"])
		nutrition_store.add_nutrition_set(1, ["b"])
		nutrition_store.add_nutrition_set(2, ["c"])
		nutrition_store.add_nutrition_set(3, ["d"])
		nutrition_store.add_nutrition_set(4, ["e"])
		nutrition_store.add_nutrition_set(5, ["f"])
		nutrition_store.add_nutrition_set(6, ["g"])
		nutrition_store.add_nutrition_set(7, ["h"])
		nutrition_store.add_nutrition_set(8, ["i"])
		nutrition_store.add_nutrition_set(9, ["j"])

		"""
		Since.
		"""

		self.assertEqual(nutrition_store.since(7), {
			7: ["h"],
			8: ["i"],
			9: ["j"]
		})

		self.assertEqual(nutrition_store.since(9), {
			9: ["j"]
		})

		self.assertEqual(nutrition_store.since(10), { })

		"""
		Before.
		"""

		self.assertEqual(nutrition_store.before(3), {
			0: ["a"],
			1: ["b"],
			2: ["c"]
		})

		self.assertEqual(nutrition_store.before(1), {
			0: ["a"]
		})

		self.assertEqual(nutrition_store.before(0), { })

		"""
		Between.
		"""

		self.assertEqual(nutrition_store.between(0, 2), {
			0: ["a"],
			1: ["b"],
		})

		self.assertEqual(nutrition_store.between(8, 12), {
			8: ["i"],
			9: ["j"],
		})

		self.assertEqual(nutrition_store.between(-2, 0), { })
		self.assertEqual(nutrition_store.between(10, 12), { })
		self.assertEqual(nutrition_store.between(10, 8), { })

	def test_remove(self):
		"""
		Test removing old nutrition sets.
		"""

		start = 1532783836

		nutrition_store = MemoryNutritionStore()
		nutrition_store.add_nutrition_set(start, ["a", "b"])
		nutrition_store.add_nutrition_set(str(start + 60 * 1), ["c", "d"])
		nutrition_store.add_nutrition_set(start + 60 * 2, ["e", "f"])
		nutrition_store.add_nutrition_set(start + 60 * 3, ["g", "h"])

		self.assertEqual(nutrition_store.get_recent_nutrition_sets(5), [
			["g", "h"],
			["e", "f"],
			["c", "d"],
			["a", "b"]
		])

		nutrition_store.remove_old_nutrition_sets(start + 60 * 1)
		self.assertEqual(nutrition_store.get_recent_nutrition_sets(5), [
			["g", "h"],
			["e", "f"],
			["c", "d"],
		])
