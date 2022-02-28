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
from vector import Vector
import vector_math

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

    def test_init_with_vectors(self):
        """
        Test that when creating the :class:`~vsm.compound.Compound` with vectors, they are added correctly and the size set correctly.
        """

        vectors = [ Vector({ 'a': 1, 'b': 2 }), Vector({ 'c': 3, 'd': 1 }) ]

        compound = Compound(vectors)
        self.assertEqual(len(vectors), compound.size)
        self.assertEqual(vector_math.concatenate(vectors).dimensions, compound.dimensions)

    def test_init_with_vectors_like_add(self):
        """
        Test that creating the :class:`~vsm.compound.Compound` with vectors is like creating an empty :class:`~vsm.compound.Compound` and then adding vectors.
        """

        vectors = [ Vector({ 'a': 1, 'b': 2 }), Vector({ 'c': 3, 'd': 1 }) ]

        c1 = Compound(vectors)
        c2 = Compound()
        c2.add(*vectors)
        self.assertEqual(c2.dimensions, c1.dimensions)

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

    def test_add_none(self):
        """
        Test that when adding no new vectors, the dimensions and size remain unchanged.
        """

        compound = Compound()
        self.assertEqual(0, compound.size)
        compound.add()
        self.assertEqual(0, compound.size)
        self.assertEqual({ }, compound.dimensions)

    def test_add_one_to_empty(self):
        """
        Test that when adding one vector to an empty :class:`~vsm.compound.Compound`, the dimensions are equal to the added vector.
        """

        vector = Vector({ 'a': 1, 'b': 2 })

        compound = Compound()
        self.assertEqual(0, compound.size)
        compound.add(vector)
        self.assertEqual(1, compound.size)
        self.assertEqual(vector.dimensions, compound.dimensions)

    def test_add_multiple_to_empty(self):
        """
        Test that when adding multiple vectors to an empty :class:`~vsm.compound.Compound`, the dimension are equal to the aggregate of all.
        """

        vectors = [ Vector({ 'a': 1, 'b': 2 }), Vector({ 'a': 3, 'b': 1 }) ]

        compound = Compound()
        self.assertEqual(0, compound.size)
        compound.add(*vectors)
        self.assertEqual(len(vectors), compound.size)
        self.assertEqual(vector_math.concatenate(vectors).dimensions, compound.dimensions)

    def test_add_all_dimensions(self):
        """
        Test that when adding multiple vectors to a :class:`~vsm.compound.Compound`, all dimensions are retained.
        """

        vectors = [ Vector({ 'a': 1, 'b': 2 }), Vector({ 'c': 3, 'd': 1 }) ]
        dimensions = [ dimension for vector in vectors for dimension in vector.dimensions ]

        compound = Compound()
        self.assertEqual(0, compound.size)
        compound.add(*vectors)
        self.assertEqual(len(vectors), compound.size)
        self.assertEqual(dimensions, list(compound.dimensions.keys()))

    def test_add_update(self):
        """
        Test updating the vectors in the :class:`~vsm.compound.Compound`.
        """

        v1, v2 = Vector({ 'a': 1, 'b': 2 }), Vector({ 'c': 3, 'd': 1 })
        compound = Compound()
        compound.add(v1)
        self.assertEqual(v1.dimensions, compound.dimensions)

        compound.add(v2)
        self.assertEqual(2, compound.size)
        self.assertEqual(vector_math.concatenate([ v1, v2 ]).dimensions, compound.dimensions)

    def test_add_update_incremental(self):
        """
        Test that updating the :class:`~vsm.compound.Compound` is the same as adding them at once.
        """

        vectors = [ Vector({ 'a': 1, 'b': 2 }), Vector({ 'c': 3, 'd': 1 }) ]
        c1 = Compound()
        c1.add(*vectors)

        c2 = Compound()
        for vector in vectors:
            c2.add(vector)

        self.assertEqual(c1.dimensions, c2.dimensions)

    def test_add_update_none(self):
        """
        Test that updating a :class:`~vsm.compound.Compound` with nothing does not change the or size dimensions.
        """

        vectors = [ Vector({ 'a': 1, 'b': 2 }), Vector({ 'c': 3, 'd': 1 }) ]
        compound = Compound()
        compound.add(*vectors)
        dimensions = dict(compound.dimensions)
        compound.add()
        self.assertEqual(2, len(vectors))
        self.assertEqual(dimensions, compound.dimensions)

    def test_add_update_keeps_previous_dimensions(self):
        """
        Test that updating a :class:`~vsm.compound.Compound` does not overwrite the previous vectors' dimensions.
        """

        v1, v2 = Vector({ 'a': 1, 'b': 2 }), Vector({ 'c': 3, 'd': 1 })
        compound = Compound()
        compound.add(v1)
        self.assertEqual(1, compound.size)
        self.assertEqual(v1.dimensions, compound.dimensions)

        compound.add(v2)
        self.assertEqual(2, compound.size)
        self.assertTrue(all( compound.dimensions[dimension] == v1.dimensions[dimension]
                             for dimension in v1.dimensions ))
