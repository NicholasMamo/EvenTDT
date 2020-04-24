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
"""
