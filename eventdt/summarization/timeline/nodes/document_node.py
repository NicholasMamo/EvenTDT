"""
A document node stores documents as a list.
"""

from .node import Node

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document

class DocumentNode(Node):
	"""
	A document node stores documents as a list.
	Comparisons are made with these documents, concatenated into one document.

	:ivar documents: The list of documents in this node.
	:type documents: :class:`~nlp.document.Document`
	"""

	def __init__(self, created_at=None):
		"""
		Create the node.

		:param created_at: The timestamp when the node was created.
						   If the timestamp is not given, the current time is used.
		:type created_at: float
		"""

		self.created_at = created_at or time.time()

	def add(self, *args, **kwargs):
		"""
		Add documents to the node.
		"""

		pass

	def similarity(self, *args, **kwargs):
		"""
		Compute the similarity between this node and a given object.

		:return: The similarity between this node and the given object.
		:rtype: float
		"""

		pass
