"""
The :class:`~WikipediaAttributeExtrapolator` is an extrapolator that extracts participants that have the same attributes as those resolved.
The extrapolator revolves closely around the :class:`~attributes.extractors.linguistic.LinguisticExtractor` to build profiles for participants and candidates.

.. note::

    The algorithm assumes that all resolved participants map to a Wikipedia page.
    Therefore Wikipedia-based resolvers make for good candidates before extrapolation.
    Both the :class:`~apd.resolvers.external.wikipedia_name_resolver.WikipediaNameResolver` and the :class:`~apd.resolvers.external.wikipedia_search_resolver.WikipediaSearchResolver` return participants as Wikipedia concepts.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ..extrapolator import Extrapolator

class WikipediaAttributeExtrapolator(Extrapolator):
    """
    The :class:`~WikipediaAttributeExtrapolator` relies on understanding to extrapolate participants.
    Understanding, here, means what makes a participant a participant.
    The class uses the :class:`~attributes.extractors.linguistic.LinguisticExtractor` to create profiles of resolved participants and looks for other participants with similar attributes.
    """
