"""
The implementation of the Apriori algorithm.
The Apriori algorithm mines for association rules breadth-first.
To restrain the depth of association rules, the Apriori algorithm accepts two parameters:

	1. `minsup`: The minimum support of an itemset to be part of a rule.
	2. `minconf`: The minimum confidence of an association rule to be accepted.
"""

def apriori(transactions, minsup=0, minconf=0):
	"""
	Perform the Apriori algorithm over the given transactions.

	:param transactions: A list of transactions, each containing any number of items.
	:type transactions: list of list or list of set
	:param minsup: The minimum support of an itemset to be part of a rule.
				   It is bound between 0 and 1.
	:type minsup: float
	:param minconf: The minimum confidence of an association rule to be accepted.
				   It is bound between 0 and 1.
	:type minconf: float

	:return: A list of association rules.
			 Each rule is a two-tuple made up of the antecedent and consequent respectively.
	:rtype: list of tuple

	:raises ValueError: When the minimum support is not bound between 0 and 1.
	:raises ValueError: When the minimum confidence is not bound between 0 and 1.
	"""

	if not 0 <= minsup <= 1:
		raise ValueError(f"The minimum support needs to be between 0 and 1; received {minsup}")

	if not 0 <= minconf <= 1:
		raise ValueError(f"The minimum confidence needs to be between 0 and 1; received {minsup}")
