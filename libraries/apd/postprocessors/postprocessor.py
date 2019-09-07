"""
A postprocessor takes in participants and does something with them to make them ready for use.
"""

import re

import unicodedata

class Postprocessor(object):
	"""
	The simplest postprocessor returns the participants without any changes.
	"""

	def postprocess(self, participants, corpus, token_attribute="tokens", *args, **kwargs):
		"""
		Postprocess the given participants.
		This postprocessor changes nothing.

		:param participants: The participants to postprocess.
		:type participants: list
		:param corpus: The corpus of documents.
		:type corpus: list
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: The postprocessed participants.
		:rtype: list
		"""

		return participants

	def remove_accents(self, participants):
		"""
		Remove the accents from the participants.

		:param participants: The participants whose accents will be removed.
		:type participants: list

		:return: The participants without any accents.
		:rtype: list
		"""

		return [ ''.join((c for c in unicodedata.normalize('NFD', participant) if unicodedata.category(c) != 'Mn')) for participant in participants ]

	def remove_disambiguation(self, participants):
		"""
		Remove the accents from the participants.

		:param participants: The participants which will be cleaned.
		:type participants: list

		:return: The participants without any disambiguation text.
		:rtype: list
		"""

		disambiguation_pattern = re.compile(" \(.*?\)$") # a pattern of information that ends a title with disambiguation information, or more information about the concept

		return [ disambiguation_pattern.sub('', participant.strip()) for participant in participants ]
