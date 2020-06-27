"""
Event-based ATE approaches use either event corpora or the output timelines to score and rank domain terms.
"""

import json
import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate.bootstrapping import probability
from ate.extractor import Extractor
from objects.exportable import Exportable

class EF(Extractor):
	"""
	The Event Frequency (EF) extractor looks for terms in timelines.
	The scoring is based on simple frequency.
	"""

	def extract(self, timelines, candidates=None):
		"""
		Calculate the event frequency of terms from the given timelines.
		The event frequency is simply the number of events in which term appears in a development.

		:param timelines: The path to a timeline or a list of paths to timelines.
						  If a string is given, it is assumed to be one event timeline.
						  If a list is given, it is assumed to be a list of event timelines.

						  .. note::

						      It is assumed that the event timelines were extracted using the collection tool.
							  Therefore each file should be a JSON string representing a :class:`~summarization.timeline.timeline.Timeline`.
		:type timelines: str or list of str
		:param candidates: A list of terms for which to calculate a score.
						   If `None` is given, all words are considered to be candidates.
		:type candidates: None or list of str

		:return: A dictionary with terms as keys and their event frequency as the values.
		:rtype: dict
		"""

		ef = { } if not candidates else dict.fromkeys(candidates, 0)

		timelines = self.to_list(timelines)

		for timeline in timelines:
			with open(timeline, 'r') as f:
				data = json.loads(''.join(f.readlines()))

				"""
				Decode the timeline and extract all the terms in it.
				"""
				timeline = Exportable.decode(data)['timeline']
				terms = set( term for node in timeline.nodes
								  for topic in node.topics
								  for term in topic.dimensions )

				"""
				Increment the event frequency of all the candidates terms—if any—in the timeline.
				"""
				terms = terms if not candidates else [ term for term in terms
				 											if term in candidates ]
				for term in terms:
					ef[term] = ef.get(term, 0) + 1

		return ef

class LogEF(EF):
	"""
	The logarithmic Event Frequency (EF) extractor looks for terms in timelines.
	The scoring is the logarithm of the simple frequency, as calculated in :class:`~ate.application.event.EF`.

	:ivar base: The logarithmic base.
	:vartype base: float
	"""

	def __init__(self, base=2):
		"""
		Create the logarithmic EF extractor with the logarithmic base.

		:param base: The logarithmic base.
		:type base: float
		"""

		super().__init__()
		self.base = base

	def extract(self, timelines, candidates=None):
		"""
		Calculate the logarithmic event frequency of terms from the given timelines.
		The event frequency is simply the number of events in which term appears in a development.

		This weighting scheme is based on the :func:`~ate.application.event.EF` weighting scheme.

		:param timelines: The path to a timeline or a list of paths to timelines.
						  If a string is given, it is assumed to be one event timeline.
						  If a list is given, it is assumed to be a list of event timelines.

						  .. note::

						      It is assumed that the event timelines were extracted using the collection tool.
							  Therefore each file should be a JSON string representing a :class:`~summarization.timeline.timeline.Timeline`.
		:type timelines: str or list of str
		:param candidates: A list of terms for which to calculate a score.
						   If `None` is given, all words are considered to be candidates.
		:type candidates: None or list of str

		:return: A dictionary with terms as keys and their logarithmic event frequency as the values.
		:rtype: dict
		"""

		timelines = self.to_list(timelines)

		extractor = EF()
		terms = extractor.extract(timelines, candidates=candidates)
		terms = { term: (math.log(value, self.base) if value else value) for term, value in terms.items() }

		return terms

class EFIDF(Extractor):
	"""
	The EF-IDF extractor combines the event frequency with the inverse document frequency.
	The algorithm can be made to work with the :class:`~ate.application.event.LogEF` class instead of the :class:`~ate.application.event.EF` class by providing a logarithmic base.

	:ivar scheme: The IDF table to use to score terms.
	:vartype scheme: :class:`~nlp.term_weighting.global_schemes.tfidf.TFIDF`
	:ivar base: The logarithmic base.
				If it is given, the :class:`~ate.application.event.LogEF` class is used.
				Otherwise, the :class:`~ate.application.event.EF` class is used.
	:vartype base: None or float
	"""

	def __init__(self, scheme, base=None):
		"""
		Create the EF-IDF extractor with the scheme used to score terms and the logarithmic base.

		:param idf: The IDF table to use to score terms.
		:type idf: :class:`~nlp.term_weighting.global_schemes.tfidf.TFIDF`
		:param base: The logarithmic base.
					If it is given, the :class:`~ate.application.event.LogEF` class is used.
					Otherwise, the :class:`~ate.application.event.EF` class is used.
		:type base: None or float
		"""

		super().__init__()
		self.scheme = scheme
		self.base = base

	def extract(self, timelines, candidates=None):
		"""
		Calculate the event-frequency-inverse-document-frequency metric for terms.
		This is a local-global weighting scheme.
		The local scheme is the event frequency, and the global scheme is the inverse-document-frequency.
		If a logarithmic base is provided, the logarithmic event frequency is used instead.

		:param timelines: The path to a timeline or a list of paths to timelines.
						  If a string is given, it is assumed to be one event timeline.
						  If a list is given, it is assumed to be a list of event timelines.

						  .. note::

						      It is assumed that the event timelines were extracted using the collection tool.
							  Therefore each file should be a JSON string representing a :class:`~summarization.timeline.timeline.Timeline`.
		:type timelines: str or list of str
		:param candidates: A list of terms for which to calculate a score.
						   If `None` is given, all words are considered to be candidates.
		:type candidates: None or list of str

		:return: A dictionary with terms as keys and their EF-IDF scores as the values.
		:rtype: dict
		"""

		efidf = { }

		timelines = self.to_list(timelines)

		extractor = EF() if not self.base else LogEF(base=self.base)
		terms = extractor.extract(timelines, candidates=candidates)
		efidf = { term: terms[term] * self.scheme.create([ term ]).dimensions[term] for term in terms }

		return efidf

