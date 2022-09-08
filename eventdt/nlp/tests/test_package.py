"""
Run unit tests on the :mod:`~nlp` package functions.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

import nlp
from wikinterface import text as wikitext

class TestPackage(unittest.TestCase):
    """
    Run unit tests on the :mod:`~nlp` package functions.
    """

    def test_entities_returns_list(self):
        """
        Test that extracting entities returns a list.
        """

        text = 'Red Bull Racing, also simply known as Red Bull or RBR and competing as Oracle Red Bull Racing, is a Formula One racing team, racing under an Austrian licence and based in the United Kingdom.'
        self.assertEqual(list, type(nlp.entities(text)))

    def test_entities_strings(self):
        """
        Test that extracting entities returns a list of tuples, containing named entities and their types.
        """

        text = 'Red Bull Racing, also simply known as Red Bull or RBR and competing as Oracle Red Bull Racing, is a Formula One racing team, racing under an Austrian licence and based in the United Kingdom.'
        self.assertTrue(all( tuple == type(ne) for ne in nlp.entities(text) ))
        self.assertTrue(all( str == type(entity) and str == type(netype)
                             for entity, netype in nlp.entities(text) ))

    def test_entities_empty(self):
        """
        Test that extracting entities from an empty string returns an empty list.
        """

        text = ''
        self.assertEqual([ ], nlp.entities(text))

    def test_entities_no_named_entities(self):
        """
        Test that if a string has no named entities, the function returns an empty list.
        """

        self.assertEqual([ ], nlp.entities("I'm heading home"))

    def test_entities_all(self):
        """
        Test that extracting entities returns all of them.
        """

        text = 'Red Bull Racing, also simply known as Red Bull or RBR and competing as Oracle Red Bull Racing, is a Formula One racing team, racing under an Austrian licence and based in the United Kingdom.'
        self.assertTrue(any( entity == 'Red Bull' for entity, _ in nlp.entities(text) ))
        self.assertTrue(any( entity == 'Oracle Red Bull Racing' for entity, _ in nlp.entities(text) ))

    def test_entities_multiple_sentences(self):
        """
        Test that extracting entities returns all entities from all sentences.
        """

        text = """Red Bull Racing, also simply known as Red Bull or RBR and competing as Oracle Red Bull Racing, is a Formula One racing team, racing under an Austrian licence and based in the United Kingdom.
                  It is one of two Formula One teams owned by beverage company Red Bull GmbH, the other being Scuderia AlphaTauri (previously Scuderia Toro Rosso)."""
        self.assertTrue(any( entity == 'Red Bull' for entity, _ in nlp.entities(text) ))
        self.assertTrue(any( entity == 'Oracle Red Bull Racing' for entity, _ in nlp.entities(text) ))
        self.assertTrue(any( entity == 'Red Bull GmbH' for entity, _ in nlp.entities(text) ))
        self.assertTrue(any( entity == 'Scuderia AlphaTauri' for entity, _ in nlp.entities(text) ))

    def test_entities_repeated(self):
        """
        Test that extracting entities returns repeated ones multiple times.
        """

        text = """Salzburg is a state (Land) of the modern Republic of Austria.
                 It is officially named Land Salzburg to distinguish it from its eponymous capital — the city of Salzburg.
                 For centuries, it was an independent Prince-Bishopric of the Holy Roman Empire."""
        self.assertEqual(2, len([ entity for entity, netype in nlp.entities(text)
                                         if entity == 'Salzburg' ]))

    def test_entities_in_text(self):
        """
        Test that all retrieved entities appear in the text.
        """

        text = """Salzburg is a state (Land) of the modern Republic of Austria.
                 It is officially named Land Salzburg to distinguish it from its eponymous capital — the city of Salzburg.
                 For centuries, it was an independent Prince-Bishopric of the Holy Roman Empire."""
        self.assertTrue(all( entity in text for entity, _ in nlp.entities(text) ))

    def test_entities_adjacent(self):
        """
        Test that adjacent entities with the same type that NLTK captures separetly are combined.
        """

        text = """Max Emilian Verstappen (born 30 September 1997) is a Belgian-Dutch racing driver and the 2021 Formula One World Champion."""
        # NOTE: NLTK splits 'Max' from 'Emilian Verstappen'
        self.assertTrue(any( 'Max Emilian Verstappen' == entity for entity, _ in nlp.entities(text) ))

    def test_entities_known_type(self):
        """
        Test that all entities have a known type.
        """

        text = """Salzburg is a state (Land) of the modern Republic of Austria.
                 It is officially named Land Salzburg to distinguish it from its eponymous capital — the city of Salzburg.
                 For centuries, it was an independent Prince-Bishopric of the Holy Roman Empire."""
        self.assertTrue(all( netype in [ 'PERSON', 'ORGANIZATION', 'GPE' ] for _, netype in nlp.entities(text) ))

    def test_entities_no_type(self):
        """
        Test that when extracting entities, if no type is given, the function returns all types.
        """

        text = """Salzburg is a state (Land) of the modern Republic of Austria.
                 It is officially named Land Salzburg to distinguish it from its eponymous capital — the city of Salzburg.
                 For centuries, it was an independent Prince-Bishopric of the Holy Roman Empire."""
        self.assertTrue(any( netype == 'PERSON' for _, netype in nlp.entities(text) ))
        self.assertTrue(any( netype == 'GPE' for _, netype in nlp.entities(text) ))
        self.assertTrue(any( netype == 'ORGANIZATION' for _, netype in nlp.entities(text) ))

    def test_entities_filter_by_type(self):
        """
        Test that when an entity type is given, all returned named entities have the given type.
        """

        text = """Salzburg is a state (Land) of the modern Republic of Austria.
                 It is officially named Land Salzburg to distinguish it from its eponymous capital — the city of Salzburg.
                 For centuries, it was an independent Prince-Bishopric of the Holy Roman Empire."""

        self.assertTrue(all( netype == 'PERSON' for _, netype in nlp.entities(text, netype='PERSON') ))
        self.assertTrue(all( netype == 'GPE' for _, netype in nlp.entities(text, netype='GPE') ))
        self.assertTrue(all( netype == 'ORGANIZATION' for _, netype in nlp.entities(text, netype='ORGANIZATION') ))

    def test_entities_type_case_insensitive(self):
        """
        Test that the given entity type is case insensitive.
        """

        text = """Salzburg is a state (Land) of the modern Republic of Austria.
                 It is officially named Land Salzburg to distinguish it from its eponymous capital — the city of Salzburg.
                 For centuries, it was an independent Prince-Bishopric of the Holy Roman Empire."""

        self.assertTrue(all( netype == 'PERSON' for _, netype in nlp.entities(text, netype='person') ))
        self.assertTrue(all( netype == 'GPE' for _, netype in nlp.entities(text, netype='gpe') ))
        self.assertTrue(all( netype == 'ORGANIZATION' for _, netype in nlp.entities(text, netype='Organization') ))

    def test_entities_unknown_type(self):
        """
        Test that filtering named entities by an unknown type returns an empty list of named entities.
        """

        text = """Salzburg is a state (Land) of the modern Republic of Austria.
                 It is officially named Land Salzburg to distinguish it from its eponymous capital — the city of Salzburg.
                 For centuries, it was an independent Prince-Bishopric of the Holy Roman Empire."""
        self.assertEqual([ ], nlp.entities(text, netype='LOCATION'))

    def test_entities_several_types(self):
        """
        Test that extracting entities with several types returns all types.
        """

        text = """San Antonio, officially the City of San Antonio, is the seventh-most populous city in the United States,
                  second largest city in the Southern United States, and the second-most populous city in Texas
                  as well as the 12th most populous city in North America with 1,434,625 residents in 2020."""
        self.assertTrue(any( netype == 'GPE' for _, netype in nlp.entities(text, netype=['GPE', 'LOCATION']) ))
        self.assertTrue(any( netype == 'LOCATION' for _, netype in nlp.entities(text, netype=['GPE', 'LOCATION']) ))

    def test_entities_several_types_separate(self):
        """
        Test that extracting entities with several types is identical to extracting each type separately.
        """

        text = """San Antonio, officially the City of San Antonio, is the seventh-most populous city in the United States,
                  second largest city in the Southern United States, and the second-most populous city in Texas
                  as well as the 12th most populous city in North America with 1,434,625 residents in 2020."""
        self.assertEqual(set(nlp.entities(text, netype='GPE') + nlp.entities(text, netype='LOCATION')),
                         set(nlp.entities(text, netype=['GPE', 'LOCATION'])))

    def test_entities_known_types(self):
        """
        Test that all named types can be handled by the `entities` function.
        """

        types = [ 'PERSON', 'ORGANIZATION', 'FACILITY', 'GPE', 'GSP', 'LOCATION' ]

        text = wikitext.collect('United States', introduction_only=False)['United States']
        entities = nlp.entities(text)
        self.assertTrue(all( _type in types for _, _type in entities ))

        text = wikitext.collect('United Kingdom', introduction_only=False)['United Kingdom']
        entities = nlp.entities(text)
        self.assertTrue(all( _type in types for _, _type in entities ))

    def test_remove_parentheses_original(self):
        """
        Test that removing the parentheses reconstructs the sentence with overwriting the original string.
        """

        sentence = "Pope Francis (Latin: Franciscus; Italian: Francesco; Spanish: Francisco; born Jorge Mario Bergoglio,[b] 17 December 1936) is the head of the Catholic Church and sovereign of the Vatican City State since 2013."
        clean = nlp.remove_parentheses(sentence)
        self.assertEqual("Pope Francis (Latin: Franciscus; Italian: Francesco; Spanish: Francisco; born Jorge Mario Bergoglio,[b] 17 December 1936) is the head of the Catholic Church and sovereign of the Vatican City State since 2013.", sentence)

    def test_remove_parentheses_none(self):
        """
        Test that a text without parentheses is unchanged when removing parentheses.
        """

        sentence = "Europe is a continent, also recognised as part of Eurasia, located entirely in the Northern Hemisphere and mostly in the Eastern Hemisphere."
        self.assertEqual(sentence, nlp.remove_parentheses(sentence))

    def test_remove_parentheses_simple(self):
        """
        Test that a text with parentheses is cleaned.
        """

        sentence = "Kylian Mbappé Lottin (born 20 December 1998) is a French professional footballer who plays as a forward for Ligue 1 club Paris Saint-Germain and the France national team."
        self.assertEqual("Kylian Mbappé Lottin is a French professional footballer who plays as a forward for Ligue 1 club Paris Saint-Germain and the France national team.", nlp.remove_parentheses(sentence))

    def test_remove_parentheses_multiple(self):
        """
        Test that when a text includes multiple parentheses, all of them are removed.
        """

        sentence = "The eurozone, officially called the euro area, is a monetary union of 19 member states of the European Union (EU) that have adopted the euro (€) as their primary currency and sole legal tender."
        self.assertEqual("The eurozone, officially called the euro area, is a monetary union of 19 member states of the European Union that have adopted the euro as their primary currency and sole legal tender.", nlp.remove_parentheses(sentence))

        sentence = "Kyiv (/ˈkiːjɪv/ KEE-yiv,[10] /kiːv/ KEEV[11]) or Kiev (/ˈkiːɛv/ KEE-ev;[12][13] Ukrainian: Київ, romanized: Kyiv, pronounced [ˈkɪjiu̯] (audio speaker iconlisten)) is the capital and most populous city of Ukraine."
        self.assertEqual("Kyiv or Kiev is the capital and most populous city of Ukraine.", nlp.remove_parentheses(sentence))

    def test_remove_parentheses_phonemes(self):
        """
        Test that a text with parentheses containing phonemes are removed.
        """

        sentence = "Kyiv (/ˈkiːjɪv/ KEE-yiv,[10] /kiːv/ KEEV[11]) or Kiev (/ˈkiːɛv/ KEE-ev;[12][13] Ukrainian: Київ, romanized: Kyiv, pronounced [ˈkɪjiu̯] (audio speaker iconlisten)) is the capital and most populous city of Ukraine."
        self.assertEqual("Kyiv or Kiev is the capital and most populous city of Ukraine.", nlp.remove_parentheses(sentence))

    def test_remove_parentheses_nested(self):
        """
        Test that if a text has nested parameters, all of them are removed.

        Note that *Eastern* is tagged as a proper noun and is thus separate from the complete phrase, *Eastern and Northern Hemispheres*.
        """

        sentence = "Asia (/ˈeɪʒə, ˈeɪʃə/ (audio speaker iconlisten)) is Earth's largest and most populous continent, located primarily in the Eastern and Northern Hemispheres."
        self.assertEqual("Asia is Earth's largest and most populous continent, located primarily in the Eastern and Northern Hemispheres.", nlp.remove_parentheses(sentence))

        sentence = "Lionel Andrés Messi (Spanish pronunciation: [ljoˈnel anˈdɾes ˈmesi] (audio speaker iconlisten); born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for Ligue 1 club Paris Saint-Germain and captains the Argentina national team."
        self.assertEqual("Lionel Andrés Messi, also known as Leo Messi, is an Argentine professional footballer who plays as a forward for Ligue 1 club Paris Saint-Germain and captains the Argentina national team.", nlp.remove_parentheses(sentence))

    def test_has_year(self):
        """
        Test that when checking for a year, the function returns a boolean.
        """

        text = 'Youssouf Koné (footballer, born 1995)'
        self.assertEqual(bool, type(nlp.has_year(text)))

    def test_has_year_range(self):
        """
        Test that when checking for a year in a range, the function returns `True`.
        """

        text = '2019–20 Premier League'
        self.assertTrue(nlp.has_year(text))

    def test_has_year_short_number(self):
        """
        Test that when checking for a year with a short number, the function does not detect a year.
        """

        text = 'Area 51'
        self.assertFalse(nlp.has_year(text))

    def test_has_year_long_number(self):
        """
        Test that when checking for a year with a long number, the function does not detect a year.
        """

        text = '1234567890'
        self.assertFalse(nlp.has_year(text))

    def test_transliterate_returns_str(self):
        """
        Test that when transliterating strings, a string is returned.
        """

        text = 'Il joue très gros... Peut-être sa dernière chance'
        self.assertEqual(str, type(nlp.transliterate(text)))

    def test_transliterate_same_length(self):
        """
        Test that when transliterating strings, a string with the same length is returned.
        """

        text = 'Il joue très gros... Peut-être sa dernière chance'
        self.assertEqual(len(text), len(nlp.transliterate(text)))

    def test_transliterate_capitalization(self):
        """
        Test that when transliterating strings, capitalization is respected.
        """

        text = 'Être, c\'est beau'
        self.assertEqual('Etre, c\'est beau', nlp.transliterate(text))

    def test_transliterate_french_special_characters(self):
        """
        Test that when French special_characters are normalized, they are converted to the correct character.
        """

        text = 'Il joue très gros... Peut-être sa dernière chance'
        self.assertEqual('Il joue tres gros... Peut-etre sa derniere chance', nlp.transliterate(text))

    def test_transliterate_germanic_special_characters(self):
        """
        Test that when Germanic special_characters are normalized, they are converted to the correct character.
        """

        text = 'Så leker Özil äntligen'
        self.assertEqual('Sa leker Ozil antligen', nlp.transliterate(text))

    def test_transliterate_maltese_special_characters(self):
        """
        Test that when Maltese special_characters are normalized, they are converted to the correct character.
        Note that this does not apply to Ħ/ħ.
        """

        text = 'Ċikku żar lil Ġanni il-Ħamrun'
        self.assertEqual('Cikku zar lil Ganni il-Ħamrun', nlp.transliterate(text))