"""
A participant detector is responsible of collecting information about participants in an event.

The process includes a number of steps:

	#. Extract candidate participants;

	#. Score the candidates;

	#. Filter the candidates - the retained ones are the participants;

	#. Resolve the participants, mapping them to lemmas (optional); and

	#. Extrapolate the participants, analogous to entity set expansion (optional)
"""

from abc import ABC, abstractmethod
import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.insert(1, path)

from nltk.corpus import words

from logger import logger

from .extractors.extractor import Extractor
from .extrapolators.extrapolator import Extrapolator
from .postprocessors.postprocessor import Postprocessor
from .resolvers.resolver import Resolver
from .scorers.scorer import Scorer

class ParticipantDetector(ABC):
	"""
	The base class for all participant detectors.
	The corpus is used for comparisons.
	It is assumed that the corpus has already been collected in its entirety.

	Similarly to query expansion, a participant detector is responsible of performing three actions:

		#. Use a corpus to extract candidates;

		#. Score and rank the candidates; and

		#. Extract the top candidates.

	:ivar _corpus: The corpus of documents on which APD is based.
		This corpus serves multiple functions, including similarity comparisons.
	:vartype _corpus: list
	:ivar _extractor: The extractor that is used to find candidate participants from the corpus.
	:vartype _extractor: :class:`apd.extractors.extractor.Extractor`
	:ivar _scorer: The scorer that assigns a value to each candidate participant.
	:vartype _scorer: :class:`apd.scorers.scorer.Scorer`
	:ivar _resolver: An instance of a resolver that transforms participants into keywords.
	:vartype _resolver: :class:`apd.resolvers.resolver.Resolver`
	:ivar _extrapolator: An extrapolator that looks for additional participants.
		These participants may not necessarily be found in the corpus.
	:vartype _extrapolator: :class:`apd.extrapolators.extrapolator.Extrapolator`
	:ivar _postprocessor: The postprocessor processes found candidates.
	:vartype _postprocessor: :class:`apd.postprocessors.postprocessor.Postprocessor`
	"""

	def __init__(self, corpus, extractor, scorer, resolver=Resolver, extrapolator=Extrapolator, postprocessor=Postprocessor):
		"""
		Create the participant detector, which is made up of a number of components.

		:param corpus: The corpus of documents on which APD is based.
		:type corpus: list
		:param extractor: The participant detector's extractor.
			This component is used to find candidate participants.
		:type extractor: :class:`apd.extractors.extractor.Extractor`
		:param scorer: The participant detector's scorer.
			This component is used to give a score to the extractor's candidate participants.
		:type scorer: :class:`apd.scorers.scorer.Scorer`
		:param resolver: The participant detector's resolver.
			This component looks for the real keywords associated with a participant.
		:type resolver: :class:`apd.resolvers.resolver.Resolver`
		:param extrapolator: The participant detector's extrapolator.
			This component looks for additional participants that might not be in the corpus.
		:type extrapolator: :class:`apd.extrapolators.extrapolator.Extrapolator`
		:param postprocessor: The participant detector's postprocessor.
			This component modifies the found participants.
		:type postprocessor: :class:`apd.postprocessors.postprocessor.Postprocessor`
		"""

		self._corpus = corpus
		self._extractor = extractor()
		self._scorer = scorer()
		self._resolver = resolver()
		self._extrapolator = extrapolator()
		self._postprocessor = postprocessor()

	def detect(self, threshold=0, max_candidates=-1, known_participants=None, *args, **kwargs):
		"""
		Detect participants from the given corpus.

		:param threshold: The minimum score to retain a candidate.
		:type threshold: float
		:param max_candidates: The maximum number of candidates to retain.
			Only the top ones should be retained after ranking.
		:type max_candidates: int
		:param known_participants: A list of participants that are known in advance.
			These are passed on to be resolved, which means they may not be retained by the resolver.
		:type known_participants: list

		:return: The list of participants.
		:rtype: list
		"""

		"""
		Convert the known participants into a dictionary.
		"""
		known_participants = [] if type(known_participants) is not list else known_participants

		documents = self._extractor.extract(self._corpus, *args, **kwargs)
		candidates = self._scorer.score(documents, *args, **kwargs)
		filtered = self._filter(candidates, threshold=threshold, max_candidates=max_candidates, *args, **kwargs)
		filtered = known_participants + filtered

		resolved, unresolved = self._resolver.resolve(filtered, self._corpus, *args, **kwargs)
		extrapolated = self._extrapolator.extrapolate(resolved, self._corpus, *args, **kwargs)
		resolved = self._postprocessor.postprocess(resolved, self._corpus, *args, **kwargs)
		extrapolated = self._postprocessor.postprocess(extrapolated, self._corpus, *args, **kwargs)

		resolved = [ resolved[i] for i in range(0, len(resolved)) if resolved[i] not in resolved[:i] ]
		unresolved = [ unresolved[i] for i in range(0, len(unresolved)) if unresolved[i] not in unresolved[:i] ]
		extrapolated = [ extrapolated[i] for i in range(0, len(extrapolated)) if extrapolated[i] not in extrapolated[:i] ]

		return resolved, unresolved, extrapolated

	def _combine(self, candidates):
		"""
		Combine the candidates.
		If a candidate is a subset of another candidate, add it to the longest one.
		The scores are added up.

		:param candidates: A dictionary of candidates participants, accompanied with a score.
		:type candidates: dict

		:return: A new dict of combined candidates.
		:rtype: dict
		"""

		all_candidates = list(candidates.keys()) # the list of candidate names
		combined_candidates = dict.fromkeys(all_candidates, 0)
		sorted_candidates = sorted(candidates.items(), key=lambda x: x[1])[::-1] # the candidates sorted by score in descending order
		longest_candidates = sorted(candidates.items(), key=lambda x: len(x[0]))[::-1]

		for candidate, _ in sorted_candidates:
			"""
			The first step is to concatenate all candidates except the current one.
			In this way, redundant checks can be skipped.
			"""
			remaining_candidates = list(all_candidates) # copy the candidates
			remaining_candidates.remove(candidate) # remove the current candidate
			candidate_string = '|'.join(remaining_candidates)

			if candidate in candidate_string:
				"""
				If the candidate is in the string, look for it in the remaining candidates.
				The overlapping candidate with the highest score is chosen.
				"""
				for other, _ in longest_candidates:
					if candidate in other and candidate != other:
						combined_candidates[other] += candidates[candidate]
						break
			else:
				"""
				Otherwise, add the score to the same candidate.
				"""
				combined_candidates[candidate] += candidates[candidate]

		"""
		Before returning, strip away candidates with no score.
		These candidates were combined.
		"""
		combined_candidates = { candidate: score for candidate, score in combined_candidates.items() if score > 0 }

		return combined_candidates

	def _filter(self, candidates, threshold=0, max_candidates=-1, combine=True, *args, **kwargs):
		"""
		Filter the given candidates and return only the top.

		:param candidates: A dictionary of candidates participants that were found earlier, accompanied with a score.
		:type candidates: dict
		:param threshold: The minimum score to retain a candidate.
		:type threshold: float
		:param max_candidates: The maximum number of candidates to retain.
			Only the top ones should be retained after ranking.
		:type max_candidates: int

		:return: A list of retained candidates.
		:rtype: list
		"""

		candidates = { candidate: score for candidate, score in candidates.items() if score >= threshold }
		# candidates = { candidate: score for candidate, score in candidates.items() if candidate.lower() not in words.words() }
		candidates = sorted(candidates.items(), key=lambda x: x[1])[::-1]

		candidates = self._combine(dict(candidates)) if combine else dict(candidates)
		candidates = sorted(candidates.items(), key=lambda x: x[1])[::-1]
		# print(candidates)

		if max_candidates > -1:
			return list([ candidate for candidate, _ in candidates ])[:max_candidates]
		else:
			return list([ candidate for candidate, _ in candidates ])
