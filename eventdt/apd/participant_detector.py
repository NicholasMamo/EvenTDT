"""
The participant detector class is a simple class that takes in each of the six steps of APD as instances.
Then, it calls them, one after the other.

The process of the participant detector can be emulated by calling the main functions of the six steps in order.
The reason why this class exists is so that it can be extended into particular types of participant detectors.
The steps are identical to APD:

	#. Extract candidate participants;
	#. Score the candidates;
	#. Filter out low-scoring candidates;
	#. Resolve the candidates into alternative representations to make the participants;
	#. Extrapolate the participants, analogous to entity set expansion; and
	#. Postprocess the participants.

Of these steps, only the first two are required:

	#. If the filter is not given, all candidates are retained;
	#. If the resolver is not given, the extractor's inputs are all returned as participants;
	#. If the extrapolator is not given, no additional participants are returned; and
	#. If the postprocessor is not given, the participants are returned as found by the previous steps.
"""

from .scorers.scorer import Scorer
from .filters.filter import Filter
from .resolvers.resolver import Resolver
from .extrapolators.extrapolator import Extrapolator
from .postprocessors.postprocessor import Postprocessor

class ParticipantDetector(object):
	"""
	The basic participant detector accepts all steps as individual instances.
	The participant detector chains them together to identify the event's participants.

	:ivar ~.extractor: The extractor finds candidate participants in the corpus.
	:vartype extractor: :class:`apd.extractors.extractor.Extractor`
	:ivar ~.scorer: The scorer assigns a value to each candidate participant.
	:vartype scorer: :class:`apd.scorers.scorer.Scorer`
	:ivar ~.filter: The filter excludes candidates that are unlikely to be participants.
				  If it is not given, all of the candidates are retained.
	:vartype filter: :class:`apd.filters.filter.Filter` or None
	:ivar ~.resolver: The resolver resolves candidates into participants, if possible.
					If it is not given, all of the candidates are considered to be participants.
	:vartype resolver: :class:`apd.resolvers.resolver.Resolver` or None
	:ivar ~.extrapolator: The extrapolator looks for additional participants.
						If it is not given, no more participants are returned.
	:vartype extrapolator: :class:`apd.extrapolators.extrapolator.Extrapolator` or None
	:ivar ~.postprocessor: The postprocessor processes the participants.
						 If it is not given, the participants are returned as found.
	:vartype postprocessor: :class:`apd.postprocessors.postprocessor.Postprocessor` or None
	"""

	def __init__(self,  extractor, scorer, filter=None,
				 resolver=None, extrapolator=None, postprocessor=None):
		"""
		Create the participant detector, which is made up of a number of components.

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
		self.extractor = extractor
		self.scorer = scorer
		self.filter = Filter() if filter is None else filter
		self.resolver = Resolver() if resolver is None else resolver
		self.extrapolator = Extrapolator() if extrapolator is None else extrapolator
		self.postprocessor = Postprocessor() if postprocessor is None else postprocessor

	def detect(self, corpus, *args, **kwargs):
		"""
		Identify participants in the corpus.

		:param corpus: The corpus of documents from where to identify participants.
		:type corpus: list of :class:`nlp.document.Document`

		:return: A three-tuple, made up of the resolved, unresolved and extrapolated participants respectively.
		:rtype: tuple of list of str
		"""

		candidates = self.extractor.extract(corpus)
		candidates = self.scorer.score(candidates)
		candidates = self.filter.filter(candidates)

		resolved, unresolved = self.resolver.resolve(filtered)
		extrapolated = self.extrapolator.extrapolate(resolved)
		resolved = self.postprocessor.postprocess(resolved)
		extrapolated = self.postprocessor.postprocess(extrapolated)

		return resolved, unresolved, extrapolated
