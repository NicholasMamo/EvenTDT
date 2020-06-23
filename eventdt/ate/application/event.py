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

	def extract(self, timelines):
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

		:return: A dictionary with terms as keys and their event frequency as the values.
		:rtype: dict
		"""

		ef = { }

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
				Increment the event frequency of all the terms in the timeline.
				"""

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
		Create the logarithmic EF extractor with the base.

		:param base: The logarithmic base.
		:type base: float
		"""

		super().__init__()
		self.base = base

	def extract(self, timelines):
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

		:return: A dictionary with terms as keys and their event frequency as the values.
		:rtype: dict
		"""

		extractor = EF()
		terms = extractor.extract(timelines)
		terms = { term: math.log(value, self.base) for term, value in terms.items() }
		return terms

def EFIDF(timelines, idf, base=None):
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
	:param idf: The IDF table to use to score terms.
	:type idf: :class:`~nlp.term_weighting.global_schemes.tfidf.TFIDF`
	:param base: The logarithmic base.
	:type base: float

	:return: A dictionary with terms as keys and their EF-IDF score as the values.
	:rtype: dict
	"""

	efidf = { }

	ef = logEF(timelines, base) if base else EF(timelines)
	efidf = { term: ef[term] * idf.create([ term ]).dimensions[term] for term in ef }

	return efidf

def variability(term, idfs):
	"""
	Calculate how variable the term is across events.
	A term is highly-variable if it appears disproportionately in one or a few events.
	A low variability indicates that the term appears consistently across all events.

	The method follows the leave-one-out principle: each event is compared against all other events.
	The final result is an average weightg according to the event sizes.

	:param term: The term for which to calculate the variability.
	:type term: str
	:param idfs: A list of IDFs, one for each event.
	:type idfs: list of :class:`~nlp.term_weighting.tfidf.TFIDF`

	:return: The variability of the term.
			 A term is highly-variable if it appears disproportionately in one or a few events.
			 A low variability indicates that the term appears consistently across all events.
	:rtype: float
	"""

	v = 0

	"""
	Calculate the number of documents across all events.
	This is the size of the contingency table.
	"""
	all_documents = sum(idf.global_scheme.documents for idf in idfs)

	"""
	For each event, compare the appearance of the term in the event with its appearance in other events.
	"""
	for idf in idfs:
		"""
		Create the contingency table and compute the chi-square value.
		The statistic's weight is based on the size of the current event.
		"""
		comparison = [ other for other in idfs if other is not idf ]
		table = _variability_contingency_table(term, idf, comparison)
		chi = probability._chi(table)
		v += chi * idf.global_scheme.documents / all_documents

	return v

def _variability_contingency_table(term, current, comparison):
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
