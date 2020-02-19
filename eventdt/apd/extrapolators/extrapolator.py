"""
The extrapolator is the fifth step of APD.
The extrapolator receives a list of participants and tries to find other relevant participants.
This step is analogous to entity set expansion.
The participants should be ranked in descending order of their relevance.

The input participants should be the product of a :class:`apd.resolvers.resolver.Resolver` process.
This input is a simple list of strings. each representing a participant.

Extrapolators return a list of new participants: simple strings as well.
The functionality revolves around one method: the :meth:`apd.extrapolators.extrapolator.Extrapolator.extrapolate` method.
"""

class Extrapolator(object):
	"""
	The simplest extrapolator returns no new participants.
	"""

	def extrapolate(self, participants, *args, **kwargs):
		"""
		Extrapolate from the given participants.
		This extrapolator returns no new participants.

		:param participants: The participants found by the resolver.
		:type participants: list of str

		:return: The new participants identified as relevant by the extrapolator
		:rtype: list of str
		"""

		return [ ]
