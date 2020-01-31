"""
The :class:`eventdt.nlp.document.Document` class builds on the :class:`eventdt.vsm.vector.Vector` class.
In addition to the normal VSM functionality, it introduces additional document-specific capabilities.
"""

__metaclass__ = type

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
	The Document class is based on the Vector Space Model, and is based on the Vector class.
	A label field is notably added, which is useful when it comes to the evaluation.

	:ivar _label: The label of the document.
	:vartype _label: str
	:ivar _text: The document's original text.
	:vartype _text:
	"""

	def __init__(self, text="", dimensions=None, attributes=None, label=None, scheme=None):
		"""
		Initialize the Document with optional dimensions and an optional label.

		:param dimensions: The initial dimensions of the document.
			If a list is provided, it is assumed that they are tokens.
			The dimensions are then created using the given scheme.
		:type dimensions: dict
		:param attributes: The initial attributes of the document.
		:type attributes: dict
		:param label: The document's label.
		:type label: str
		:param scheme: The scheme that is used to convert the tokens into dimensions.
		:type scheme: :class:`vector.nlp.TermWeighting`
		"""

		"""
		If a list is provided, assume that it is a list of tokens.
		This list of tokens is converted into a dictionary representing the dimensions of the Vector.
		The conversion is carried out by the term weighting scheme.
		"""
		from term_weighting import TF # import located here because of circular dependencies

		if (type(dimensions) == list):
			scheme = scheme if scheme is not None else TF()
			tokens = list(dimensions)
			dimensions = scheme.create(tokens).get_dimensions()

		super(Document, self).__init__(dimensions, attributes)
		self.set_text(text)
		self.set_label(label)

	def set_text(self, text):
		"""
		Set the text.

		:param text: The document's text.
		:type text: str
		"""
		self._text = text

	def get_text(self):
		"""
		Get the document's text.

		:return: The document's text.
		:rtype: str
		"""

		return self._text

	def set_label(self, label):
		"""
		Set the label.

		:param label: The document's label.
		:type label: str
		"""
		self._label = label

	def get_label(self):
		"""
		Get the label.

		:return: The document's label.
		:rtype: str
		"""
		return self._label

	def to_array(self):
		"""
		Export the document as an associative array.

		:return: The document as an associative array.
		:rtype: dict
		"""

		array = Vector.to_array(self)
		array.update({
			"class": str(Document),
			"text": self.get_text(),
			"label": self.get_label(),
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
			label=array.get("label", ""),
		)
