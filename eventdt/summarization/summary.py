"""
The summary object represents a textual summary.
"""

import importlib
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
	sys.path.insert(1, path)

from objects.attributable import Attributable

class Summary(Attributable):
	"""
	A summary is made up of various attributes.
	It is made up of the actual list of :class:`~vector.nlp.document.Document` of the summary.
	Associated with the summary are also two timestamps - the timestamps when the summary was creation and last updated.

	:ivar documents: The documents that make up the summary.
	:vartype documents: list of :class:`~nlp.document.Document`
	"""

	def __init__(self, documents=None, *args, **kwargs):
		"""
		Create the summary.

		:param documents: A list of documents that make up the summary.
		:type documents: list of :class:`~nlp.document.Document`
		"""

		super(Summary, self).__init__(*args, **kwargs)
		self.documents = documents or [ ]

	def __repr__(self):
		"""
		Get the string representation of the summary.
		This is equivalent to concatenating the text of all documents.

		:return: The string representation of the summary.
		:rtype: str
		"""

		return ' '.join([ document.text for document in self.documents ])

	def to_array(self):
		"""
		Export the summary as a dictionary.

		:return: The summary as a dictionary.
		:rtype: dict
		"""

		return {
			'attributes': self._attributes,
			'documents': [ document.to_array() for document in self.documents ]
		}

	@staticmethod
	def from_array(array):
		"""
		Create a summary instance from the given dictionary.

		:param array: The dictionary with the necessary information to re-create the summary.
		:type array: dict

		:return: A new summary.
		:rtype: :class:`~summarization.summary.Summary`
		"""

		documents = []
		for vector in array.get('documents'):
			cls = vector.get('class', '')
			cls = cls[ cls.index('\'') + 1:cls.rindex('\'') ]
			module_name, class_name = cls[ :cls.rindex('.') ], cls[ cls.rindex('.') + 1: ]
			module = importlib.import_module(module_name)
			cls = getattr(module, class_name)
			documents.append(cls.from_array(vector))

		return Summary(documents=documents, attributes=array.get('attributes'))
