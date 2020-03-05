"""
Run unit tests on Zhao et al. (2011)'s algorithm.
"""

import math
import os
import sys
import time
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from algorithms import Zhao
from nutrition.memory import MemoryNutritionStore

class TestZhao(unittest.TestCase):
	"""
	Test Zhao et al. (2011)'s' algorithm.
	"""

	def test_empty_store(self):
		"""
		Test that when the nutrition store is empty, Zhao et al.'s algorithm does not fail, but returns `False`.
		"""

		store = MemoryNutritionStore()
		algo = Zhao()
		self.assertFalse(algo.detect(store))

	def test_timestamp_before_nutrition(self):
		"""
		Test that if a timestamp before which there is no nutrition is given, the algorithm returns `False`.
		"""

		store = MemoryNutritionStore()
		algo = Zhao()

		"""
		Create the test data.
		"""
		for i in range(10, 20):
			store.add(i, i * 10)

		self.assertFalse(algo.detect(store, timestamp=10))

	def test_small_time_window(self):
		"""
		Test that the post rate starts looking for bursts from the smallest time window even when multiple are breaking.
		"""

		store = MemoryNutritionStore()
		algo = Zhao()

		"""
		Create the test data.
		"""
		for i in range(6, 0, -1):
			for j in range(5, 0, -1):
				store.add(i * 5 + j, math.pow(i * 10, 3))

		self.assertEqual((31, 35), algo.detect(store, 35 + 1))

	def test_incomplete_nutrition_store(self):
		"""
		Test that when the 10-second time window is not breaking and there is no more data, the algorithm stops looking and returns `False`.
		"""

		store = MemoryNutritionStore()
		algo = Zhao()

		"""
		Create the test data.
		"""
		for i in range(6, 4, -1):
			for j in range(5, 0, -1):
				store.add(i * 5 + j, i * 10)

		self.assertFalse(algo.detect(store, 35 + 1))

	def test_10_time_window(self):
		"""
		Test that algorithm correctly detects bursts from the 10-second time window.
		"""

		store = MemoryNutritionStore()
		algo = Zhao()

		"""
		Create the test data.
		"""
		for i in range(60, 50, -1):
			store.add(i, 10 if i > 55 else 5)

		self.assertEqual((56, 60), algo.detect(store, 60 + 1))

	def test_20_time_window(self):
		"""
		Test that algorithm correctly detects bursts from the 20-second time window.
		"""

		store = MemoryNutritionStore()
		algo = Zhao()

		"""
		Create the test data.
		"""
		for i in range(60, 40, -1):
			store.add(i, 10 if i > 50 else 5)

		self.assertEqual((51, 60), algo.detect(store, 60 + 1))

	def test_30_time_window(self):
		"""
		Test that algorithm correctly detects bursts from the 30-second time window.
		"""

		store = MemoryNutritionStore()
		algo = Zhao()

		"""
		Create the test data.
		"""
		for i in range(60, 30, -1):
			store.add(i, 10 if i > 45 else 5)

		self.assertEqual((46, 60), algo.detect(store, 60 + 1))

	def test_60_time_window(self):
		"""
		Test that algorithm correctly detects bursts from the 60-second time window.
		"""

		store = MemoryNutritionStore()
		algo = Zhao()

		"""
		Create the test data.
		"""
		for i in range(60, 0, -1):
			store.add(i, 10 if i > 30 else 5)

		self.assertEqual((31, 60), algo.detect(store, 60 + 1))

	def test_realtime(self):
		"""
		Test that if no timestamp is given, the real-time timestamp is used instead.
		"""

		store = MemoryNutritionStore()
		algo = Zhao()

		"""
		Create the test data.
		"""
		timestamp = int(time.time())
		for i in range(timestamp, timestamp - 60, -1):
			store.add(i, 10 if i > timestamp - 10 else 1)

		self.assertEqual((timestamp - 9, timestamp), algo.detect(store))
