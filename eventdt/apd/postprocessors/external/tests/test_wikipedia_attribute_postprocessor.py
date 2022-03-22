"""
Test the functionality of the :class:`~apd.postprocessors.wikipedia_attribute_postprocessor.WikipediaAttributePostprocessor`.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from apd.postprocessors.external.wikipedia_attribute_postprocessor import WikipediaAttributePostprocessor

class TestWikipediaAttributePostprocessor(unittest.TestCase):
    """
    Test the functionality of the :class:`~apd.postprocessors.wikipedia_attribute_postprocessor.WikipediaAttributePostprocessor`.
    """

    pass
