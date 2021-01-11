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

    def test_extract_lowercase_keys(self):
        """
        Test that when extracting attributes, all keys are in lowercase.
        """

        sentence = "Memphis Depay, also known simply as Memphis, is a Dutch professional footballer and rapper who plays as a forward for French football club Lyon and the Netherlands national team."
        extractor = LinguisticExtractor()
        profile = extractor.extract(sentence)
        self.assertTrue(all( name.lower() == name for name in profile.attributes ))

    def test_extract_lowercase_values(self):
        """
        Test that when extracting attributes, all values are in lowercase.
        """

        sentence = "Memphis Depay, also known simply as Memphis, is a Dutch professional footballer and rapper who plays as a forward for French football club Lyon and the Netherlands national team."
        extractor = LinguisticExtractor()
        profile = extractor.extract(sentence)
        self.assertTrue(all( value.lower() == value for values in profile.attributes.values() for value in values ))

    def test_extract_multiple_sentences(self):
        """
        Test that when providing multiple sentences, attributes are extracted from each.
        """

        sentences = [ "Memphis Depay is a footballer.", "He plays as a forward." ]
        extractor = LinguisticExtractor()
        profile = extractor.extract(' '.join(sentences))

        """
        Parse the first sentence.
        """
        p1 = extractor.extract(sentences[0])
        self.assertTrue(p1.attributes)
        for name, value in p1.attributes.items():
            self.assertTrue(name in profile.attributes)
            self.assertEqual(value, profile.attributes[name])

        """
        Parse the second sentence.
        """
        p2 = extractor.extract(sentences[1])
        self.assertTrue(p2.attributes)
        for name, value in p2.attributes.items():
            self.assertTrue(name in profile.attributes)
            self.assertEqual(value, profile.attributes[name])

        """
        Make sure that all attributes from both sentences are present in either sentence's attributes.
        """
        self.assertTrue(all( name in p1.attributes or name in p2.attributes for name in profile.attributes ))

    def test_extract_simple(self):
        """
        Test extracting attributes from simple sentences.
        """

        extractor = LinguisticExtractor()

        sentence = "Memphis Depay is a footballer."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'footballer' } }, profile.attributes)

        sentence = "Memphis Depay plays as a forward."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'plays': { 'forward' } }, profile.attributes)

    def test_extract_conjunctions(self):
        """
        Test extracting attributes which have conjunctions.
        """

        extractor = LinguisticExtractor()

        sentence = "Memphis Depay is a footballer and rapper."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'footballer', 'rapper' } }, profile.attributes)

        sentence = "Memphis Depay plays as a forward and midfielder."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'plays': { 'forward', 'midfielder' } }, profile.attributes)

    def test_extract_conjunctions(self):
        """
        Test extracting attributes which have conjunctions.
        """

        extractor = LinguisticExtractor()

        sentence = "Memphis Depay is a footballer, rapper and preacher."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'footballer', 'preacher', 'rapper' } }, profile.attributes)

        sentence = "Memphis Depay plays as a forward, winger and midfielder."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'plays': { 'forward', 'winger', 'midfielder' } }, profile.attributes)
