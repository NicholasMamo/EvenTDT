"""
Run unit tests on the Vector class
"""

import math
import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '..')
if path not in sys.path:
    sys.path.append(path)

from vector import Vector, VectorSpace
from vector_math import *

class TestVector(unittest.TestCase):
    """
    Test the Vector class.
    """

    def test_empty_constructor(self):
        """
        Test providing an empty constructor.
        """

        vector = Vector()
        self.assertEqual({ }, vector.dimensions)

    def test_constructor(self):
        """
        Test providing the dimensions to the vector constructor.
        """

        vector = Vector({"x": 2, "y": 1})
        self.assertEqual({"x": 2, "y": 1}, vector.dimensions)

    def test_dimensions(self):
        """
        Test setting and getting dimensions.
        """

        vector = Vector({"x": 2, "y": 1})
        del vector.dimensions["x"]
        self.assertEqual({"y": 1}, vector.dimensions)

        vector.dimensions["x"] = 1
        self.assertEqual({"x": 1, "y": 1}, vector.dimensions)

    def test_normalization(self):
        """
        Test normalizing vectors.
        """

        vector = Vector({"x": 3, "y": 1.2, "z": -2})
        vector.normalize()
        self.assertEqual({ "x": 0.789474, "y": 0.315789, "z": -0.526316 }, { key: round(value, 6) for key, value in vector.dimensions.items() })

    def test_double_normalization(self):
        """
        Test that normalizing the same vector twice returns the same vector as when normalized once.
        """

        vector = Vector({"x": 3, "y": 1.2, "z": -2})
        vector.normalize()
        w = vector.copy()
        w.normalize()
        self.assertEqual(vector.dimensions, w.dimensions)

    def test_normalize_empty_vector(self):
        """
        Test that when normalizing an empty vector, the resulting vector is also empty.
        """

        vector = Vector({ })
        vector.normalize()
        self.assertEqual({ }, vector.dimensions)

    def test_normalize_zero_length_vector(self):
        """
        Test that when normalizing a vector with a zero length, the resulting vector is also empty.
        """

        vector = Vector({ 'x': 0 })
        vector.normalize()
        self.assertEqual({ 'x': 0 }, vector.dimensions)

    def test_get_dimension(self):
        """
        Test that when getting the value of a dimension, the correct value is returned.
        """

        vector = Vector({ 'x': 1 })
        self.assertEqual(1, vector.dimensions['x'])

    def test_get_non_existent_dimension(self):
        """
        Test that when getting the value of a dimension that does not exist, 0 is returned.
        """

        vector = Vector({ })
        self.assertEqual(0, vector.dimensions['x'])

    def test_vector_space_initialization(self):
        """
        Test that when providing no dimensions, an empty vector space is created.
        """

        vector = Vector()
        self.assertEqual({ }, vector.dimensions)
        self.assertEqual(0, vector.dimensions['x'])
        vector.dimensions['x'] = 10
        self.assertEqual({ 'x': 10 }, vector.dimensions)
        self.assertEqual(10, vector.dimensions['x'])

    def test_dimensions_vector_space(self):
        """
        Test that dimensions are created as a vector space.
        """

        vector = Vector()
        self.assertEqual(VectorSpace, type(vector.dimensions))

    def test_empty_dict_dimensions_vector_space(self):
        """
        Test that dimensions are created as a vector space when given as an empty dictionary.
        """

        vector = Vector({ })
        self.assertEqual(VectorSpace, type(vector.dimensions))

    def test_non_empty_dict_dimensions_vector_space(self):
        """
        Test that dimensions are created as a vector space when given as a non-empty dictionary.
        """

        vector = Vector({ 'x': 10 })
        self.assertEqual(VectorSpace, type(vector.dimensions))

    def test_normalize_vector_space(self):
        """
        Test that when a vector is normalized, its dimensions ae a vecto space.
        """

        vector = Vector({ 'x': 10 })
        self.assertEqual(VectorSpace, type(vector.dimensions))
        vector.normalize()
        self.assertEqual(VectorSpace, type(vector.dimensions))

    def test_copy(self):
        """
        Test copying.
        """

        vector = Vector({ 'x': 3 })
        copy = vector.copy()

        self.assertEqual(vector.dimensions, copy.dimensions)

        vector.dimensions['x'] = 2
        self.assertEqual(2, vector.dimensions['x'])
        self.assertEqual(3, copy.dimensions['x'])
        vector.dimensions['x'] = 3

    def test_copy_attributes(self):
        """
        Test that the attributes are also copied.
        """

        vector = Vector({ 'x': 3 }, { 'y': True })
        copy = vector.copy()

        self.assertEqual(vector.attributes, copy.attributes)

    def test_copy_attributes_original(self):
        """
        Test that changing the copy's attributes does not affect the original's, and vice-versa.
        """

        vector = Vector({ 'x': 3 }, { 'y': True, 'z': False })
        copy = vector.copy()

        copy.attributes['y'] = False
        self.assertFalse(copy.attributes['y'])
        self.assertTrue(vector.attributes['y'])

        vector.attributes['z'] = True
        self.assertFalse(copy.attributes['z'])
        self.assertTrue(vector.attributes['z'])

    def test_copy_nested_attributes_original(self):
        """
        Test that changing the copy's nested attributes does not affect the original's, and vice-versa.
        """

        vector = Vector({ 'x': 3 }, { 'y': { 'a': True }, 'z': { 'b': False } })
        copy = vector.copy()

        copy.attributes['y']['a'] = False
        self.assertFalse(copy.attributes['y']['a'])
        self.assertTrue(vector.attributes['y']['a'])

        vector.attributes['z']['b'] = True
        self.assertFalse(copy.attributes['z']['b'])
        self.assertTrue(vector.attributes['z']['b'])

    def test_copy_dimensions_original(self):
        """
        Test that changing the copy's dimensions does not affect the original's, and vice-versa.
        """

        vector = Vector({ 'x': 3 }, { 'y': True })
        copy = vector.copy()

        copy.dimensions['x'] = 2
        self.assertEqual(2, copy.dimensions['x'])
        self.assertEqual(3, vector.dimensions['x'])

        vector.dimensions['x'] = 4
        self.assertEqual(2, copy.dimensions['x'])
        self.assertEqual(4, vector.dimensions['x'])

    def test_export(self):
        """
        Test exporting and importing vectors.
        """

        vector = Vector({ 'x': 3 })
        e = vector.to_array()
        self.assertEqual(vector.attributes, Vector.from_array(e).attributes)
        self.assertEqual(vector.dimensions, Vector.from_array(e).dimensions)
        self.assertEqual(vector.__dict__, Vector.from_array(e).__dict__)

    def test_export_attributes(self):
        """
        Test that exporting and importing vectors includes attributes.
        """

        vector = Vector({ 'x': 3 }, { "y": True })
        e = vector.to_array()
        self.assertEqual(vector.attributes, Vector.from_array(e).attributes)
        self.assertEqual(vector.__dict__, Vector.from_array(e).__dict__)
