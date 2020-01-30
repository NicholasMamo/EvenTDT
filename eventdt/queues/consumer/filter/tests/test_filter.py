"""
Run unit tests on the Filter class
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.append(path)

from libraries.queues.consumer.filter import filter

class TestFilter(unittest.TestCase):
	"""
	Test the Filter class
	"""

	def test_filter(self):
		"""
		Test the basic filter functionality
		"""

		element = {
			"int": 10,
			"float": 2.4,
		}

		f = filter.Filter([])

		f.set_rules([
			("int", filter.lte, 10),
		])
		self.assertTrue(f.filter(element))

		f.set_rules([
			("int", filter.lt, 10)
		])
		self.assertFalse(f.filter(element))

		f.set_rules([
			("int", filter.gte, 10),
		])
		self.assertTrue(f.filter(element))

		f.set_rules([
			("int", filter.gt, 10)
		])
		self.assertFalse(f.filter(element))

		f.set_rules([
			("int", filter.equal, 10),
		])
		self.assertTrue(f.filter(element))

		f.set_rules([
			("int", filter.not_equal, 10)
		])
		self.assertFalse(f.filter(element))

		f.set_rules([
			("int", filter.in_list, [10, 20]),
		])
		self.assertTrue(f.filter(element))

		f.set_rules([
			("int", filter.not_in_list, [10, 20, 30])
		])
		self.assertFalse(f.filter(element))

	def test_combined_filter(self):
		"""
		Test filters that use multiple filters simultaneously
		"""

		element = {
			"int": 10,
			"float": 2.4,
			"l": {
				1: 3
			},
		}

		f = filter.Filter([])

		f.set_rules([
			("int", filter.gte, "float"),
		])
		self.assertTrue(f.filter(element))

		f.set_rules([
			("int", filter.gte, "l:1"),
		])
		self.assertTrue(f.filter(element))

	def test_recursive_filter(self):
		"""
		Test the recursive filter functionality
		"""

		element = {
			"a": {
				"b": 10,
				"c": {
					"d": "s",
					"e": 10,
					"f": 9,
					2: [5, 3, 10]
				}
			}
		}

		f = filter.Filter([])

		f.set_rules([
			("a:b", filter.equal, "a:c:e"),
		])
		self.assertTrue(f.filter(element))

		f.set_rules([
			("a:b", filter.in_list, "a:c:2"),
		])
		self.assertTrue(f.filter(element))
