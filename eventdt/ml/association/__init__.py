"""
Association rule mining is used to find items that are correlated.
Association rules are made up of an antecedent and a consequent:

.. math::

	\{X, Y\} => \{Z\}

where :math:`\{X, Y\}` is the antecedent and :math:`\{Z\}` is the consequent.
Both the antecedent and consequent are sets.

Key to association rule mining are:

	- Itemset: The antecedent and consequent,
	- Support: The fraction of transactions that contain all items in the itemset,
	- Confidence: The posterior probability of the support given the antecedent,
	- Lift: The ratio of confidence of the association rule divided by the consequent's support.
"""
