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

from evaluation import unique, is_precise, precise, recalled, precision, pk, recall, f1

class TestPackage(unittest.TestCase):
    """
    Test the functionality of the evaluation package-level functions.
    """

    def test_unique_empty(self):
        """
        Test that the unique list of an empty list is another empty list.
        """

        self.assertEqual([ ], unique([ ]))

    def test_unique_all_unique(self):
        """
        Test that the unique list of a list of unique items is identical.
        """

        items = list(range(5))
        self.assertEqual(items, unique(items))

    def test_unique_repetition(self):
        """
        Test that the unique list of a list does not contain duplicates.
        """

        items = list(range(5)) + [ 4 ]
        self.assertEqual(list(range(5)), unique(items))

    def test_unique_same_order(self):
        """
        Test that the unique list of a list keeps the original order.
        """

        items = [ 1, 4, 2, 1, 3, 4, 5 ]
        self.assertEqual([ 1, 4, 2, 3, 5 ], unique(items))

    def test_is_precise_in_gold(self):
        """
        Test that all items in the gold set are precise.
        """

        gold = range(0, 10)
        self.assertTrue(all( is_precise(item, gold) for item in gold ))

    def test_is_precise_not_in_gold(self):
        """
        Test that an item that is not in the gold set is not precise.
        """

        self.assertFalse(is_precise(10, range(0, 10)))

    def test_is_precise_empty_gold(self):
        """
        Test that when the gold set is empty, all items are False.
        """

        self.assertFalse(is_precise(10, [ ]))

    def test_precise_empty(self):
        """
        Test that when the item set is empty, the precise items is also an empty set.
        """

        self.assertEqual(set(), precise([ ], range(0, 5)))

    def test_precise_empty_gold(self):
        """
        Test that when the gold set is empty, the precise items is also an empty set.
        """

        self.assertEqual(set(), precise(range(0, 5), [ ]))

    def test_precise_identical_sets(self):
        """
        Test that when the item set is the same as the gold set, the same items are returned.
        """

        self.assertEqual(set(range(0, 5)), precise(range(0, 5), range(0, 5)))

    def test_precise_items_subset(self):
        """
        Test that when the item set is a subset of the gold set, only the items that are also in the gold set are returned.
        """

        self.assertEqual(set(range(0, 3)), precise(range(0, 3), range(0, 5)))

    def test_precise_gold_subset(self):
        """
        Test that when the gold set is a subset of the items set, the items in the gold set are returned.
        """

        self.assertEqual(set(range(0, 3)), precise(range(0, 5), range(0, 3)))

    def test_precise_list_set(self):
        """
        Test that the precise function accepts lists and sets.
        """

        self.assertEqual(set(range(0, 3)), precise(list(range(0, 5)), list(range(0, 3))))
        self.assertEqual(set(range(0, 3)), precise(set(range(0, 5)), list(range(0, 3))))
        self.assertEqual(set(range(0, 3)), precise(list(range(0, 5)), set(range(0, 3))))
        self.assertEqual(set(range(0, 3)), precise(set(range(0, 5)), set(range(0, 3))))

    def test_precise_duplicate_items(self):
        """
        Test that the precise function ignores duplicates in the item set.
        """

        self.assertEqual(set(range(0, 3)), precise(list(range(0, 5)) + list(range(0, 5)), range(0, 3)))

    def test_precise_duplicate_gold(self):
        """
        Test that the precise function ignores duplicates in the gold set.
        """

        self.assertEqual(set(range(0, 3)), precise(range(0, 5), list(range(0, 3)) + list(range(0, 3))))

    def test_recalled_empty(self):
        """
        Test that when the item set is empty, the recalled items is also an empty set.
        """

        self.assertEqual(set(), recalled([ ], range(0, 5)))

    def test_recalled_empty_gold(self):
        """
        Test that when the gold set is empty, the recalled items is also an empty set.
        """

        self.assertEqual(set(), recalled(range(0, 5), [ ]))

    def test_recalled_identical_sets(self):
        """
        Test that when the item set is the same as the gold set, the same items are returned.
        """

        self.assertEqual(set(range(0, 5)), recalled(range(0, 5), range(0, 5)))

    def test_recalled_items_subset(self):
        """
        Test that when the item set is a subset of the gold set, only the items that are also in the gold set are returned.
        """

        self.assertEqual(set(range(0, 3)), recalled(range(0, 3), range(0, 5)))

    def test_recalled_gold_subset(self):
        """
        Test that when the gold set is a subset of the items set, the items in the gold set are returned.
        """

        self.assertEqual(set(range(0, 3)), recalled(range(0, 5), range(0, 3)))

    def test_recalled_list_set(self):
        """
        Test that the recalled function accepts lists and sets.
        """

        self.assertEqual(set(range(0, 3)), recalled(list(range(0, 5)), list(range(0, 3))))
        self.assertEqual(set(range(0, 3)), recalled(set(range(0, 5)), list(range(0, 3))))
        self.assertEqual(set(range(0, 3)), recalled(list(range(0, 5)), set(range(0, 3))))
        self.assertEqual(set(range(0, 3)), recalled(set(range(0, 5)), set(range(0, 3))))

    def test_recalled_duplicate_items(self):
        """
        Test that the recalled function ignores duplicates in the item set.
        """

        self.assertEqual(set(range(0, 3)), recalled(list(range(0, 5)) + list(range(0, 5)), range(0, 3)))

    def test_recalled_duplicate_gold(self):
        """
        Test that the recalled function ignores duplicates in the gold set.
        """

        self.assertEqual(set(range(0, 3)), recalled(range(0, 5), list(range(0, 3)) + list(range(0, 3))))

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

    def test_precision_gold_subset(self):
        """
        Test that when the gold set is a subset of the items, the precision is less than 1.
        """

        items = list(range(0, 5))
        gold = items[:3]
        self.assertLess(precision(items, gold), 1)

    def test_precision_items_subset(self):
        """
        Test that when the item set is a subset of the gold set, the precision is equal to 1.
        """

        gold = list(range(0, 5))
        items = gold[:3]
        self.assertEqual(1, precision(items, gold))

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

    def test_pk_k_negative(self):
        """
        Test that the P@k function raises a ValueError when k is negative.
        """

        self.assertRaises(ValueError, pk, range(0, 5), range(0, 5), -1)

    def test_pk_k_zero(self):
        """
        Test that the P@k function raises a ValueError when k is zero.
        """

        self.assertRaises(ValueError, pk, range(0, 5), range(0, 5), 0)

    def test_pk_k_one(self):
        """
        Test that the P@k function accepts a value of one for k.
        """

        self.assertTrue(pk(range(0, 5), range(0, 5), 1))

    def test_pk_none(self):
        """
        Test that the P@k function accepts a value of `None` for k.
        """

        self.assertTrue(pk(range(0, 5), range(0, 5)))

    def test_pk_empty(self):
        """
        Test that when the item list is empty, the precision is zero.
        """

        self.assertEqual(0, pk([ ], range(0, 5), 1))

    def test_pk_none_empty_none(self):
        """
        Test that when the item set is empty and `None` is given as k, the function returns a dictionary.
        """

        self.assertEqual({ }, pk([ ], range(0, 5)))

    def test_pk_inclusive(self):
        """
        Test that the P@k function includes _k_ items in the calculation.
        """

        self.assertEqual(0.6, pk(range(0, 5), range(0, 3), 5))

    def test_pk_order(self):
        """
        Test that the P@k function bases the calculation on the first items.
        """

        self.assertEqual(1, pk(range(4, 9), range(0, 5), 1))
        self.assertEqual(0.5, pk(range(4, 9), range(0, 5), 2))

    def test_pk_large_k(self):
        """
        Test that when k is large, the P@k function ignores the extra items.
        """

        self.assertEqual(pk(range(4, 9), range(0, 7), 5), pk(range(4, 9), range(0, 7), 25))

    def test_pk_example(self):
        """
        Test the P@k function with an example.
        """

        self.assertEqual(1, pk(range(4, 9), range(0, 7), 1))
        self.assertEqual(1, pk(range(4, 9), range(0, 7), 2))
        self.assertEqual(1, pk(range(4, 9), range(0, 7), 3))
        self.assertEqual(0.75, pk(range(4, 9), range(0, 7), 4))
        self.assertEqual(0.6, pk(range(4, 9), range(0, 7), 5))
        self.assertEqual(0.6, pk(range(4, 9), range(0, 7), 6))

    def test_pk_none_duplicates(self):
        """
        Test that the P@k function ignores duplicates when `None` is given as k.
        """

        items, gold = list(range(0, 5)) + [ 4 ], range(4, 9)
        p = pk(items, gold)
        self.assertEqual(5, len(p))
        self.assertEqual(1/5, p[max(p)])

    def test_pk_none_example(self):
        """
        Test the P@k function with `None` as k.
        """

        items, gold = [ 3, 5, 7, 9, 1], range(4, 9)
        p = pk(items, gold)
        self.assertEqual({
            1: 0,
            2: 1/2,
            3: 2/3,
            4: 2/4,
            5: 2/5
        }, p)

    def test_recall_empty(self):
        """
        Test that the recall is 0 when the items and the gold set are empty.
        """

        self.assertEqual(0, recall([ ], [ ]))

    def test_recall_empty_items(self):
        """
        Test that the recall of an empty item set is 0.
        """

        self.assertEqual(0, recall([ ], [ 1 ]))

    def test_recall_empty_gold(self):
        """
        Test that the recall is 0 when the gold set is empty.
        """

        self.assertEqual(0, recall([ 1 ], [ ]))

    def test_recall_identical_set(self):
        """
        Test that the recall is 1 when the item set and the gold set are identical.
        """

        self.assertEqual(1, recall(set(range(10)), set(range(10))))

    def test_recall_identical_list(self):
        """
        Test that the recall is 1 when the item list and the gold list are identical.
        """

        self.assertEqual(1, recall(list(range(10)), list(range(10))))

    def test_recall_gold_subset(self):
        """
        Test that when the gold set is a subset of the items, the recall is 1.
        """

        items = list(range(0, 5))
        gold = items[:3]
        self.assertEqual(1, recall(items, gold))

    def test_recall_items_subset(self):
        """
        Test that when the item set is a subset of the gold set, the recall is less than 1.
        """

        gold = list(range(0, 5))
        items = gold[:3]
        self.assertLess(recall(items, gold), 1)

    def test_recall_order_irrelevant(self):
        """
        Test that the order of the item and gold set items is irrelevant.
        """

        self.assertEqual(1, recall(list(range(10)), list(range(10))[::-1]))

    def test_recall_type(self):
        """
        Test that the variable type matters when calculating recall.
        """

        self.assertEqual(0, recall([ '1' ], [ 1 ]))
        self.assertEqual(0, recall([ 1 ], [ '1' ]))
        self.assertEqual(1, recall([ 1 ], [ 1 ]))
        self.assertEqual(0, recall([ '' ], [ None ]))
        self.assertEqual(0, recall([ '' ], [ 0 ]))
        self.assertEqual(1, recall([ None ], [ None ]))

    def test_recall_example(self):
        """
        Test calculating recall with an example.
        """

        self.assertEqual(0.6, recall(range(0, 3), range(0, 5)))

    def test_recall_duplicate_item(self):
        """
        Test that when calculating recall, duplicate elements are removed.
        """

        self.assertEqual(0.6, recall(list(range(0, 3)) + list(range(0, 3)), range(0, 5)))

    def test_recall_duplicate_gold_item(self):
        """
        Test that when calculating recall, duplicate elements are removed from the gold set.
        """

        self.assertEqual(0.6, recall(range(0, 3), list(range(0, 5)) + list(range(0, 5))))

    def test_f1_precision_negative(self):
        """
        Test that when the precision is negative, the F1 raises a ValueError.
        """

        self.assertRaises(ValueError, f1, -1, 0.5)

    def test_f1_precision_zero(self):
        """
        Test that when the precision is zero, the F1 does not raise a ValueError.
        """

        self.assertEqual(0, f1(0, 0.5))

    def test_f1_precision_one(self):
        """
        Test that when the precision is one, the F1 does not raise a ValueError.
        """

        self.assertTrue(f1(1, 0.5))

    def test_f1_precision_large(self):
        """
        Test that when the precision is greater than 1, the F1 raises a ValueError.
        """

        self.assertRaises(ValueError, f1, 2, 0.5)

    def test_f1_recall_negative(self):
        """
        Test that when the recall is negative, the F1 raises a ValueError.
        """

        self.assertRaises(ValueError, f1, 0.5, -1)

    def test_f1_recall_zero(self):
        """
        Test that when the recall is zero, the F1 does not raise a ValueError.
        """

        self.assertEqual(0, f1(0.5, 0))

    def test_f1_recall_one(self):
        """
        Test that when the recall is one, the F1 does not raise a ValueError.
        """

        self.assertTrue(f1(0.5, 1))

    def test_f1_recall_large(self):
        """
        Test that when the recall is greater than 1, the F1 raises a ValueError.
        """

        self.assertRaises(ValueError, f1, 0.5, 2)

    def test_f1_precision_recall_zero(self):
        """
        Test that when precision and recall are both 0, the F1 is also 0.
        """

        self.assertEqual(0, f1(0, 0))

    def test_f1_precision_only_zero(self):
        """
        Test that when precision is zero, F1 is also zero.
        """

        self.assertEqual(0, f1(0, 1))

    def test_f1_recall_only_zero(self):
        """
        Test that when recall is zero, F1 is also zero.
        """

        self.assertEqual(0, f1(1, 0))

    def test_f1_precision_recall_one(self):
        """
        Test that when precision and recall are both one, F1 is also one.
        """

        self.assertEqual(1, f1(1, 1))

    def test_f1_example(self):
        """
        Test the F1 function with worked examples.
        """

        self.assertEqual(0.5, f1(0.5, 0.5))
        self.assertEqual(0.421, round(f1(0.308, 0.667), 3))
