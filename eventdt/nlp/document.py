"""
The :class:`eventdt.nlp.document.Document` class builds on the :class:`eventdt.vsm.vector.Vector` class.
In addition to the normal VSM functionality, it introduces additional document-specific capabilities.
"""

import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
	sys.path.insert(1, path)

from vsm.vector import Vector

from logger import logger

class Document(Vector):
	"""
	The :class:`eventdt.nlp.document.Document` class is based on the :class:`eventdt.vsm.vector.Vector` class. class.
	The main addition is the text field.
	This field stores the original document text for any later changes.

	:ivar text: The document's original text.
	:vartype text: str
	"""

	def __init__(self, text='', dimensions=None, scheme=None, *args, **kwargs):
		"""
		Initialize the document with the text and optional dimensions.
		Any other arguments or keyword arguments are passed on to the :class:`eventdt.vsm.vector.Vector` constructor.

		:param text: The document's text.
		:type text: str
		:param dimensions: The initial dimensions of the document.
						   If a list is provided, it is assumed that they are tokens.
						   The dimensions are then created from this list using the given scheme.
		:type dimensions: list or dict
		:param scheme: The term-weighting scheme that is used to convert the tokens into dimensions.
					   If `None` is given, the :class:`vector.nlp.TermWeighting.TF` term-weighting scheme is used.
		:type scheme: None or :class:`vector.nlp.TermWeighting`
		"""

		"""
		If a list is provided, assume that it is a list of tokens.
		This list of tokens is converted into a dictionary representing the dimensions of the vector.
		The conversion is carried out by the term-weighting scheme.
		"""
		from term_weighting import TF # NOTE: The import is located here because of circular dependencies

		if (type(dimensions) == list):
			scheme = scheme if scheme is not None else TF()
			dimensions = scheme.create(dimensions).dimensions

		super(Document, self).__init__(dimensions, *args, **kwargs)
		self.text = text

	def to_array(self):
		"""
		Export the document as an associative array.

		:return: The document as an associative array.
		:rtype: dict
		"""

		array = Vector.to_array(self)
		array.update({
			"class": str(Document),
			"text": self.text,
		})
		return array

	@staticmethod
	def from_array(array):
		"""
		Create an instance of the document from the given associative array.

		:param array: The associative array with the attributes to create the document.
		:type array: dict

		:return: A new instance of an object with the same attributes stored in the object.
		:rtype: :class:`vector.nlp.document.Document`
		"""

		return Document(text=array.get("text", ""),
			dimensions=array.get("dimensions", None),
			attributes=array.get("attributes", {}),
		)
