"""
Run unit tests on the Attributable class
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '../')
if path not in sys.path:
    sys.path.append(path)

from libraries.objects.attributable import Attributable

class TestVector(unittest.TestCase):
	"""
	Test the Attributable class.
	"""

	def test_init(self):
		"""
		Test the Attributable constructor.
		"""

		v = Attributable()
		self.assertEqual(v.get_attributes(), {})

		v = Attributable({"x": 2, "y": 1})
		self.assertEqual(v.get_attributes(), {"x": 2, "y": 1})

	def test_attributes(self):
		"""
		Test setting and getting attributes.
		"""

		v = Attributable({"x": 2, "y": 1})
		v.set_attribute("x")
		self.assertEqual(v.get_attributes(), {"y": 1})

		v.set_attribute("x", 1)
		self.assertEqual(v.get_attributes(), {"x": 1, "y": 1})

		v.initialize_attribute("x", 2)
		self.assertEqual(v.get_attribute("x"), 1)

		v.initialize_attribute("w", 2)
		self.assertEqual(v.get_attribute("w"), 2)

		self.assertEqual(v.get_attribute("y"), 1)

		self.assertEqual(v.get_attribute("p"), None)

	def test_clear_attributes(self):
		"""
		Test clearing attributes.
		"""

		v = Attributable({"x": 3, "y": 2, "z": 4})
		v.clear_attributes()
		self.assertEqual(v.get_attributes(), {})

		v = Attributable({"x": 3, "y": 2, "z": 4})
		v.clear_attribute("w")
		self.assertEqual(v.get_attributes(), {"x": 3, "y": 2, "z": 4})

		v.clear_attribute("x")
		self.assertEqual(v.get_attributes(), {"y": 2, "z": 4})

	def test_export(self):
		"""
		Test exporting and importing attributables.
		"""

		v = Attributable({"x": 3, "y": 2, "z": 4})
		e = v.to_array()
		self.assertEqual(v.get_attributes(), Attributable.from_array(e).get_attributes())
		self.assertEqual(v.__dict__, Attributable.from_array(e).__dict__)
