"""
Run unit tests on the Compound class.
"""

import math
import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '..')
if path not in sys.path:
    sys.path.append(path)

from compound import Compound

class TestCompound(unittest.TestCase):
    """
    Test the Compound class.
    """

    def test_init_vectors_none(self):
        """
        Test that when initializing the :class:`~vsm.compound.Compound`, if `None` is provided instead of vectors, the dimensions are empty.
        """

        compound = Compound()
        self.assertEqual({ }, compound.dimensions)
        self.assertEqual(0, compound.size)

        compound = Compound(vectors=None)
        self.assertEqual({ }, compound.dimensions)
        self.assertEqual(0, compound.size)

    def test_init_vectors_empty(self):
        """
        Test that when initializing the :class:`~vsm.compound.Compound`, if an empty list of vectors is provided, the size is zero.
        """

        compound = Compound()
        self.assertEqual({ }, compound.dimensions)
        self.assertEqual(0, compound.size)

    def test_init_attributes_empty(self):
        """
        Test that by default, the :class:`~vsm.compound.Compound` has no attributes.
        """

        compound = Compound()
        self.assertEqual({ }, compound.attributes)

    def test_init_attributes(self):
        """
        Test that when initializing the :class:`~vsm.compound.Compound`, attributes are saved correctly.
        """

        attributes = { 'a': 1, 'b': 2 }
        compound = Compound(attributes=attributes)
        self.assertEqual(attributes, compound.attributes)
