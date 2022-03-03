"""
Run unit tests on the :class:`~objects.attributable.Attributable` class.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from objects import Attributable
from vsm import Vector

class TestAttributable(unittest.TestCase):
    """
    Test the :class:`~objects.attributable.Attributable` class.
    """

    def test_create_empty(self):
        """
        Test that the empty :class:`~objects.attributable.Attributable` object has an empty dictionary.
        """

        self.assertEqual({ }, Attributable().attributes)

    def test_create_None(self):
        """
        Test that a :class:`~objects.attributable.Attributable` object created with `None` attributes still has an empty dictionary.
        """

        self.assertEqual({ }, Attributable(None).attributes)

    def test_create_with_data(self):
        """
        Test that an :class:`~objects.attributable.Attributable` object accepts attributes in the constructor.
        """

        self.assertEqual({ 'a': 1 }, Attributable({ 'a': 1 }).attributes)

    def test_init_name_attributes_overwrite_none(self):
        """
        Test that overwriting the attributes with ``None`` creates an empty dictionary of attributes.
        """

        attributable = Attributable({ 'a': 1 })
        self.assertEqual(1, attributable.a)

        attributable.attributes = None
        self.assertEqual({ }, attributable.attributes)

    def test_get_attribute_as_property(self):
        """
        Test getting an attribute from the :class:`~objects.attributable.Attributable` as a property.
        """

        attributable = Attributable({ 'a': 1 })
        self.assertEqual(1, attributable.a)

    def test_get_non_existent_attribute_as_property(self):
        """
        Test getting an attribute that does not exist from the :class:`~objects.attributable.Attributable` as a property.
        """

        attributable = Attributable({ 'a': 1 })
        self.assertEqual(None, attributable.b)

    def test_set_attribute_from_property(self):
        """
        Test that attributes cannot be set using properties.
        """

        attributable = Attributable({ 'a': 1 })
        attributable.b = 10
        self.assertEqual(None, attributable.attributes.get('b'))

    def test_get_attribute_as_property_from_derived_classes(self):
        """
        Test that attributes can be accessed as properties even in derived classes.
        """

        vector = Vector(dimensions={ 'a': 1 }, attributes={ 'b': 2 })
        self.assertEqual({ 'b': 2 }, vector.attributes)

    def test_get_actual_property_from_attributable(self):
        """
        Test that normal properties remain accessable.
        """

        vector = Vector(dimensions={ 'a': 1 })
        self.assertEqual({ 'a': 1 }, vector.dimensions)

    def test_call_function_not_property(self):
        """
        Test that normal functions remain accessable.
        """

        vector = Vector(dimensions={ 'a': 1 })
        self.assertEqual(dict, type(vector.to_array()))
