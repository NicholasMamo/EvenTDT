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
