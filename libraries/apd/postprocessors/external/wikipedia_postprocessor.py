"""
A postprocessor that uses Wikipedia to postprocess candidates.
"""

import os
import re
import sys

from nltk.corpus import words

path = os.path.dirname(__file__)
path = os.path.join(path, '../../../')
if path not in sys.path:
	sys.path.append(path)

from logger import logger

from vector import vector_math

from vector.nlp.document import Document
from vector.nlp.tokenizer import Tokenizer

from wikinterface.info_collector import InfoCollector

from ..postprocessor import Postprocessor

class WikipediaPostprocessor(Postprocessor):
	"""
	The Wikipedia postprocessor assumes that the given candidates map to Wikipedia pages.
	It uses this knowledge to get additional information about candidates.
	"""

	def postprocess(self, candidates, corpus, token_attribute="tokens",
		postprocessor_remove_accents=True, postprocessor_remove_disambiguation=True, postprocessor_surname_only=True, force_retain=False, *args, **kwargs):
		"""
		Postprocess the given candidates.

		:param candidates: The candidates to postprocess.
			It is assumed that all of the given candidates were resolved using :class:`apd.resolvers.external.wikipedia_resolver.WikipediaResolver`.
			The alternative is that they are the product
			This means that all candidates share their name with a Wikipedia page.
		:type candidates: list
		:param corpus: The corpus of documents, which helps to isolate relevant candidates.
		:type corpus: list
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str
		:param postprocessor_remove_accents: A boolean that indicates whether accents should be removed.
			Accents may be less likely to be written on social media since not all keyboards have them readily available.
		:type postprocessor_remove_accents: bool
		:param postprocessor_remove_disambiguation: A boolean indicating whether disambiguation text in the title should be removed.
		:type postprocessor_remove_disambiguation: bool
		:param postprocessor_surname_only: A boolean that indicates whether candidates should be reduced to surnames.
			Especially in sports events, surnames are predominantly used.
			This only applies to candidates that are known to be persons based on Wikipedia information.
			It is assumed that the surname is only one word long.
		:type postprocessor_surname_only: bool
		:param force_retain: A boolean indicating whether all the candidates should be retained.
			This was added in case of some participants who are known only by surname, like Pedro (Chelsea F.C.).
			In this case, these participants would be scrapped when their surname is also a word.
			If true, all participants are retained, even in this unlikely case.
		:type force_retain: bool

		:return: The new candidates.
			These candidates are stored as a dictionary.
			The keys are the resolved candidates, and the values are their scores.
		:rtype: dict
		"""

		postprocessed = list(candidates)
		info_collector = InfoCollector()

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

		"""
		The removal of disambiguation text may result in words, which should be removed.
		"""
		postprocessed = [ participant for participant in postprocessed if participant.lower() not in words.words() ] if not force_retain else postprocessed

		return postprocessed
