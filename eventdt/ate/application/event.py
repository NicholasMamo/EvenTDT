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
