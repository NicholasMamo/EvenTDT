"""
The token extractor considers all the tokens in the corpus to be candidate participants.
Therefore it does not perform any filtering whatsoever on the corpus.
"""

from ..extractor import Extractor

class TokenExtractor(Extractor):
	"""
	The token extractor does not perform any filtering whatsoever on the corpus.
	It returns all tokens as potential candidates.
	"""

	def extract(self, corpus, tokenizer=None, *args, **kwargs):
		"""
		Extract all the potential participants from the corpus.
		The output is a list of lists.
		Each outer list represents a document.
		Each inner list is the candidates in that document.

		:param corpus: The corpus of documents where to extract candidate participants.
		:type corpus: list
		:param tokenizer: The tokenizer used to extract the tokens anew.
						  If it is given, the tokens are extracted anew.
						  Otherwise, the document dimensions are used instead.
		:type tokenizer: None or :class:`nlp.tokenizer.Tokenizer`

		:return: A list of candidates separated by the document in which they were found.
		:rtype: list of list of str
		"""

		if tokenizer:
			return [ tokenizer.tokenize(document.text) for document in corpus ]
		else:
			return [ [ token for token in document.dimensions ] for document in corpus ]
