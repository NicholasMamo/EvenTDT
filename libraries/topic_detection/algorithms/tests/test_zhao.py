"""
Run unit tests on Zhao et al.'s algorithm.
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.append(path)

from libraries.topic_detection.algorithms import zhao
from libraries.topic_detection.nutrition_store.memory_nutrition_store import MemoryNutritionStore

import random

class TestZhao(unittest.TestCase):
	"""
	Test Zhao et al.'s algorithm.
	"""

	def test_topic_detection(self):
		"""
		Test the topic detection component
		"""

		nutrition_store = MemoryNutritionStore()
		volume = [4, 6, 7, 4, 5,
					6, 7, 8, 10, 12,
					15, 25, 40, 45, 30,
					28, 30, 32, 48, 50,
					45, 40, 35, 32, 31,
					30, 31, 30, 28, 27,
					32, 38, 40, 37, 36,
					35, 33, 34, 32, 37,
					35, 35, 33, 34, 35,
					40, 37, 39, 37, 33,
					30, 28, 35, 30, 25]

		for i, v in enumerate(volume):
			nutrition_store.add_nutrition_set(i * 2, v)

		self.assertTrue(zhao.detect_topics(nutrition_store, 40)[0])
		self.assertTrue(zhao.detect_topics(nutrition_store, 60)[0])
		self.assertFalse(zhao.detect_topics(nutrition_store, 100)[0])
