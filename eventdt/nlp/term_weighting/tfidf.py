"""
The Term Frequency-Inverse Document Frequency (TF-IDF) term-weighting scheme is one of the most popular schemes.
The scheme promotes features that appear commonly in a document, but rarely outside of it.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__))
if path not in sys.path:
    sys.path.append(path)

from scheme import TermWeightingScheme
from local_schemes.tf import TF
from global_schemes.idf import IDF

class TFIDF(TermWeightingScheme):
	"""
	The Term Frequency-Inverse Document Frequency (TF-IDF) term-weighting scheme is one of the most popular schemes.
	The scheme promotes features that appear commonly in a document, but rarely outside of it.
	"""

	def __init__(self, idf, documents):
		"""
		Initialize the TF-IDF term-weighting scheme by supplying the TF and IDF schemes.

		:param idf: The IDF table used in conjunction with term weighting.
					The keys are the terms, and the corresponding values are the number of documents in which they appear.
		:type idf: dict
		:param documents: The number of documents in the IDF table.
		:type documents: int
		"""

		tf = TF()
		idf = IDF(idf, documents)
		super(TFIDF, self).__init__(tf, idf)
