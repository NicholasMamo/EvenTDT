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

		disambiguation_pattern = re.compile(" \(.*?\)$") # a pattern of information that ends a title with disambiguation information, or more information about the concept

		if postprocessor_surname_only:
			"""
			If only surnames should be retained for persons (and persons only), get the participant information.
			If the participant is a person, retain only the last part of their name.
			The only exceptions is if the surname is a word, like `Young` in `Ashley Young`.
			In these cases, retain the full name.
			"""
			processed = []
			candidate_status = info_collector.is_person(candidates)
			for participant in postprocessed:
				if participant not in candidate_status:
					logger.warning("%s not in [%s]" % (participant, ', '.join(list(candidate_status.keys()))))
				if participant in candidate_status and candidate_status[participant]:
					"""
					If the participant is a person, retain only the last part of their name.
					First, though, get the disambiguation text and remove it.
					This is consistent with the idea because only the surname is ever needed.
					"""
					participant = disambiguation_pattern.sub('', participant.strip())
					participant = self.remove_accents([ participant ])[0] if postprocessor_remove_accents else participant
					surname = participant[participant.rfind(" ") + 1:]
					if surname not in words.words() and surname.lower() not in words.words():
						processed.append(surname)
					else:
						processed.append(participant)
				else:
					"""
					If the participant is not a person, just append them without any changes.
					"""
					processed.append(participant)

			postprocessed = processed

		"""
		Remove disambiguation text if need be.
		"""
		postprocessed = self.remove_disambiguation(postprocessed) if postprocessor_remove_disambiguation else postprocessed # remove disambiguation details from the end of the title

		"""
		Remove the accents if need be.
		"""
		postprocessed = self.remove_accents(postprocessed) if postprocessor_remove_accents else postprocessed

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
