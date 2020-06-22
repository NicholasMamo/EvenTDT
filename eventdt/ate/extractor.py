"""
The extractor outlines the functionality that all ATE approaches should offer.
The abstract class is very simple and all extractors must, at least, provide functionality to extract terms from a corpus or corpora.
"""

from abc import ABC, abstractmethod

class Extractor(ABC):
	"""
	An abstract class that defines what all ATE extractors should be able to do.
	This simple class necessitates only that all extractors accept a corpus or corpora and returns a list of terms.
	"""

	@abstractmethod
	def extract(self, corpora):
		"""
		Extract terms from the given corpora.

		:param corpora: A path to a corpus or a list of paths to corpora where to look for terms.
						The basic extractor does not place any restrictions of the corpora.
						Linguistic or hybrid approaches might need the original text to be available in the corpora.
						For statistical approaches, a tokenized corpus might suffice.
		:type corpora: str or list of str

		:return: A list of terms.
		:rtype: list of str
		"""

		pass

	def to_list(self, corpora):
		"""
		Convert the given corpora to a list of corpora.
		This function can be invoked when the input is either a list or a single path.
		If a list of corpora is provided, this function returns the original input.

		:param corpora: A path to a corpus or paths to corpora.
		:type corpora: str or list of str

		:return: A list of corpora.
		:rtype: list of str
		"""

		return corpora if type(corpora) is list else [ corpora ]

class DummyExtractor(Extractor):
	"""
	A dummy extractor that does nothing and returns an empty list of terms.
	It is used only for testing purposes.
	"""

	def extract(self, corpora):
		"""
		Return an empty list of terms.

		:param corpora: A path to a corpus or a list of paths to corpora where to look for terms.
		:type corpora: str or list of str

		:return: An empty list of terms.
		:rtype: list of str
		"""

		return [ ]
