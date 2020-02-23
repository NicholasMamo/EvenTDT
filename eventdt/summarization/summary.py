"""
The summary object represents a textual summary.
"""

import importlib
import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '../')
if path not in sys.path:
	sys.path.insert(1, path)

from logger import logger

from objects.exportable import Exportable

from vector.nlp.cleaners import cleaner

class Summary(Exportable):
	"""
	A summary is made up of various attributes.
	It is made up of the actual list of :class:`~vector.nlp.document.Document` of the summary.
	Associated with the summary are also two timestamps - the timestamps when the summary was creation and last updated.

	:ivar _documents: The documents making up the summary.
	:vartype _documents: list of :class:`~vector.nlp.document.Document` instances.
	:ivar _created: The timestamp when the summary was created.
	:vartype _created: int
	:ivar _last_updated: The timestamp when the summary was last updated.
	:vartype _last_updated: int
	"""

	def __init__(self, documents=None, timestamp=None):
		"""
		Create the summary.

		:param documents: A list of documents that make up the summary.
		:type documents: list of :class:`~vector.nlp.document.Document` instances
		:param timestamp: The timestamp when the summary was created.
		:type timestamp: int
		"""

		self._documents = documents if documents is not None else []
		self._created = timestamp if timestamp is not None else 0
		self._last_updated = self._created

	def add_document(self, document):
		"""
		Add the given document to the summary.

		:param document: The new document.
		:type document: :class:`~vector.nlp.document.Document`
		"""

		self._documents.append(document)

	def remove_document(self, document):
		"""
		Remove the given document from the summary.

		:param document: The document to remove from the summary.
		:type document: :class:`~vector.nlp.document.Document`
		"""

		if document in self._documents:
			self._documents.remove(document)

	def set_documents(self, documents):
		"""
		Set the list of documents making up the summary.

		:param documents: The list of documents that now make up the summary.
		:type documents: list of :class:`~vector.nlp.document.Document` instances
		"""

		self._documents = documents

	def get_documents(self):
		"""
		Get the list of documents in the summary.

		:return: A list of documents that make up the summary.
		:rtype: list of :class:`~vector.nlp.document.Document` instances
		"""

		return self._documents

	def created_at(self):
		"""
		Get the time when the summary was created.

		:return: The time when the summary was created as a timestamp.
		:rtype: int
		"""

		return self._created

	def set_created_at(self, timestamp):
		"""
		Set the timestamp when the summary was created.

		:param timestamp: The timestamp when the summary was created.
		:type timestamp: int
		"""

		self._created = timestamp

	def set_last_updated(self, timestamp):
		"""
		Set the timestamp when the Summary was last updated.

		:param timestamp: The timestamp when the summary was last updated.
		:type timestamp: int
		"""

		self._last_updated = timestamp

	def last_updated(self):
		"""
		Get the last time that the summary was updated.

		:return: The last time that the summary was updated as a timestamp.
		:rtype: int
		"""

		return self._last_updated

	def get_concatenated_summary(self, cleaner=cleaner.Cleaner, *args, **kwargs):
		"""
		Get the concatenated summary as a document.
		"""

	def generate_summary(self, cleaner=cleaner.Cleaner, *args, **kwargs):
		"""
		Generate the actual textual summary. This is a concatenation of all the documents.

		:param cleaner: The class to use to clean the documents.
			By default, no cleaning is performed.
			Each document is cleaned individually.
		:type cleaner: :class:`~summarization.cleaners.cleaner.Cleaner`

		:return: The textual summary.
		:rtype: str
		"""

		cleaner = cleaner()

		documents = sorted(self._documents, key=lambda document: document.get_attribute("timestamp", 0))
		snippets = [ cleaner.clean(document.get_text()) for document in documents ]
		snippets = [ snippet for snippet in snippets if len(snippet) > 0 ]
		return ' '.join(snippets)

	def to_array(self):
		"""
		Export the summary as an associative array.

		:return: The summary as an associative array.
		:rtype: dict
		"""

		array = {}
		array.update({
			"documents": [ document.to_array() for document in self._documents ],
			"last_updated": self._last_updated,
			"created": self._created
		})
		return array

	@staticmethod
	def from_array(array):
		"""
		Create a summary instance from the given associative array.

		:param array: The associative array with the attributes to create the summary.
		:type array: dict

		:return: A new instance of an object with the same attributes stored in the object.
		:rtype: :class:`~summarization.summary.Summary`
		"""

		vectors = array.get("documents", [])
		loaded_vectors = []
		for vector in vectors:
			c = vector.get("class", "")
			c = c[c.index("'")+1:c.rindex("'")]
			module_name, class_name = c[:c.rindex(".")], c[c.rindex(".")+1:]
			module = importlib.import_module(module_name)
			c = getattr(module, class_name)
			loaded_vectors.append(c.from_array(vector))

		summary = Summary(documents=loaded_vectors, timestamp=array.get("created", 0))
		summary.set_last_updated(array.get("last_updated"))
		return summary
