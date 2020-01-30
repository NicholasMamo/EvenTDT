"""
Different term weighting schemes, used by the Document class to create documents from tokens.
"""

from abc import ABC, abstractmethod

import math

from .document import Document

class TermWeighting(ABC):
	"""
	This class defines a list of properties that schemes must have.
	"""

	@abstractmethod
	def create(self, tokens):
		"""
		Create a document from the given tokens.

		:param tokens: A list of tokens that can be converted into dimensions.
		:type tokens: list

		:return: A new document.
		:rtype: :class:`vector.nlp.document.Document`
		"""

		pass

class TF(TermWeighting):
	"""
	The Term Frequency (TF) is one of the simplest term weighting schemes that is used.
	The weight of a dimension is simply the number of times the feature appears.
	"""

	def create(self, tokens):
		"""
		Create a document from the given tokens.

		:param tokens: A list of tokens that can be converted into dimensions.
		:type tokens: list

		:return: A new document.
		:rtype: :class:`vector.nlp.document.Document`
		"""

		dimensions = { token: tokens.count(token) for token in tokens }
		document = Document(dimensions=dimensions)
		return document

class TFIDF(TermWeighting):
	"""
	Term Frequency - Inverse Document Frequency (TF-IDF) is one of the most common term weighting schemes.
	Apart from the TF component, the scheme promotes uncommon tokens.

	:ivar _idf: The IDF table used in conjunction with term weighting.
	:vartype _idf: dict
	"""

	def __init__(self, idf):
		"""
		Create the term-weighting scheme with the Inverse Document Frequency table.

		:param idf: The IDF table used in conjunction with term weighting.
		:type idf: dict
		"""

		# TODO ensure that it is a dictionary, and that it has a 'DOCUMENTS' attribute

		self._idf = idf

	def create(self, tokens):
		"""
		Create a document from the given tokens.

		:param tokens: A list of tokens that can be converted into dimensions.
		:type tokens: list

		:return: A new document.
		:rtype: :class:`vector.nlp.document.Document`
		"""

		dimensions = { token: tokens.count(token) * math.log(max(self._idf.get("DOCUMENTS"), 1) / self._idf.get(token, 1), 10) for token in tokens }
		document = Document(dimensions=dimensions)
		return document
