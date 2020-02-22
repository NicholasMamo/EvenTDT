"""
The Wikipedia postprocessor uses Wikipedia to get information about participants.
It uses this information to postprocess participants.
For example, participants that are persons can be reduced to a surname.

.. note::

	The Wikipedia postprocessor assumes that the given participants map to Wikipedia pages.
"""

import os
import re
import sys
import unicodedata

from nltk.corpus import words

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from nlp.tokenizer import Tokenizer

from wikinterface import info

from ..postprocessor import Postprocessor

class WikipediaPostprocessor(Postprocessor):
	"""
	The Wikipedia postprocessor assumes that the given participants map to Wikipedia pages.
	It uses this knowledge to get additional information about participants and postprocess the .

	:ivar remove_accents: A boolean that indicates whether accents should be removed.
	:vartype remove_accents: bool
	:ivar remove_brackets: A boolean indicating whether brackets should be removed.
	:vartype remove_brackets: bool
	:ivar surname_only: A boolean that indicates whether participants should be reduced to surnames.
						This only applies to participants that are known to be persons based on Wikipedia information.
						It is assumed that the surname is made up of all terms except the first one.
						Participants whose surnames are also words retain the full name.
						Note that when only surnames are retained, brackets are removed.
	:vartype surname_only: bool
	"""

	def __init__(self, remove_accents=True, remove_brackets=True, surname_only=True):
		"""
		Create the postprocessor.

		:param remove_accents: A boolean that indicates whether accents should be removed.
		:type remove_accents: bool
		:param remove_brackets: A boolean indicating whether brackets should be removed.
		:type remove_brackets: bool
		:param surname_only: A boolean that indicates whether participants should be reduced to surnames.
							 This only applies to participants that are known to be persons based on Wikipedia information.
							 It is assumed that the surname is made up of all terms except the first one.
							 Participants whose surnames are also words retain the full name.
							 Note that when only surnames are retained, brackets are removed.
		:type surname_only: bool
		"""

		self.remove_accents = remove_accents
		self.remove_brackets = remove_brackets
		self.surname_only = surname_only

	def postprocess(self, participants, *args, **kwargs):
		"""
		Postprocess the given participants.

		:param participants: The participants to postprocess.
							 It is assumed that all map to a Wikipedia page.
		:type participants: list of str

		:return: The postprocessed participants.
		:rtype: list of str
		"""

		if self.surname_only:
			"""
			If only surnames should be retained for persons, get the participant information.
			If the participant is a person, remove the first component of their name.
			The only exceptions is if the surname is a word, like `Young` in `Ashley Young`.
			In these cases, retain the full name.
			If surnames are to be removed, brackets are also always removed.
			"""
			persons = info.is_person(participants)
			for i, participant in enumerate(participants):
				# TODO: Look for "commonly known simply as" (Memphis) or "commonly known as" (Juninho) relations.
				if persons[participant]:
					participants[i] = self._get_surname(participant)

		"""
		Remove the brackets if need be.
		"""
		participants = [ self._remove_brackets(participant) for participant in participants ] if self.remove_brackets else participants

		"""
		Remove the accents if need be.
		"""
		participants = [ self._remove_accents(participant) for participant in participants ] if self.remove_accents else participants

		return participants

	def _get_surname(self, participant):
		"""
		Get the surname of the given participant.
		If the participant has brackets, they are removed.
		The surname is assumed to be all components except the first one.
		If the participant's surname is a word, the whole participant name is returned.

		:param participant: The participant whose surname will be removed.
		:type participant: str

		:return: The participant's surname.
		:rtype: str
		"""

		name = self._remove_brackets(participant)
		surname = ' '.join(name.split()[1:])
		if (surname and surname not in words.words() and
			surname.lower() not in words.words()):
			return surname.strip()

		return name.strip()

	def _remove_brackets(self, participant):
		"""
		Remove the accents from the given participant.

		:param participant: The participant whose brackets will be removed.
		:type participant: str

		:return: The participant without any brackets.
		:rtype: str
		"""

		bracket_pattern = re.compile("\(.*?\)")
		return bracket_pattern.sub(' ', participant).strip()

	def _remove_accents(self, participant):
		"""
		Remove the accents from the given participant.

		:param participant: The participant whose accents will be removed.
		:type participant: str

		:return: The participant without any accents.
		:rtype: str
		"""

		return ''.join((c for c in unicodedata.normalize('NFD', participant) if unicodedata.category(c) != 'Mn'))
