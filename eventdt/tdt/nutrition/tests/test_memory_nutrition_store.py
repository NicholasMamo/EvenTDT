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
		self.assertEqual({ 10: { 'a': 1 } }, nutrition.store)

	def test_add_nutrition_string(self):
		"""
		Test that when adding nutrition data in a timestamp given as a string, it is type-cast properly.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.store)
		nutrition.add('10', { 'a': 1 })
		self.assertEqual({ 10: { 'a': 1 } }, nutrition.store)

	def test_add_nutrition_arbitrary(self):
		"""
		Test that the nutrition store handles any type of nutrition data.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.store)
		nutrition.add(123, 10)
		self.assertEqual({ 123: 10 }, nutrition.store)

	def test_add_multiple_nutrition(self):
		"""
		Test that when adding nutrition data at multiple timestamps, all of them are stored.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.store)
		nutrition.add(10, { 'a': 1 })
		self.assertEqual({ 10: { 'a': 1 } }, nutrition.store)
		nutrition.add(20, { 'b': 2 })
		self.assertEqual({ 10: { 'a': 1 }, 20: { 'b': 2 } }, nutrition.store)

	def test_add_overwrite(self):
		"""
		Test that when adding nutrition to an already-occupied timestamp, the old data is overwritten.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.store)
		nutrition.add(10, { 'a': 1 })
		self.assertEqual({ 10: { 'a': 1 } }, nutrition.store)
		nutrition.add(10, { 'b': 2 })
		self.assertEqual({ 10: { 'b': 2 } }, nutrition.store)

	def test_add_overwrite_string(self):
		"""
		Test that when adding nutrition to an already-occupied timestamp with a string as timestamp, the old data is overwritten.
		"""

		nutrition = MemoryNutritionStore()
		self.assertEqual({ }, nutrition.store)
		nutrition.add(10, { 'a': 1 })
		self.assertEqual({ 10: { 'a': 1 } }, nutrition.store)
		nutrition.add('10', { 'b': 2 })
		self.assertEqual({ 10: { 'b': 2 } }, nutrition.store)
