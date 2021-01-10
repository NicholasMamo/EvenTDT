"""
Run unit tests on the :class:`~attributes.profile.Profile` class.
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '..', '..')
if path not in sys.path:
    sys.path.append(path)

from attributes.profile import Profile

class TestProfile(unittest.TestCase):
    """
    Test the :class:`~attributes.profile.Profile` class.
    """

    def test_init_attributes_empty(self):
        """
        Test that the attributes are initially empty.
        """

        profile = Profile()
        self.assertEqual({ }, profile.attributes)

    def test_init_attributes_none(self):
        """
        Test that the attributes are initially set to an empty dictionary when ``None`` is given.
        """

        profile = Profile(None)
        self.assertEqual({ }, profile.attributes)

    def test_init_default_attributes(self):
        """
        Test that when providing default attributes, they are stored.
        """

        profile = Profile({ 'known_as': 'Memphis', 'age': 26 })
        self.assertEqual({ 'known_as': 'Memphis', 'age': 26 }, profile.attributes)

    def test_attributes_overwrite(self):
        """
        Test that setting the attributes overwrites the previous attributes.
        """

        profile = Profile({ 'known_as': 'Memphis', 'age': 26 })
        self.assertEqual({ 'known_as': 'Memphis', 'age': 26 }, profile.attributes)

        profile.attributes = { 'name': 'Memphis Depay' }
        self.assertEqual({ 'name': 'Memphis Depay' }, profile.attributes)

    def test_attributes_overwrite_none(self):
        """
        Test that overwriting the attributes with ``None`` creates an empty dictionary of attributes.
        """

        profile = Profile({ 'known_as': 'Memphis', 'age': 26 })
        self.assertEqual({ 'known_as': 'Memphis', 'age': 26 }, profile.attributes)

        profile.attributes = None
        self.assertEqual({ }, profile.attributes)

    def test_attributes_add(self):
        """
        Test adding a new attribute to a profile.
        """

        profile = Profile()
        self.assertEqual({ }, profile.attributes)

        profile.attributes['name'] = 'Memphis Depay'
        self.assertEqual({ 'name': 'Memphis Depay' }, profile.attributes)

    def test_attributes_update(self):
        """
        Test update an existing attribute in a profile.
        """

        profile = Profile({ 'known_as': 'Memphis Depay', 'age': 26 })
        self.assertEqual({ 'known_as': 'Memphis Depay', 'age': 26 }, profile.attributes)

        profile.attributes['known_as'] = 'Memphis'
        self.assertEqual({ 'known_as': 'Memphis', 'age': 26 }, profile.attributes)

    def test_attributes_remove(self):
        """
        Test removing an existing attribute from a profile.
        """

        profile = Profile({ 'known_as': 'Memphis Depay', 'age': 26 })
        self.assertEqual({ 'known_as': 'Memphis Depay', 'age': 26 }, profile.attributes)

        del profile.attributes['age']
        self.assertEqual({ 'known_as': 'Memphis Depay' }, profile.attributes)
