"""
The filler global term-weighting scheme is used when there is no need for a global term-weighting scheme.
The scheme assigns the same score :math:`fill_{t,d}` to all terms :math:`t` if they appear in the document :math:`d`, 0 otherwise:

.. math::

	fill_{t,d} = \\begin{cases}
				     1 & \\text{if } t \\in d \\\\
					 0 & \\text{otherwise}
				 \\end{cases}
"""

import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from weighting import SchemeScorer

class Filler(SchemeScorer):
	"""
	The filler global term-weighting scheme is used when there is no need for a global term-weighting scheme.
	The scheme assigns the same score to all terms: 1.
	"""

	def score(self, tokens):
		"""
		Score the given tokens.

		:param tokens: The list of tokens to weigh.
		:type tokens: list of str

		:return: A dictionary with the tokens as the keys and the weights as the values.
		:rtype: dict
		"""

		weights = { token: 1 for token in list(set(tokens)) }
		return weights
