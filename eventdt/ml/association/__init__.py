"""
Association rule mining is used to find items that are correlated in transactions.
Association rules are made up of an antecedent and a consequent:

.. math::

	\{X, Y\} \\implies \{Z\}

where :math:`\{X, Y\}` is the antecedent and :math:`\{Z\}` is the consequent.
Both the antecedent and consequent are sets.

Key to association rule mining are transactions, the itemset, the support, the confidence and the lift of association rules.

Association rules are built from transactions.
Each transaction has associated with it a number of items.

The itemset is the set comprising all items in the antecedent and consequent.
For example, the itemset of :math:`\{X, Y\} \\implies \{Z\}` is :math:`\{X, Y, Z\}`.

The support of an item or a set of items is the number of transactions in which it appears:

.. math::

	s_X = \\frac{|\{ t | X \\in t, t \\in T \}|}{|T|}

where :math:`s_X` is the support of :math:`s_X` and :math:`T` is the set of transactions.

Confidence is calculated for association rules.
It is the posterior probability of the consequent given the antecedent:

.. math::

	c_{\{X, Y\} \\implies \{Z\}} = \\frac{s_{\{X, Y, Z\}}}{s_{\{X, Y\}}}

where :math:`c_{\{X, Y\} \\implies \{Z\}}` is the confidence of the association rule :math:`\{X, Y\} \\implies \{Z\}`.

Lift avoids overweighting items by computing the ratio of the rule's confidence as a function of the consequent's support.
If the antecedent really contributes to the consequent, the ratio will be greater than 1.
Otherwise, if the antecedent doesn't contribute more to the consequent with its presence, the lift will be less than 1.

.. math::

	l_{\{X, Y\} \\implies \{Z\}} = \\frac{s_{\{X, Y, Z\}}}{s_{\{X, Y\}} \\cdot s_{\{Z\}}}

where :math:`l_{\{X, Y\} \\implies \{Z\}}` is the lift of the association rule.
Lift can also be defined in terms of the confidence:

.. math::

	l_{\{X, Y\} \\implies \{Z\}} = \\frac{c_{\{X, Y\} \\implies \{Z\}}}{s_{\{Z\}}}
"""

def support(transactions, itemset):
	"""
	Calculate the support of the itemset in the given transactions.

	The support of an item or a set of items is the number of transactions in which it appears:

	.. math::

		s_X = \\frac{|\{ t | X \\in t, t \\in T \}|}{|T|}

	where :math:`s_X` is the support of :math:`s_X` and :math:`T` is the set of transactions.

	:param transactions: A list of transactions, each containing any number of items.
	:type transactions: list of list or list of set
	:param itemset: The itemset for which to calculate the support.
	:type itemset: list or set

	:return: The support of the itemset in the given transactions.
	:rtype: float
	"""

	if not transactions:
		return 0

	cover = [ transaction for transaction in transactions
			  if all( item in transaction for item in itemset ) ]
	return len(cover) / len(transactions)

def confidence(transactions, antecedent, consequent):
	"""
	Calculate the confidence for the given antecedent and consequent in the given transactions.

	It is the posterior probability of the consequent given the antecedent:

	.. math::

		c_{\{X, Y\} \\implies \{Z\}} = \\frac{s_{\{X, Y, Z\}}}{s_{\{X, Y\}}}

	where :math:`c_{\{X, Y\} \\implies \{Z\}}` is the confidence of the association rule :math:`\{X, Y\} \\implies \{Z\}`.

	:param transactions: A list of transactions, each containing any number of items.
	:type transactions: list of list or list of set
	:param antecedent: The antecedent is the condition for the association rule.
					   It is presented as a set of items.
	:type antecedent: list or set
	:param consequent: The consequent is the conclusion of the antecedent.
	:type consequent: list or set

	:return: The confidence of the association rule.
	:rtype: float
	"""

	antecedent_support = support(transactions, antecedent)
	if antecedent_support > 0:
		return support(transactions, set( set(antecedent).union(set(consequent)) ))/antecedent_support

	return 0

def lift(transactions, antecedent, consequent):
	"""
	Calculate the lift for the given antecedent and consequent in the given transactions.

	Lift avoids overweighting items by computing the ratio of the rule's confidence as a function of the consequent's support.
	If the antecedent really contributes to the consequent, the ratio will be greater than 1.
	Otherwise, if the antecedent doesn't contribute more to the consequent with its presence, the lift will be less than 1.

	.. math::

		l_{\{X, Y\} \\implies \{Z\}} = \\frac{s_{\{X, Y, Z\}}}{s_{\{X, Y\}} \\cdot s_{\{Z\}}}

	where :math:`l_{\{X, Y\} \\implies \{Z\}}` is the lift of the association rule.
	Lift can also be defined in terms of the confidence:

	.. math::

		l_{\{X, Y\} \\implies \{Z\}} = \\frac{c_{\{X, Y\} \\implies \{Z\}}}{s_{\{Z\}}}

	:param transactions: A list of transactions, each containing any number of items.
	:type transactions: list of list or list of set
	:param antecedent: The antecedent is the condition for the association rule.
					   It is presented as a set of items.
	:type antecedent: list or set
	:param consequent: The consequent is the conclusion of the antecedent.
	:type consequent: list or set

	:return: The lift of the association rule.
	:rtype: float
	"""

	consequent_support = support(transactions, consequent)
	if consequent_support > 0:
		return confidence(transactions, antecedent, consequent) / consequent_support

	return 0