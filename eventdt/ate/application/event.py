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

from objects.exportable import Exportable

def EF(timelines):
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

	timelines = [ timelines ] if type(timelines) is str else timelines

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

def logEF(timelines, base=2):
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
	:param base: The logarithmic base.
	:type base: floa

	:return: A dictionary with terms as keys and their event frequency as the values.
	:rtype: dict
	"""

	ef = EF(timelines)
	ef = { term: math.log(value, base) for term, value in ef.items() }
	return ef

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
	:type idf: :class:`~nlp.term_weighting.global_schemes.idf.IDF`
	:param base: The logarithmic base.
	:type base: floa

	:return: A dictionary with terms as keys and their EF-IDF score as the values.
	:rtype: dict
	"""

	efidf = { }

	ef = logEF(timelines, base) if base else EF(timelines)
	efidf = { term: ef[term] * idf.create([ term ]).dimensions[term] for term in ef }

	return efidf


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
