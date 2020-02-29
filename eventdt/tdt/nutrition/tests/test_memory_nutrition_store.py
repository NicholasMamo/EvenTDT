"""
Test the memory nutrition store.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from memory import MemoryNutritionStore

class TestMemoryNutritionStore(unittest.TestCase):
	"""
	Test the memory nutrition store.
	"""

	def test_create_nutrition_store(self):
		"""
		Test that when creating the nutrition store, it is an empty dictionary.
		"""

		self.assertEqual({ }, MemoryNutritionStore().store)

	def test_add_nutrition(self):
		"""
		Test that when adding nutrition data, it is stored.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.store)
		nutrition.add(10, { 'a': 1 })
		self.assertEqual({ '10': { 'a': 1 } }, nutrition.store)

	def test_add_nutrition_int(self):
		"""
		Test that when adding nutrition data in a timestamp given as an integer, it is type-cast properly.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.store)
		nutrition.add(10, { 'a': 1 })
		self.assertEqual({ '10': { 'a': 1 } }, nutrition.store)

	def test_add_nutrition_float(self):
		"""
		Test that when adding nutrition data in a timestamp given as a float, it is type-cast properly.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.store)
		nutrition.add(10.5, { 'a': 1 })
		self.assertEqual({ '10.5': { 'a': 1 } }, nutrition.store)

	def test_add_nutrition_arbitrary(self):
		"""
		Test that the nutrition store handles any type of nutrition data.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.store)
		nutrition.add(123, 10)
		self.assertEqual({ '123': 10 }, nutrition.store)

	def test_add_multiple_nutrition(self):
		"""
		Test that when adding nutrition data at multiple timestamps, all of them are stored.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.store)
		nutrition.add(10, { 'a': 1 })
		self.assertEqual({ '10': { 'a': 1 } }, nutrition.store)
		nutrition.add(20, { 'b': 2 })
		self.assertEqual({ '10': { 'a': 1 }, '20': { 'b': 2 } }, nutrition.store)

	def test_add_overwrite(self):
		"""
		Test that when adding nutrition to an already-occupied timestamp, the old data is overwritten.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.store)
		nutrition.add(10, { 'a': 1 })
		self.assertEqual({ '10': { 'a': 1 } }, nutrition.store)
		nutrition.add(10, { 'b': 2 })
		self.assertEqual({ '10': { 'b': 2 } }, nutrition.store)

	def test_add_overwrite_int(self):
		"""
		Test that when adding nutrition to an already-occupied timestamp with an integer as timestamp, the old data is overwritten.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.store)
		nutrition.add('10', { 'a': 1 })
		self.assertEqual({ '10': { 'a': 1 } }, nutrition.store)
		nutrition.add(10, { 'b': 2 })
		self.assertEqual({ '10': { 'b': 2 } }, nutrition.store)

	def test_add_overwrite_float(self):
		"""
		Test that when adding nutrition to an already-occupied timestamp with a float as timestamp, the old data is overwritten.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.store)
		nutrition.add('10.5', { 'a': 1 })
		self.assertEqual({ '10.5': { 'a': 1 } }, nutrition.store)
		nutrition.add(10.5, { 'b': 2 })
		self.assertEqual({ '10.5': { 'b': 2 } }, nutrition.store)

	def test_get_nutrition(self):
		"""
		Test getting nutrition data.
		"""

		nutrition = MemoryNutritionStore()
		nutrition.add('10', { 'a': 1 })
		self.assertEqual({ 'a': 1 }, nutrition.get('10'))

	def test_get_nutrition_int(self):
		"""
		Test getting nutrition data with an integer as timestamp.
		"""

		nutrition = MemoryNutritionStore()
		nutrition.add('10', { 'a': 1 })
		self.assertEqual({ 'a': 1 }, nutrition.get(10))

	def test_get_nutrition_float(self):
		"""
		Test getting nutrition data with a float as a timestamp.
		"""

		nutrition = MemoryNutritionStore()
		nutrition.add('10.5', { 'a': 1 })
		self.assertEqual({ 'a': 1 }, nutrition.get(10.5))

	def test_get_missing_nutrition(self):
		"""
		Test that when getting nutrition for a missing timestamp, an IndexError is returned.
		"""

		nutrition = MemoryNutritionStore()
		self.assertRaises(KeyError, nutrition.get, 10)

	def test_all_nutrition(self):
		"""
		Test that when getting all the nutrition data, all of it is returned.
		"""

		nutrition = MemoryNutritionStore()
		nutrition.add(10, 1)
		nutrition.add(20, 2)
		self.assertEqual({ '10': 1, '20': 2 }, nutrition.all())

	def test_all_dict(self):
		"""
		Test that the return type when getting all nutrition data is a dictionary.
		"""

		nutrition = MemoryNutritionStore()
		nutrition.add(10, 1)
		nutrition.add(20, 2)
		self.assertEqual(dict, type(nutrition.all()))

	def test_all_empty(self):
		"""
		Test that an empty dictionary is returned when there is no data in the nutrition store.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.all())

	def test_between_start_after_than_end(self):
		"""
		Test that when getting nutrition with the start timestamp being less than the end timestamp, a ValueError is raised.
		"""

		nutrition = MemoryNutritionStore()
		self.assertRaises(ValueError, nutrition.between, '10', '0')

	def test_between_start_same_as_end(self):
		"""
		Test that when getting nutrition with the start timestamp being equivalent to the end timestamp, a ValueError is raised.
		"""

		nutrition = MemoryNutritionStore()
		self.assertRaises(ValueError, nutrition.between, '10', '10')

	def test_between_start_after_than_end_int(self):
		"""
		Test that when getting nutrition with the start timestamp being less than the end timestamp, a ValueError is raised.
		This test uses integers.
		"""

		nutrition = MemoryNutritionStore()
		self.assertRaises(ValueError, nutrition.between, 10, 0)

	def test_between_start_same_as_end_int(self):
		"""
		Test that when getting nutrition with the start timestamp being equivalent to the end timestamp, a ValueError is raised.
		This test uses integers.
		"""

		nutrition = MemoryNutritionStore()
		self.assertRaises(ValueError, nutrition.between, 10, 10)

	def test_between_start_after_than_end_float(self):
		"""
		Test that when getting nutrition with the start timestamp being less than the end timestamp, a ValueError is raised.
		This test uses floats.
		"""

		nutrition = MemoryNutritionStore()
		self.assertRaises(ValueError, nutrition.between, 10.5, 0.0)

	def test_between_start_same_as_end_float(self):
		"""
		Test that when getting nutrition with the start timestamp being equivalent to the end timestamp, a ValueError is raised.
		This test uses floats.
		"""

		nutrition = MemoryNutritionStore()
		self.assertRaises(ValueError, nutrition.between, 10.5, 10.5)

	def test_between_start_inclusive(self):
		"""
		Test that the start timestamp is inclusive when getting nutrition data between two timestamps.
		"""

		nutrition = MemoryNutritionStore()
		nutrition.add('10', 1)
		nutrition.add('20', 2)
		self.assertEqual({ '10': 1}, nutrition.between(10, 15))

	def test_between_end_exclusive(self):
		"""
		Test that the end timestamp is exclusive when getting nutrition data between two timestamps.
		"""

		nutrition = MemoryNutritionStore()
		nutrition.add('10', 1)
		nutrition.add('20', 2)
		self.assertEqual({ '10': 1}, nutrition.between(9, 20))

	def test_between_empty_result_dict(self):
		"""
		Test that when getting the nutrition data matches nothing, an empty dictionary is returned.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.between(0, 10))

	def test_between(self):
		"""
		Test getting nutrition data between two timestamps.
		"""

		nutrition = MemoryNutritionStore()
		nutrition.add('0', 0)
		nutrition.add('10', 1)
		nutrition.add('20', 2)
		self.assertEqual({ '10': 1}, nutrition.between(1, 19))
