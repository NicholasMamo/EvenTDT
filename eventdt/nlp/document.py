"""
Documents are the basis in NLP tasks.
The :class:`~nlp.document.Document` class builds on the :class:`~vsm.vector.Vector` class.
In addition to the normal VSM functionality, it stores the original text for any later changes.

Creating documents is a two-step process.
First, the text needs to be converted into tokens using the :class:`~nlp.tokenizer.Tokenizer` class.
Second, those tokens need to be weighted using a :class:`~nlp.term_weighting.scheme.TermWeightingScheme`, transforming them into document features, or vector dimensions.
"""

import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
	sys.path.insert(1, path)

from vsm import Vector

class Document(Vector):
	"""
	The :class:`~nlp.document.Document` class is based on the :class:`~vsm.vector.Vector` class. class.
	The main addition is the text field for any later changes.

	:ivar text: The document's original text.
	:vartype text: str
	"""

	def __init__(self, text='', dimensions=None, scheme=None, *args, **kwargs):
		"""
		Initialize the document with the text and optional dimensions.
		Any other arguments or keyword arguments are passed on to the :class:`~vsm.vector.Vector` constructor.

		:param text: The document's text.
		:type text: str
		:param dimensions: The initial dimensions of the document.
						   If a list is provided, it is assumed that they are tokens.
						   The dimensions are then created from this list using the given scheme.
		:type dimensions: list or dict
		:param scheme: The term-weighting scheme that is used to convert the tokens into dimensions.
					   If `None` is given, the :class:`~nlp.term_weighting.TermWeighting.TF` term-weighting scheme is used.
		:type scheme: None or :class:`~nlp.term_weighting.TermWeighting`
		"""

		"""
		If a list is provided, assume that it is a list of tokens.
		This list of tokens is converted into a dictionary representing the dimensions of the vector.
		The conversion is carried out by the term-weighting scheme.
		"""
		if type(dimensions) is list:
			from nlp.term_weighting.tf import TF # NOTE: The import is located here because of circular dependencies
			scheme = scheme if scheme is not None else TF()
			dimensions = scheme.create(dimensions).dimensions

		super(Document, self).__init__(dimensions, *args, **kwargs)
		self.text = text

	def __str__(self):
		"""
		Get the string representation of the document.
		This is equivalent to the document's text.

		:return: The text of the document.
		:rtype: str
		"""

		return self.text

	def to_array(self):
		"""
		Export the document as an associative array.

		:return: The document as an associative array.
		:rtype: dict
		"""

		array = Vector.to_array(self)
		array.update({
			'class': str(Document),
			'text': self.text,
		})
		return array

	@staticmethod
	def from_array(array):
		"""
		Create an instance of the document from the given associative array.

		:param array: The associative array with the attributes to create the document.
		:type array: dict

		:return: A new instance of an object with the same attributes stored in the object.
		:rtype: :class:`~vector.nlp.document.Document`
		"""

		return Document(text=array.get('text'), dimensions=array.get('dimensions'),
						attributes=array.get('attributes'))

	@staticmethod
	def concatenate(*args, tokenizer, scheme=None, **kwargs):
		"""
		Concatenate all of the documents that are provided as arguments.
		The function first concatenates the text of all the documents.
		Then, it tokenizes the concatenated and creates a document from it.

		Any additional keyword arguments are passed on to the Document constructor.

		:param scheme: The term-weighting scheme to use to create the concatenated document.
		:type scheme: :class:`~nlp.term_weighting.scheme.TermWeightingScheme`
		:param tokenizer: The tokenizer to use to construct the concatenated document.
		:type tokenizer: :class:`~nlp.tokenizer.Tokenizer`

		:return: A new document representing the concatenated documents.
				 The document is not normalized.
		:rtype: :class:`~nlp.document.Document`
		"""

		text = ' '.join([ document.text for document in args ])
		tokens = tokenizer.tokenize(text)
		document = Document(text, tokens, scheme=scheme, **kwargs)
		return document
