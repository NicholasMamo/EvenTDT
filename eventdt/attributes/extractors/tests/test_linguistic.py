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
        self.assertEqual({ 'plays_as': { 'forward' } }, profile.attributes)

    def test_extract_sets(self):
        """
        Test that when extracting attributes, the extractor returns sets for attribute values.
        """

        extractor = LinguisticExtractor()

        sentence = "Memphis Depay is a footballer and rapper who plays for Lyon."
        profile = extractor.extract(sentence)
        self.assertTrue(all(set == type(value) for value in profile.attributes.values()))
        self.assertEqual({ 'is': { 'footballer', 'rapper' }, 'plays_for': { 'lyon' } }, profile.attributes)
        self.assertEqual({ 'is': { 'rapper', 'footballer' }, 'plays_for': { 'lyon' } }, profile.attributes)

    def test_extract_conjunctions_and(self):
        """
        Test extracting attributes which have _and_ conjunctions.
        """

        extractor = LinguisticExtractor()

        sentence = "Memphis Depay is a footballer and rapper."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'footballer', 'rapper' } }, profile.attributes)

        sentence = "Memphis Depay plays as a forward and midfielder."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'plays_as': { 'forward', 'midfielder' } }, profile.attributes)

    def test_extract_conjunctions_or(self):
        """
        Test extracting attributes which have _or_ conjunctions.
        """

        extractor = LinguisticExtractor()

        sentence = "Memphis Depay is a footballer or rapper, depending on who you ask."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'footballer', 'rapper' } }, profile.attributes)

        sentence = "Memphis Depay plays as a forward or midfielder."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'plays_as': { 'forward', 'midfielder' } }, profile.attributes)

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
        self.assertEqual({ 'plays_as': { 'forward', 'winger', 'midfielder' } }, profile.attributes)

    def test_extract_prepositions_appended_to_name(self):
        """
        Test that when extracting attributes with prepositions, the preposition is appended to the name.
        """

        extractor = LinguisticExtractor()

        sentence = "Memphis Depay plays as a forward, winger and midfielder."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'plays_as': { 'forward', 'winger', 'midfielder' } }, profile.attributes)

    def test_extract_prepositions_separate(self):
        """
        Test that when an attribute has several prepositions, the values are stored separately.
        """

        extractor = LinguisticExtractor()

        sentence = "Memphis Depay plays as a forward, winger and midfielder for Lyon."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'plays_as': { 'forward', 'winger', 'midfielder' }, 'plays_for': { 'lyon' } }, profile.attributes)

        sentence = "Memphis Depay plays as a forward, winger and midfielder for Lyon with boots."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'plays_as': { 'forward', 'winger', 'midfielder' }, 'plays_for': { 'lyon' }, 'plays_with': { 'boots' } }, profile.attributes)

    def test_extract_real_examples(self):
        """
        Test extracting attributes from real example strings.

        Some mistakes, such as in Lautaro Martinez's example, are due to NLTK's incorrect tagging.
        """

        extractor = LinguisticExtractor()
        sentence = "Memphis Depay, also known simply as Memphis, is a Dutch professional footballer and rapper who plays as a forward for French football club Lyon and the Netherlands national team."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'known_as': { 'memphis' }, 'is': { 'dutch professional footballer', 'rapper' }, 'plays_as': { 'forward' }, 'plays_for': { 'lyon', 'netherlands national team' } }, profile.attributes)

        sentence = "Tinotenda \"Tino\" Kadewere is a Zimbabwean professional footballer who plays for Ligue 1 side Lyon and the Zimbabwe national team as a striker."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'zimbabwean professional footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'lyon', 'zimbabwe national team' } }, profile.attributes)

        sentence = "Lucas Tolentino Coelho de Lima, or simply Lucas Paquetá, is a Brazilian professional footballer who plays as an attacking midfielder for French Ligue 1 club Lyon and the Brazil national team."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'brazilian professional footballer' }, 'plays_as': { 'attacking midfielder' }, 'plays_for': { 'lyon', 'brazil national team' } }, profile.attributes)

        sentence = "Thiago Henrique Mendes Ribeiro is a Brazilian professional footballer who plays as a central midfielder for French club Lyon."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'brazilian professional footballer' }, 'plays_as': { 'central midfielder' }, 'plays_for': { 'lyon' } }, profile.attributes)

        sentence = "Jason Grégory Marianne Denayer is a Belgian professional footballer who plays as a centre-back for French club Lyon and the Belgium national side."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'belgian professional footballer' }, 'plays_as': { 'centre-back' }, 'plays_for': { 'lyon', 'belgium national side' } }, profile.attributes)

        sentence = "Romelu Menama Lukaku Bolingoli is a Belgian professional footballer who plays as a striker for Serie A club Inter Milan and the Belgium national team."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'belgian professional footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'inter milan', 'belgium national team' } }, profile.attributes)

        sentence = "Lautaro Javier Martínez is an Argentine professional footballer who plays as a striker for Italian club Inter Milan and the Argentina national team."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'argentine professional footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'inter milan', 'argentina national team' } }, profile.attributes)

        sentence = "Donald John Trump is the 45th and current president of the United States of America."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { '45th and current president' }, 'is_of': { 'united states', 'america' } }, profile.attributes)

        sentence = "Joseph Robinette Biden Jr. is an American politician and the president-elect of the United States."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'american politician', 'president-elect' }, 'is_of': { 'united states' } }, profile.attributes)
