"""
Test the functionality of the Wikipedia attribute extrapolator.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from apd.extrapolators.external.wikipedia_attribute_extrapolator import WikipediaAttributeExtrapolator

class TestWikipediaAttributeExtrapolator(unittest.TestCase):
    """
    Test the implementation and results of the Wikipedia attribute extrapolator.
    """
