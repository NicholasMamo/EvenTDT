"""
A simple extractor that considers all tokens to be potential candidates.
"""

from ..extractor import Extractor

class TokenExtractor(Extractor):
	"""
	The token extractor does not perform any filtering whatsoever on the corpus.
	It returns all tokens as potential candidates.
	"""

	def extract(self, corpus, token_attribute="tokens", *args, **kwargs):
		"""
		Extract all the potential participants from the corpus.
		The output is a list of lists.
		It should be noted that zipping together this list and the corpus should return a list of documents and associated candidates.

		:param corpus: The corpus of documents where to extract participants.
		:type corpus: list
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: A list of candidates separated by the document in which they were found.
		:rtype: list
		"""

		return [ [ token for token in document.get_attribute(token_attribute) ] for document in corpus ]
