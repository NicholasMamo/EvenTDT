"""
The :class:`~WikipediaAttributePostprocessor` creates an :class:`~attributes.profile.Profile` for each participant.
The profile describes participants in terms of their attributes.

.. note::

    The :class:`~WikipediaAttributePostprocessor` assumes that the resolved participants map to Wikipedia articles.
    Therefore Wikipedia-based resolvers and extrapolators make for good candidates before post-processing.
"""

import nltk
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ..postprocessor import Postprocessor
from attributes import Profile
from attributes.extractors import LinguisticExtractor
from wikinterface import info, text

class WikipediaAttributePostprocessor(Postprocessor):
    """
    The :class:`~WikipediaAttributePostprocessor` assumes that all participants map to Wikipedia articles.
    It uses the definition sentence, the first one in the article, to build a :class:`~attributes.profile.Profile` with attributes for each participant.

    :ivar extractor: The extractor to use to build profiles.
    :vartype extractor: :class:`~attributes.extractors.linguistic.LinguisticExtractor`
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the postprocessor with an extractor.
        """

        self.extractor = LinguisticExtractor()

    def postprocess(self, participants, *args, **kwargs):
        """
        Post-process the given participants.

        :param participants: The participants to postprocess.
        :type participants: list of str

        :return: The postprocessed participants, a mapping from the original participants to their post-processed version.
        :rtype: dict
        """

        return self._build_profiles(participants)

    def _build_profiles(self, titles):
        """
        Build attribute profiles from the given Wikipedia articles.

        For each article, the function returns a :class:`~attributes.profile.Profile`.
        The profile considers only the first sentence of the article, since it usually refers unambiguously to the article's subject.

        .. note:

            The function builds profiles in bulk, rather than one-by-one, to minimize the number of requests and maximize throughput.

        :param titles: The Wikipedia article titles.
        :type titles: list of str

        :return: A dictionary with the Wikipedia titles as keys and the corresponding :class:`~attributes.profile.Profile` instances as values.
        :rtype: dict
        """

        # create the empty profiles in case some pages are missing
        profiles = { title: Profile(name=title) for title in titles }

        definitions = text.collect(titles, introduction_only=True)
        definitions = { title: text for title, text in definitions.items()
                                    if title in titles }
        definitions = { title: nltk.sent_tokenize(text)[0] if text else text
                        for title, text in definitions.items() }
        profiles.update({ title: self.extractor.extract(text, name=title, remove_parentheses=False)
                          for title, text in definitions.items() })

        return profiles
