"""
Run unit tests on the :class:`~attributes.extractors.linguistic.LinguisticExtractor` class.
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from attributes.profile import Profile
from attributes.extractors import LinguisticExtractor

class TestLinguisticExtractor(unittest.TestCase):
    """
    Test the :class:`~attributes.extractors.linguistic.LinguisticExtractor` class.
    """

    def test_init_default_grammar(self):
        """
        Test that when no grammar is provided, the extractor uses a default grammar.
        """

        extractor = LinguisticExtractor()
        self.assertTrue(extractor.parser._grammar)

    def test_init_override_grammar(self):
        """
        Test that when providing a grammar, it overrides the class' default grammar.
        """

        grammar = "NP: { <DT>?<JJ.*|VBG|NN.*|CD>*<NN.*> }"
        extractor = LinguisticExtractor(grammar)
        self.assertEqual(grammar, extractor.parser._grammar)

    def test_extract_returns_profile(self):
        """
        Test that when extracting attributes, the function always returns a profile.
        """

        extractor = LinguisticExtractor()
        self.assertEqual(Profile, type(extractor.extract('')))
