"""
Test the functionality of the evaluation package-level functions.
"""

import json
import os
import string
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..', '..'),
          os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from evaluation import precision

class TestPackage(unittest.TestCase):
    """
    Test the functionality of the evaluation package-level functions.
    """

    def test_precision_empty(self):
        """
        Test that the precision is 0 when the items and the gold set are empty.
        """

        self.assertEqual(0, precision([ ], [ ]))

    def test_precision_empty_items(self):
        """
        Test that the precision of an empty item set is 0.
        """

        self.assertEqual(0, precision([ ], [ 1 ]))

    def test_precision_empty_gold(self):
        """
        Test that the precision is 0 when the gold set is empty.
        """

        self.assertEqual(0, precision([ 1 ], [ ]))

    def test_precision_identical_set(self):
        """
        Test that the precision is 1 when the item set and the gold set are identical.
        """

        self.assertEqual(1, precision(set(range(10)), set(range(10))))

    def test_precision_identical_list(self):
        """
        Test that the precision is 1 when the item list and the gold list are identical.
        """

        self.assertEqual(1, precision(list(range(10)), list(range(10))))

    def test_precision_order_irrelevant(self):
        """
        Test that the order of the item and gold set items is irrelevant.
        """

        self.assertEqual(1, precision(list(range(10)), list(range(10))[::-1]))

    def test_precision_type(self):
        """
        Test that the variable type matters when calculating precision.
        """

        self.assertEqual(0, precision([ '1' ], [ 1 ]))
        self.assertEqual(0, precision([ 1 ], [ '1' ]))
        self.assertEqual(1, precision([ 1 ], [ 1 ]))
        self.assertEqual(0, precision([ '' ], [ None ]))
        self.assertEqual(0, precision([ '' ], [ 0 ]))
        self.assertEqual(1, precision([ None ], [ None ]))

    def test_precision_example(self):
        """
        Test calculating precision with an example.
        """

        self.assertEqual(0.6, precision(range(0, 5), range(0, 3)))

    def test_precision_duplicate_item(self):
        """
        Test that when calculating precision, duplicate elements are removed.
        """

        self.assertEqual(0.6, precision(list(range(0, 5)) + list(range(0, 5)), range(0, 3)))

    def test_precision_duplicate_gold_item(self):
        """
        Test that when calculating precision, duplicate elements are removed from the gold set.
        """

        self.assertEqual(0.6, precision(range(0, 5), list(range(0, 3)) + list(range(0, 3))))
