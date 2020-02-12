"""
The Inverse Document Frequency (IDF) global term-weighting scheme penalizes common terms.
The reasoning is that common terms are not informative.
Terms that appear often in one document but rarely outside characterize that document.

The IDF :math:`idf_{t}` for term :math:`t` is computed as follows:

.. math::

	idf_{t} = \\log{\\frac{N}{n_t}}

where :math:`N` is the total number of documents and :math:`n_t` is the total number of documents in :math:`N` that contain term :math:`t`.
"""

import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from scheme import SchemeScorer

class IDF(SchemeScorer):
	"""
	The Inverse Document Frequency (TF-IDF) is one of the most common term-weighting schemes.
	This scheme promotes uncommon tokens.

	:ivar idf: The IDF table used in conjunction with term weighting.
	:vartype idf: dict
	"""

	def __init__(self, idf, documents):
		"""
		Create the term-weighting scheme with the IDF table and the number of documents in that scheme.

		:param idf: The IDF table used in conjunction with term weighting.
					The keys are the terms, and the corresponding values are the number of documents in which they appear.
		:type idf: dict
		:param documents: The number of documents in the IDF table.
		:type documents: int

		:raises ValueError: When the document frequency of a term is higher than the number of the IDF documents.
		:raises ValueError: When the document frequency of a term is negative.
		:raises ValueError: When the number of documents is negative.
		"""

		if max(idf.values()) > documents:
			raise ValueError(f"The number of documents ({documents}) must be greater or equal to the most common term ({max(idf.values())})")

		if min(idf.values()) < 0:
			raise ValueError("The IDF values must be non-negative")

		if documents < 0:
			raise ValueError("The number of documents in the IDF must be non-negative")

		self.idf = idf
		self.documents = documents

	def score(self, tokens):
		"""
		Score the given tokens.

		:param tokens: The list of tokens to weigh.
		:type tokens: list of str

		:return: A dictionary with the tokens as the keys and the weights as the values.
		:rtype: dict
		"""

		weights = { token: math.log(self.documents / (self.idf.get(token, 0) + 1), 10) for token in tokens }
		return weights
