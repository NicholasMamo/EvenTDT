"""
The Term Frequency (TF) local term-weighting scheme assigns a weight to each term according to the number of times that it appears.
The term frequency :math:`tf_{t,d}` of a feature :math:`t` is equivalent to its frequency :math:`f_{t,d}` in document :math:`d`:

.. math::

	tf_{t,d} = f_{t,d}
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from term_weighting import SchemeScorer

class TF(SchemeScorer):
	"""
	The Term Frequency (TF) term-weighting scheme is one of the simplest term weighting schemes that is used.
	The weight of a dimension is simply the number of times that the feature appears.
	"""

	def score(self, tokens, *args, **kwargs):
		"""
		Score the given tokens.
		The score is equal to the frequency of the token in the list.

		:param tokens: The list of tokens to weigh.
		:type tokens: list of str

		:return: A dictionary with the tokens as the keys and the weights as the values.
		:rtype: dict
		"""

		weights = { token: tokens.count(token) for token in tokens }
		return weights
