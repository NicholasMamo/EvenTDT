"""
The Term Frequency-Inverse Document Frequency (TF-IDF) term-weighting scheme is one of the most popular schemes.
The scheme promotes features that appear commonly in a document, but rarely outside of it.
The TFIDF is simply the multiplication of the :class:`~nlp.term_weighting.local_schemes.tf.TF` and :class:`~nlp.term_weighting.global_schemes.idf.IDF` term-weighting schemes:
The weight :math:`tfidf_{t,d}` of term :math:`idf_{t}` in document :math:`d` is computed as follows:

.. math::

	tfidf_{t,d} = tf_{t,d} \\cdot idf_{t}
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from objects.exportable import Exportable
from nlp.term_weighting import TermWeightingScheme

class TFIDF(Exportable, TermWeightingScheme):
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

		# NOTE: The imports are located here because of circular dependencies
		from local_schemes.tf import TF
		from global_schemes.idf import IDF

		tf = TF()
		idf = IDF(idf, documents)
		super(TFIDF, self).__init__(tf, idf)

	def to_array(self):
		"""
		Export the TF-IDF as an associative array.

		:return: The TF-IDF as an associative array.
		:rtype: dict
		"""

		return {
			'class': str(TFIDF),
			'idf': self.global_scheme.to_array(),
		}

	@staticmethod
	def from_array(array):
		"""
		Create an instance of the TF-IDF from the given associative array.

		:param array: The associative array with the attributes to create the TF-IDF.
		:type array: dict

		:return: A new instance of the TF-IDF with the same attributes stored in the object.
		:rtype: :class:`~nlp.term_weighting.tfidf.TFIDF`
		"""

		return TFIDF(idf=array.get('idf').get('idf'), documents=array.get('idf').get('documents'))
