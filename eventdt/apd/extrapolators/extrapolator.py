"""
An extrapolator takes in candidates and tries to find other candidates, similar to entity set expansion.
"""

class Extrapolator(object):
	"""
	The simplest extrapolator returns the candidates without any new members.
	"""

	def extrapolate(self, candidates, corpus, extrapolated_participants=10, extrapolated_threshold=0, token_attribute="tokens", *args, **kwargs):
		"""
		Extrapolate from the given candidates.
		This extrapolator changes nothing.

		:param candidates: The seed set of candidates.
		:type candidates: list
		:param corpus: The corpus of documents, which helps to measure the membership of new candidates.
		:type corpus: list
		:param extrapolated_participants: The number of extrapolated participants to retrieve.
		:type extrapolated_participants: int
		:param extrapolated_threshold: The minimum score of the extrapolated participant to be considered.
		:type extrapolated_threshold: float
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: The new candidates.
		:rtype: list
		"""

		return [ ]
