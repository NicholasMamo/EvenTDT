"""
Term-weighting schemes give different weights to different terms in a document.
"""

class SchemeScorer(ABC):
	"""
	A scheme is used to score documents' tokens.
	It is important to distinguish between :class:`eventdt.nlp.term_weighting.scheme.TermWeightingScheme` and :class:`eventdt.nlp.term_weighting.scheme.SchemeScorer`.
	The former is a complete term-weighting scheme that takes local and global scheme scorers.
	The latter is the actual scorer.
	A :class:`eventdt.nlp.term_weighting.scheme.SchemeScorer` is a component of a term-weighting scheme.
	A :class:`eventdt.nlp.term_weighting.scheme.TermWeightingScheme` combines local and global scorers to create documents.
	"""

	@abstractmethod
	def score(self, tokens, *args, **kwargs):
		"""
		Score the given list of tokens.

		:param tokens: The list of tokens to weigh.
		:type tokens: list of str

		:return: A dictionary with the tokens as the keys and the weights as the values.
		:rtype: dict
		"""

		pass
