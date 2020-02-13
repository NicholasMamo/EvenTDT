"""
The resolver is the fourth step of APD.
Its job is to take a list of candidate participants and try to transform them into actual participants.

The representation between candidates and participants can remain almost identical.
For example a stemmed token can be replaced by a proper term.
It can also change the representation radically.
For example, it can map a named entity to a Wikipedia concept.

Resolvers return a tuple, containing resolved and unresolved candidates.
The unresolved candidates are usually discarded.
"""

class Resolver(object):
	"""
	The simplest resolver returns all candidates without any resolution.
	"""

	def resolve(self, candidates, *args, **kwargs):
		"""
		The resolution function returns the same candidates as they were given without making any changes.

		:param candidates: The candidates to resolve.
		:type candidates: list

		:return: A tuple containing the resolved and unresolved candidates respectively.
				 The function resolves all candidates.
				 Therefore unresolved candidates are empty.
		:rtype: tuple
		"""

		return (candidates, [ ])
