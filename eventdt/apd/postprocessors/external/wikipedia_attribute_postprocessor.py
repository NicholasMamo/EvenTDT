"""
The :class:`~WikipediaAttributePostprocessor` creates an :class:`~attributes.profile.Profile` for each participant.
The profile describes participants in terms of their attributes.

.. note::

    The :class:`~WikipediaAttributePostprocessor` assumes that the resolved participants map to Wikipedia articles.
    Therefore Wikipedia-based resolvers and extrapolators make for good candidates before post-processing.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ..postprocessor import Postprocessor

class WikipediaAttributePostprocessor(Postprocessor):
    """
    The :class:`~WikipediaAttributePostprocessor` assumes that all participants map to Wikipedia articles.
    It uses the definition sentence, the first one in the article, to build a :class:`~attributes.profile.Profile` with attributes for each participant.
    """

    pass
