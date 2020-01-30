"""
A resolver takes in candidates and resolves them to an alternative representation.
"""

class Resolver(object):
	"""
	The simplest resolver returns the candidates without any resolution.
	"""

	def resolve(self, candidates, corpus, token_attribute="tokens", *args, **kwargs):
		"""
		Resolve the given candidates.
		This resolver changes nothing.

		:param candidates: The candidates to resolve.
		:type candidates: list
		:param corpus: The corpus of documents, which helps to resolve the candidates.
		:type corpus: list
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: A tuple containing the resolved candidates, and unresolved ones.
		:rtype: tuple
		"""

		return (candidates, [])
