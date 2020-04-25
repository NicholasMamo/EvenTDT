"""
The implementation of the Apriori algorithm.
The Apriori algorithm mines for association rules breadth-first.
To restrain the depth of association rules, the Apriori algorithm accepts two parameters:

	1. `minsup`: The minimum support of an itemset to be part of a rule.
	2. `minconf`: The minimum confidence of an association rule to be accepted.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

import association

def apriori(transactions, minsup=0, minconf=0):
	"""
	Perform the Apriori algorithm over the given transactions.

	:param transactions: A list of transactions, each containing any number of items.
	:type transactions: list of list or list of set
	:param minsup: The minimum support of an itemset to be part of a rule.
				   It is bound between 0 and 1 and is inclusive.
	:type minsup: float
	:param minconf: The minimum confidence of an association rule to be accepted.
				   It is bound between 0 and 1 and is inclusive.
	:type minconf: float

	:return: A list of association rules.
			 Each rule is a two-tuple made up of the antecedent and consequent respectively.
	:rtype: list of tuple

	:raises ValueError: When the minimum support is not between 0 and 1.
	:raises ValueError: When the minimum confidence is not between 0 and 1.
	"""

	if not 0 <= minsup <= 1:
		raise ValueError(f"The minimum support needs to be between 0 and 1; received {minsup}")

	if not 0 <= minconf <= 1:
		raise ValueError(f"The minimum confidence needs to be between 0 and 1; received {minsup}")

def get_itemsets(itemsets, length):
	"""
	Construct new itemsets from the given ones.
	All new itemsets have the given length.

	:param itemsets: The itemset from which to which to create the new itemsets.
	:type itemsets: list of list or list of set
	:param length: The length of the new itemsets.
				   This is usually one bigger than the length of any given itemset.
	:type length: int

	:return: The new itemsets, created by combining the given itemsets.
			 All itemsets have the same length, as given in the parameters.
	:rtype: list of set

	:raises ValueError: When the length is not an integer.
	:raises ValueError: When the length is not positive.
	"""

	if type(length) is not int and length % 1:
		raise ValueError(f"The itemset length has to be an integer; received {length} ({type(length)})")

	if length <= 0:
		raise ValueError(f"The itemset length has to be positive; received {length}")

	"""
	Convert all the itemsets to sets first.
	Then, make sure that there are no duplicate itemsets.
	"""
	itemsets = [ set(itemset) for itemset in itemsets ]
	unique_itemsets = [ ]
	for itemset in itemsets:
		if itemset not in unique_itemsets:
			unique_itemsets.append(itemset)
	itemsets = unique_itemsets

	"""
	Expand the itemsets.
	"""
	expanded = [ ]
	for n, itemset_1 in enumerate(itemsets):
		for itemset_2 in itemsets[n + 1:]:
			expanded.append(itemset_1.union(itemset_2))

	"""
	Filter out itemsets that do not match the given length.
	"""
	expanded = [ itemset for itemset in expanded if len(itemset) == length ]
	return expanded

def filter_itemsets(transactions, itemsets, minsup):
	"""
	Filter the itemsets to retain only those having a minimum support.

	:param transactions: A list of transactions, each containing any number of items.
	:type transactions: list of list or list of set
	:param itemsets: The itemsets to filter.
	:type itemsets: list of list or list of set
	:param minsup: The minimum support of an itemset to be part of a rule.
				   It is bound between 0 and 1 and is inclusive.
	:type minsup: float

	:return: The filtered itemsets.
			 All itemsets have at least a support equivalent to the given minimum.
	:rtype: list of set

	:raises ValueError: When the minimum support is not between 0 and 1.
	"""

	if not 0 <= minsup <= 1:
		raise ValueError(f"The minimum support needs to be between 0 and 1; received {minsup}")

	return [ itemset for itemset in itemsets if association.support(transactions, itemset) >= minsup ]