class Variability(Extractor):
	"""
	Variability is a metric that measures the consistency of appearance of a term across different events.
	The variability metric is based on the chi-square statistic.
	The intuition is that terms that appear more consistently in different events are more likely to belong to the domain.

	:ivar base: The logarithmic base.
	:vartype base: float
	"""

	def __init__(self, base=10):
		"""
		Create the variability extractor with a logarithmic base.
		This base is used because the variability score is the inverse of the chi-square.
		Therefore scores end up being very close to each other without a logarithm.

		:param base: The logarithmic base.
		:type base: float
		"""

		super().__init__()

		self.base = base

	def extract(self, idfs, candidates=None):
		"""
		Calculate how variable the term is across events.
		A term is highly-variable if it appears disproportionately in one or a few events.
		A low variability indicates that the term appears consistently across all events.
		To reflect this behavior in the score, the inverse of the variability is returned.

		The method follows the leave-one-out principle: each event is compared against all other events.
		The final result is an average weightg according to the event sizes.

		:param idfs: A list of IDFs, one for each event.
		:type idfs: list of :class:`~nlp.term_weighting.tfidf.TFIDF`
		:param candidates: A list of terms for which to calculate a score.
						   If `None` is given, all words are considered to be candidates.
		:type candidates: None or list of str

		:return: A dictionary with terms as keys and their inverse variability score as the values.
				 A term is highly-variable if it appears disproportionately in one or a few events.
				 A low variability indicates that the term appears consistently across all events.
				 To reflect this behavior in the score, the inverse of the variability is returned.
		:rtype: dict
		"""

		variability = { }

		"""
		Calculate the number of documents across all events.
		This is the size of the contingency table.
		"""
		all_documents = sum(idf.global_scheme.documents for idf in idfs)

		"""
		Go through each term and compute the variability.
		For each event, compare the appearance of the term in the event with its appearance in other events.
		"""
		vocabulary = candidates or self._vocabulary(idfs)
		for term in vocabulary:
			v = 0
			for idf in idfs:
				"""
				Create the contingency table and compute the chi-square value.
				The statistic's weight is based on the size of the current event.
				"""
				comparison = [ other for other in idfs if other is not idf ]
				table = self._variability_contingency_table(term, idf, comparison)
				chi = probability._chi(table)
				v += chi * idf.global_scheme.documents / all_documents

			variability[term] = 1./math.log(v, self.base) if v else 0

		return variability

	def _vocabulary(self, idfs):
		"""
		Extract the vocabulary from the given IDFs.

		:param idfs: A list of IDFs, one for each event.
		:type idfs: list of :class:`~nlp.term_weighting.tfidf.TFIDF`

		:return: A list of terms in the given IDFs.
		:rtype: list of str
		"""

		vocabulary = [ ]
		for idf in idfs:
			vocabulary.extend(list(idf.global_scheme.idf.keys()))

		return list(set(vocabulary))

	def _variability_contingency_table(self, term, current, comparison):
		"""
		Create the contingency table comparing the term's appearance in the current event versus other events.

		:param term: The term for which to create the contingency table.
		:type term: str
		:param current: The current event's IDF table.
		:type current: :class:`~nlp.term_weighting.tfidf.TFIDF`
		:param comparison: A list of IDFs, one for each event.
		:type comparison: list of :class:`~nlp.term_weighting.tfidf.TFIDF`

		:return: The contingency table for the term, contrasting the current event with all other events.
				 The first row is the total number of documents in the current event.
				 The second row is the total number of documents in the comparison events.
				 The totals of both rows sum up to the total number of documents.
				 The contingency table is returned as a tuple with four floats.
				 These correspond to the first and second rows respectively.
		:rtype: tuple of float
		"""

		current_documents = current.global_scheme.documents
		comparison_documents = sum(idf.global_scheme.documents for idf in comparison)

		"""
		`A` is the number of current event documents in which the term appears.
		"""
		A = current.global_scheme.idf.get(term, 0)

		"""
		`B` is the number of current event documents in which the term does not appear
		"""
		B = current_documents - A

		"""
		`C` is the number of other events in which the term appears.
		It is computed as the number of times the term appears in all events minus `A`.
		"""
		C = sum(idf.global_scheme.idf.get(term, 0) for idf in comparison)

		"""
		`D` is the number of other events in which the term does not appear.
		"""
		D = comparison_documents - C

		return (A, B, C, D)
