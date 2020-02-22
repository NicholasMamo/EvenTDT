"""
The postprocessor is the sixth and last step in the APD process.
A postprocessor formats the participants.

The postprocessor returns the same number of participants with any changes to them.
The functionality revolves around one method: the :meth:`apd.postprocessors.postprocessor.Postprocessor.postprocess` method.
"""

class Postprocessor(object):
	"""
	The simplest postprocessor returns the participants without any changes.
	"""

	def postprocess(self, participants, *args, **kwargs):
		"""
		Return the same participants as those received.

		:param participants: The participants to postprocess.
		:type participants: list of str

		:return: The postprocessed participants.
		:rtype: list of str
		"""

		return participants
