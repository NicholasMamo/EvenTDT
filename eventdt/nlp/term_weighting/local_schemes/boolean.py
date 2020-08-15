"""
A simple local term-weighting scheme that sets the weight of a term to 1 if it appears in the document.
The weight :math:`bool_{t,d}` of a feature :math:`t` is simply 1 if it appears in a document :math:`d`, 0 otherwise.

.. math::

	bool_{t,d} = \\begin{cases}
				     1 & \\text{if } t \\in d \\\\
					 0 & \\text{otherwise}
				 \\end{cases}
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from term_weighting import SchemeScorer

class Boolean(SchemeScorer):
	"""
	The boolean term-weighting scheme is one of the simplest term weighting schemes that is used.
	The weight of a feature is 1 if it appears in a document, 0 otherwise.
	"""

	def score(self, tokens, *args, **kwargs):
		"""
		Score the given tokens.
		The score is 1 if a feature appears in the document, 0 otherwise.

		:param tokens: The list of tokens to weigh.
		:type tokens: list of str

		:return: A dictionary with the tokens as the keys and the weights as the values.
		:rtype: dict
		"""

		weights = { token: 1 for token in list(set(tokens)) }
		return weights
