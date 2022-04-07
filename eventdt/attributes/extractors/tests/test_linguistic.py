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

    def test_remove_references_original(self):
        """
        Test that removing references does not alter the original text.
        """

        extractor = LinguisticExtractor()

        sentence = "Open Data Science Conference, or ODSC, is an annual event held in Boston,[1] San Francisco, Brazil, London, and India.[2] "
        clean = extractor._remove_references(sentence)
        self.assertEqual("Open Data Science Conference, or ODSC, is an annual event held in Boston,[1] San Francisco, Brazil, London, and India.[2] ", sentence)
        profile = extractor.extract(sentence)
        self.assertEqual("Open Data Science Conference, or ODSC, is an annual event held in Boston,[1] San Francisco, Brazil, London, and India.[2] ", sentence)

        self.assertEqual({ 'is': { 'annual event' }, 'held_in': { 'boston', 'san francisco', 'brazil', 'london', 'india' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'event' }, 'held_in': { 'boston', 'san francisco', 'brazil', 'london', 'india' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_remove_references_none(self):
        """
        Test that if the text has no references, the sentence remains unchanged.
        """

        extractor = LinguisticExtractor()

        sentence = "Maximilian Beister (born 6 September 1990) is a German professional footballer who plays as a forward for FC Ingolstadt 04."
        clean = extractor._remove_references(sentence)
        self.assertEqual(sentence, clean)

        self.assertEqual({ 'is': { 'german professional footballer' }, 'plays_as': { 'forward' }, 'plays_for': { 'fc ingolstadt 04' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer' }, 'plays_as': { 'forward' }, 'plays_for': { 'fc ingolstadt 04' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_remove_references_alphabetical(self):
        """
        Test that a sentence with alphabetical references has none after removing them.
        """

        extractor = LinguisticExtractor()

        sentence = """Pyotr Mironovich Masherov[a] (né Mashero; 26 February [O.S. 13 February] 1919 – 4 October 1980) was a Soviet partisan, statesman, and one of the leaders of the Belarusian resistance during World War II who governed the Byelorussian Soviet Socialist Republic as First Secretary of the Communist Party of Byelorussia from 1965 until his death in 1980."""
        clean = extractor._remove_references(sentence)
        self.assertEqual(sentence.replace('[a]', ''), clean)

        self.assertEqual({ 'was': { 'soviet partisan', 'statesman', 'one' }, 'was_of': { 'leaders', 'belarusian resistance' },
                           'was_during': { 'world war ii' }, 'governed': { 'byelorussian soviet socialist republic'}, 'governed_as': { 'first secretary' },
                           'governed_of': { 'communist party', 'byelorussia' }, 'governed_from': { '1965' }, 'governed_until': { 'death' }, 'governed_in': { '1980' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'was': { 'partisan', 'statesman', 'one' }, 'was_of': { 'leaders', 'resistance' },
                           'was_during': { 'world war ii' }, 'governed': { 'socialist republic'}, 'governed_as': { 'first secretary' },
                           'governed_of': { 'communist party', 'byelorussia' }, 'governed_from': { '1965' }, 'governed_until': { 'death' }, 'governed_in': { '1980' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_remove_references(self):
        """
        Test that a sentence with one reference has none after removing them.
        """

        extractor = LinguisticExtractor()

        sentence = "Ernestine Tahedl (born 1940)[1] is a Canadian painter."
        clean = extractor._remove_references(sentence)
        self.assertEqual("Ernestine Tahedl (born 1940) is a Canadian painter.", clean)

        self.assertEqual({ 'is': { 'canadian painter' } }, LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'painter' } }, LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_remove_references_multiple(self):
        """
        Test removing multiple references from the same sentence.
        """

        extractor = LinguisticExtractor()

        sentence = "Jack Nasher (born 1979 in Korbach; Jack Lord Nasher-Awakemian)[1] is a bestselling author, negotiation advisor,[2] and a professor at Munich Business School.[3]"
        clean = extractor._remove_references(sentence)
        self.assertEqual("Jack Nasher (born 1979 in Korbach; Jack Lord Nasher-Awakemian) is a bestselling author, negotiation advisor, and a professor at Munich Business School.", clean)

        self.assertEqual({ 'is': { 'bestselling author', 'negotiation advisor', 'professor' }, 'is_at': { 'munich business school' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'bestselling author', 'negotiation advisor', 'professor' }, 'is_at': { 'munich business school' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_remove_references_adjacent(self):
        """
        Test removing adjacent references.
        """

        extractor = LinguisticExtractor()

        sentence = "Schlafen family member 11 is a protein that in humans is encoded by the SLFN11 gene.[3][4]"
        clean = extractor._remove_references(sentence)
        self.assertEqual("Schlafen family member 11 is a protein that in humans is encoded by the SLFN11 gene.", clean)

        self.assertEqual({ 'is': { 'protein' }, 'encoded_by': { 'slfn11 gene' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'protein' }, 'encoded_by': { 'slfn11 gene' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Anthidium eremicum is a species of bee in the family Megachilidae, the leaf-cutter, carder, or mason bees.[1][2]"
        clean = extractor._remove_references(sentence)
        self.assertEqual("Anthidium eremicum is a species of bee in the family Megachilidae, the leaf-cutter, carder, or mason bees.", clean)
        self.assertEqual({ 'is': { 'species' }, 'is_of': { 'bee' }, 'is_in': { 'megachilidae', 'leaf-cutter', 'carder', 'mason bees' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'species' }, 'is_of': { 'bee' }, 'is_in': { 'megachilidae', 'leaf-cutter', 'carder', 'mason bees' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Kraussaria angulifera is a species of grasshopper in the family Acrididae found in Africa.[1][2]"
        clean = extractor._remove_references(sentence)
        self.assertEqual("Kraussaria angulifera is a species of grasshopper in the family Acrididae found in Africa.", clean)
        self.assertEqual({ 'is': { 'species' }, 'is_of': { 'grasshopper' }, 'is_in': { 'acrididae' }, 'found_in': { 'africa' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'species' }, 'is_of': { 'grasshopper' }, 'is_in': { 'acrididae' }, 'found_in': { 'africa' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_remove_references_with_note(self):
        """
        Test that new lines are still separated by a space when removing references.
        """

        extractor = LinguisticExtractor()

        sentence = "Valletta is the southernmost capital of Europe,[5][note 1] and at just 0.61 square kilometres (0.24 sq mi), it is the European Union's smallest capital city.[6][7]"
        cleaned = extractor._remove_references(sentence)
        self.assertEqual("Valletta is the southernmost capital of Europe, and at just 0.61 square kilometres (0.24 sq mi), it is the European Union's smallest capital city.", cleaned)
        self.assertEqual({ 'is': { 'southernmost capital', 'european union \'s smallest capital city' }, 'is_of': { 'europe' }, 'is_at': { 'just 0.61 square kilometres' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'capital', 'capital city' }, 'is_of': { 'europe' }, 'is_at': { 'kilometres' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_returns_profile(self):
        """
        Test that when extracting attributes, the function always returns a profile.
        """

        extractor = LinguisticExtractor()
        self.assertEqual(Profile, type(extractor.extract('')))

    def test_extract_default_name(self):
        """
        Test that the default name is an empty string.
        """

        extractor = LinguisticExtractor()
        self.assertEqual('', extractor.extract('').name)

    def test_extract_with_name(self):
        """
        Test that when passing a name while extracting, it is saved as the profile's name.
        """

        extractor = LinguisticExtractor()
        self.assertEqual('profile name', extractor.extract('', name='profile name').name)

    def test_extract_with_text(self):
        """
        Test that the extractor creates a profile with the source text stored.
        """

        extractor = LinguisticExtractor()

        sentence = "Post Scriptum (abbreviated as PS) is a tactical first-person shooter video game set during the Second World War (specifically during the Battle of France, Operation Overlord, and Operation Market Garden) developed by British[2] studio Periscope Games."
        profile = extractor.extract(sentence, remove_parentheses=False)
        self.assertEqual(sentence, profile.text)
        self.assertEqual({ 'abbreviated_as': { 'ps' }, 'is': { 'tactical first-person shooter video game' }, 'set_during': { 'second world war' }, 'developed_by': { 'periscope games' } },
                         LinguisticExtractor(head_only=False).extract(sentence, remove_parentheses=False).attributes)
        self.assertEqual({ 'abbreviated_as': { 'ps' }, 'is': { 'first-person shooter video game' }, 'set_during': { 'world war' }, 'developed_by': { 'periscope games' } },
                         LinguisticExtractor(head_only=True).extract(sentence, remove_parentheses=False).attributes)

    def test_extract_with_parentheses(self):
        """
        Test that the extractor creates a profile with the original source text, including parentheses.
        """

        extractor = LinguisticExtractor()

        sentence = "Post Scriptum (abbreviated as PS) is a tactical first-person shooter video game set during the Second World War (specifically during the Battle of France, Operation Overlord, and Operation Market Garden) developed by British[2] studio Periscope Games."
        profile = extractor.extract(sentence, remove_parentheses=True)
        self.assertEqual(sentence, profile.text)
        self.assertEqual({ 'is': { 'tactical first-person shooter video game' }, 'set_during': { 'second world war' }, 'developed_by': { 'periscope games' } },
                         LinguisticExtractor(head_only=False).extract(sentence, remove_parentheses=True).attributes)
        # Second tagged as an adjective/JJ not as a proper noun/NNP
        self.assertEqual({ 'is': { 'first-person shooter video game' }, 'set_during': { 'world war' }, 'developed_by': { 'periscope games' } },
                         LinguisticExtractor(head_only=True).extract(sentence, remove_parentheses=True).attributes)

    def test_extract_with_references(self):
        """
        Test that the extractor creates a profile with the original source text, including references.
        """

        extractor = LinguisticExtractor()

        sentence = "John Alston Moorehead (February 19, 1882 – August 18, 1931)[1] was an American college football player and coach."
        profile = extractor.extract(sentence)
        self.assertEqual(sentence, profile.text)
        self.assertEqual({ 'was': { 'american college football player', 'coach' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'was': { 'college football player', 'coach' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

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

        sentence = "Memphis Depay is a footballer."
        self.assertEqual({ 'is': { 'footballer' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Memphis Depay plays as a forward."
        self.assertEqual({ 'plays_as': { 'forward' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'plays_as': { 'forward' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_sets(self):
        """
        Test that when extracting attributes, the extractor returns sets for attribute values.
        """

        extractor = LinguisticExtractor()

        sentence = "Memphis Depay is a footballer and rapper who plays for Lyon."
        profile = extractor.extract(sentence)
        self.assertTrue(all(set == type(value) for value in profile.attributes.values()))
        self.assertEqual({ 'is': { 'footballer', 'rapper' }, 'plays_for': { 'lyon' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer', 'rapper' }, 'plays_for': { 'lyon' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_with_lemmatization(self):
        """
        Test that when initializing the extractor with the lemmatizer, the attribute names are lemmatized.
        """

        sentence = "François Gérard Georges Nicolas Hollande is a French politician who served as president of France from 2012 to 2017."
        self.assertEqual({ 'is': { 'french politician' }, 'served_as': { 'president' }, 'served_of': { 'france' }, 'served_from': { '2012' }, 'served_to': { '2017'} },
                         LinguisticExtractor(head_only=False, lemmatize=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'politician' }, 'served_as': { 'president' }, 'served_of': { 'france' }, 'served_from': { '2012' }, 'served_to': { '2017'} },
                         LinguisticExtractor(head_only=True, lemmatize=False).extract(sentence).attributes)

        sentence = "François Gérard Georges Nicolas Hollande is a French politician who served as president of France from 2012 to 2017."
        self.assertEqual({ 'be': { 'french politician' }, 'serve_as': { 'president' }, 'serve_of': { 'france' }, 'serve_from': { '2012' }, 'serve_to': { '2017'} },
                         LinguisticExtractor(head_only=False, lemmatize=True).extract(sentence).attributes)
        self.assertEqual({ 'be': { 'politician' }, 'serve_as': { 'president' }, 'serve_of': { 'france' }, 'serve_from': { '2012' }, 'serve_to': { '2017'} },
                         LinguisticExtractor(head_only=True, lemmatize=True).extract(sentence).attributes)

    def test_extract_from_parentheses(self):
        """
        Test that the attributes may be extracted from parentheses (if the POS tagger does not mislabel them).
        """

        sentence = "Dale Owen Bennett (born 6 January 1990) is an English professional footballer, who played as a defender."
        self.assertEqual({ 'born': { '6 january 1990' }, 'is': { 'english professional footballer' }, 'played_as': { 'defender' } },
                         LinguisticExtractor(head_only=False).extract(sentence, remove_parentheses=False).attributes)
        self.assertEqual({ 'born': { '6 january 1990' }, 'is': { 'professional footballer' }, 'played_as': { 'defender' } },
                         LinguisticExtractor(head_only=True).extract(sentence, remove_parentheses=False).attributes)

    def test_extract_with_periods(self):
        """
        Test extracting attributes from a sentence that has periods.
        """

        sentence = "Ampelokipoi Larissa F.C. (Greek: ΑΟ Αμπελοκήπων) is a football club based in Larissa, Thessaly, Greece and currently competes in the Larissa FCA league."
        self.assertEqual({ 'is': { 'football club' }, 'based_in': { 'larissa', 'thessaly', 'greece' }, 'competes_in': { 'larissa fca league' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'football club' }, 'based_in': { 'larissa', 'thessaly', 'greece' }, 'competes_in': { 'larissa fca league' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_DATE_format_1(self):
        """
        Test extracting a date in the format DD MM YYYY.
        """

        sentence = "Emmanuel Jean-Michel Frédéric Macron is a French politician who has been serving as the president of France since 14 May 2017."
        self.assertEqual({ 'is': { 'french politician' }, 'serving_as': { 'president' }, 'serving_of': { 'france' }, 'serving_since': { '14 may 2017' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'politician' }, 'serving_as': { 'president' }, 'serving_of': { 'france' }, 'serving_since': { '14 may 2017' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_DATE_format_2(self):
        """
        Test extracting a date in the format MM DD, YYYY.
        """

        sentence = "William Henry Gates III (born on October 28, 1955) is an American business magnate, software developer, investor, author, and philanthropist."
        self.assertEqual({ 'born_on': { 'october 28 , 1955' }, 'is': { 'american business magnate', 'software developer', 'investor', 'author', 'philanthropist' } },
                         LinguisticExtractor(head_only=False).extract(sentence, remove_parentheses=False).attributes)
        self.assertEqual({ 'born_on': { 'october 28 , 1955' }, 'is': { 'business magnate', 'software developer', 'investor', 'author', 'philanthropist' } },
                         LinguisticExtractor(head_only=True).extract(sentence, remove_parentheses=False).attributes)

    def test_extract_DATE_format_3(self):
        """
        Test extracting a date in the format dd, DD MM YYYY.
        """

        sentence = "The Normandy landings were the landing operations and associated airborne operations on Tuesday, 6 June 1944 of the Allied invasion of Normandy in Operation Overlord during World War II."
        self.assertEqual({ 'were': { 'landing operations', 'associated airborne operations' }, 'were_on': { 'tuesday , 6 june 1944' }, 'were_of': { 'allied invasion', 'normandy' },
                           'were_in': { 'operation overlord' }, 'were_during': { 'world war ii' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'were': { 'operations', 'operations' }, 'were_on': { 'tuesday , 6 june 1944' }, 'were_of': { 'allied invasion', 'normandy' },
                           'were_in': { 'operation overlord' }, 'were_during': { 'world war ii' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_DATE_TIME(self):
        """
        Text extracting a date that has a time acts like a number.
        """

        sentence = """The attack on Pearl Harbor was a surprise military strike by the Imperial Japanese Navy Air Service
                      upon the United States against the naval base at Pearl Harbor in Honolulu, Territory of Hawaii,
                      just before 08:00, on Sunday, December 7, 1941."""
        self.assertEqual({ 'was': { 'military strike' }, 'was_by': { 'imperial japanese navy air service' },
                           'was_upon': { 'united states' }, 'was_against': { 'naval base' }, 'was_at': { 'pearl harbor' }, 'was_in': { 'territory', 'honolulu' }, 'was_of': { 'hawaii' },
                           'was_before': { '08:00' }, 'was_on': { 'sunday , december 7 , 1941' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        # 'surprise' incorrectly labelled as a noun/NN
        self.assertEqual({ 'was': { 'surprise military strike' }, 'was_by': { 'imperial japanese navy air service' },
                           'was_upon': { 'united states' }, 'was_against': { 'base' }, 'was_at': { 'pearl harbor' }, 'was_in': { 'territory', 'honolulu' }, 'was_of': { 'hawaii' },
                           'was_before': { '08:00' }, 'was_on': { 'sunday , december 7 , 1941' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_MOD_starts_with_number(self):
        """
        Test that a modifier may start with a number.
        """

        sentence = "The eurozone, officially called the euro area, is a monetary union of 19 member states of the European Union (EU) that have adopted the euro as their primary currency and sole legal tender."
        self.assertEqual({ 'called': { 'euro area' }, 'is': { 'monetary union' }, 'is_of': { 'member states', 'european union' }, 'adopted': { 'euro' }, 'adopted_as': { 'primary currency', 'sole legal tender' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'called': { 'area' }, 'is': { 'union' }, 'is_of': { 'member states', 'european union' }, 'adopted': { 'euro' }, 'adopted_as': { 'currency', 'tender' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_ENT_ends_number(self):
        """
        Test extracting an attribute value when it is an entity that ends with a number.
        """

        sentence = "Mark-Alexander Uth is a German footballer who plays as a striker for Bundesliga club Schalke 04."
        self.assertEqual({ 'is': { 'german footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'schalke 04' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'schalke 04' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_ENT_starts_number(self):
        """
        Test extracting an attribute value when it is an entity that starts with a number.
        """

        sentence = "Fabian Greilinger is a German professional footballer who plays as a winger for 1860 Munich."
        self.assertEqual({ 'is': { 'german professional footballer' }, 'plays_as': { 'winger' }, 'plays_for': { '1860 munich' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer' }, 'plays_as': { 'winger' }, 'plays_for': { '1860 munich' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_ENT_has_number(self):
        """
        Test extracting an attribute value when it is an entity that has a number in the middle.
        """

        sentence = "Dennis Erdmann is a German professional footballer who plays as a defensive midfielder or attacking midfielder for TSV 1860 Munich."
        self.assertEqual({ 'is': { 'german professional footballer' }, 'plays_as': { 'defensive midfielder', 'attacking midfielder' }, 'plays_for': { 'tsv 1860 munich' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer' }, 'plays_as': { 'midfielder', 'attacking midfielder' }, 'plays_for': { 'tsv 1860 munich' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_ENT_with_IN(self):
        """
        Test extracting an entity with a preposition in it.
        """

        sentence = "Donald John Trump is the 45th and current president of the United States of America."
        self.assertEqual({ 'is': { '45th and current president' }, 'is_of': { 'united states', 'america' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'president' }, 'is_of': { 'united states', 'america' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Sallie Kim is currently a U.S. Magistrate Judge of the United States District Court for the Northern District of California."
        self.assertEqual({ 'is': { 'u.s. magistrate judge' }, 'is_of': { 'united states district court', 'california' }, 'is_for': { 'northern district' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'u.s. magistrate judge' }, 'is_of': { 'united states district court', 'california' }, 'is_for': { 'northern district' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "The 2004 Kansas Jayhawks football team represented the University of Kansas in the 2004 NCAA Division I-A football season."
        self.assertEqual({ 'represented': { 'university' }, 'represented_of': { 'kansas' }, 'represented_in': { '2004 ncaa division i-a football season' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'represented': { 'university' }, 'represented_of': { 'kansas' }, 'represented_in': { '2004 ncaa division i-a football season' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Giuseppe Tartini was an Italian Baroque composer and violinist born in the Republic of Venice."
        self.assertEqual({ 'was': { 'italian baroque composer', 'violinist' }, 'born_in': { 'republic' }, 'born_of': { 'venice' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'was': { 'baroque composer', 'violinist' }, 'born_in': { 'republic' }, 'born_of': { 'venice' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_ENT_with_MOD(self):
        """
        Test that an entity may be preceded by a modifier.
        """

        sentence = "France, officially the French Republic, is a transcontinental country spanning Western Europe and overseas regions and territories in the Americas and the Atlantic, Pacific and Indian Oceans."
        self.assertEqual({ 'is': { 'transcontinental country' }, 'spanning': { 'western europe', 'overseas regions', 'territories' }, 'spanning_in': { 'americas', 'atlantic', 'pacific', 'indian oceans' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        # Indian is tagged as an adjective/JJ
        self.assertEqual({ 'is': { 'country' }, 'spanning': { 'western europe', 'regions', 'territories' }, 'spanning_in': { 'americas', 'atlantic', 'pacific', 'oceans' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_NAME_VBG(self):
        """
        Test that an attribute name may be a gerund.
        """

        sentence = "Emmanuel Jean-Michel Frédéric Macron is a French politician who has been serving as the president of France since 14 May 2017."
        self.assertEqual({ 'is': { 'french politician' }, 'serving_as': { 'president' }, 'serving_of': { 'france' }, 'serving_since': { '14 may 2017' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'politician' }, 'serving_as': { 'president' }, 'serving_of': { 'france' }, 'serving_since': { '14 may 2017' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_NAME_VBD(self):
        """
        Test that an attribute name may be in the past.
        """

        sentence = "Dale Owen Bennett (born 6 January 1990) is an English professional footballer, who played as a defender."
        self.assertEqual({ 'born': { '6 january 1990' }, 'is': { 'english professional footballer' }, 'played_as': { 'defender' } },
                         LinguisticExtractor(head_only=False).extract(sentence, remove_parentheses=False).attributes)
        self.assertEqual({ 'born': { '6 january 1990' }, 'is': { 'professional footballer' }, 'played_as': { 'defender' } },
                         LinguisticExtractor(head_only=True).extract(sentence, remove_parentheses=False).attributes)

    def test_extract_VALUE_DATE(self):
        """
        Test that a date is a valid attribute value.
        """

        sentence = "William Henry Gates III (born on October 28, 1955) is an American business magnate, software developer, investor, author, and philanthropist."
        self.assertEqual({ 'born_on': { 'october 28 , 1955' }, 'is': { 'american business magnate', 'software developer', 'investor', 'author', 'philanthropist' } },
                         LinguisticExtractor(head_only=False).extract(sentence, remove_parentheses=False).attributes)
        self.assertEqual({ 'born_on': { 'october 28 , 1955' }, 'is': { 'business magnate', 'software developer', 'investor', 'author', 'philanthropist' } },
                         LinguisticExtractor(head_only=True).extract(sentence, remove_parentheses=False).attributes)

        sentence = "Nicolas Paul Stéphane Sarközy de Nagy-Bocsa is a French politician who served as President of France from 16 May 2007 until 15 May 2012."
        self.assertEqual({ 'is': { 'french politician' }, 'served_as': { 'president' }, 'served_of': { 'france' }, 'served_from': { '16 may 2007' }, 'served_until': { '15 may 2012' } },
                         LinguisticExtractor(head_only=False).extract(sentence, remove_parentheses=False).attributes)
        self.assertEqual({ 'is': { 'politician' }, 'served_as': { 'president' }, 'served_of': { 'france' }, 'served_from': { '16 may 2007' }, 'served_until': { '15 may 2012' } },
                         LinguisticExtractor(head_only=True).extract(sentence, remove_parentheses=False).attributes)

    def test_extract_VALUE_CD(self):
        """
        Test that a number is a valid attribute value.
        """

        sentence = "François Gérard Georges Nicolas Hollande is a French politician who served as president of France from 2012 to 2017."
        self.assertEqual({ 'is': { 'french politician' }, 'served_as': { 'president' }, 'served_of': { 'france' }, 'served_from': { '2012' }, 'served_to': { '2017'} },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'politician' }, 'served_as': { 'president' }, 'served_of': { 'france' }, 'served_from': { '2012' }, 'served_to': { '2017'} },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUE_ENT_NP_head(self):
        """
        Test that when extracting values, if an entity is preceded by noun phrases, only the entity is retained.
        """

        sentence = "Lucas Tolentino Coelho de Lima known as Lucas Paquetá, is a Brazilian professional footballer who plays as an attacking midfielder for Ligue 1 club Lyon and the Brazil national team."
        self.assertEqual({ 'known_as': { 'lucas paquetá' }, 'is': { 'brazilian professional footballer' }, 'plays_as': { 'attacking midfielder' }, 'plays_for': { 'lyon', 'brazil national team' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'known_as': { 'lucas paquetá' }, 'is': { 'footballer' }, 'plays_as': { 'attacking midfielder' }, 'plays_for': { 'lyon', 'team' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Spalacopsis stolata is a species of beetle in the family Cerambycidae."
        self.assertEqual({ 'is': { 'species' }, 'is_of': { 'beetle' }, 'is_in': { 'cerambycidae' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'species' }, 'is_of': { 'beetle' }, 'is_in': { 'cerambycidae' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        # incorrect tagging of 'band/VBP'
        sentence = '"I Want Out" is a song by English rockabilly band Matchbox featuring Kirsty MacColl.'
        self.assertEqual({ 'is': { 'song' }, 'band': { 'matchbox' }, 'featuring': { 'kirsty maccoll' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'song' }, 'band': { 'matchbox' }, 'featuring': { 'kirsty maccoll' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Memphis Depay, also known simply as Memphis, is a Dutch professional footballer and rapper who plays as a forward for French football club Lyon and the Netherlands national team."
        self.assertEqual({ 'known_as': { 'memphis' }, 'is': { 'dutch professional footballer', 'rapper' }, 'plays_as': { 'forward' }, 'plays_for': { 'lyon', 'netherlands national team' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'known_as': { 'memphis' }, 'is': { 'professional footballer', 'rapper' }, 'plays_as': { 'forward' }, 'plays_for': { 'lyon', 'team' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Tinotenda \"Tino\" Kadewere is a Zimbabwean professional footballer who plays for Ligue 1 side Lyon and the Zimbabwe national team as a striker."
        self.assertEqual({ 'is': { 'zimbabwean professional footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'lyon', 'zimbabwe national team' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'lyon', 'team' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Thiago Henrique Mendes Ribeiro is a Brazilian professional footballer who plays as a central midfielder for French club Lyon."
        self.assertEqual({ 'is': { 'brazilian professional footballer' }, 'plays_as': { 'central midfielder' }, 'plays_for': { 'lyon' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer' }, 'plays_as': { 'midfielder' }, 'plays_for': { 'lyon' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Jason Grégory Marianne Denayer is a Belgian professional footballer who plays as a centre-back for French club Lyon and the Belgium national side."
        self.assertEqual({ 'is': { 'belgian professional footballer' }, 'plays_as': { 'centre-back' }, 'plays_for': { 'lyon', 'belgium national side' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer' }, 'plays_as': { 'centre-back' }, 'plays_for': { 'lyon', 'side' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Mathis Rayan Cherki (French pronunciation: ​[ʁajan ʃɛʁki]; Arabic: رايان شرقي; born 17 August 2003) is a French professional footballer who plays as attacking midfielder for Ligue 1 club Lyon."
        self.assertEqual({ 'is': { 'french professional footballer' }, 'plays_as': { 'attacking midfielder' }, 'plays_for': { 'lyon' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer' }, 'plays_as': { 'attacking midfielder' }, 'plays_for': { 'lyon' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Romelu Menama Lukaku Bolingoli is a Belgian professional footballer who plays as a striker for Serie A club Inter Milan and the Belgium national team."
        self.assertEqual({ 'is': { 'belgian professional footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'inter milan', 'belgium national team' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'inter milan', 'team' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Lautaro Javier Martínez is an Argentine professional footballer who plays as a striker for Italian club Inter Milan and the Argentina national team."
        self.assertEqual({ 'is': { 'argentine professional footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'inter milan', 'argentina national team' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'inter milan', 'team' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUE_JJ_NP(self):
        """
        Test that when extracting values, if a value has an adjective, both the adjective and the noun phrase are retained.
        """

        sentence = "Granada Club de Fútbol, S.A.D., known simply as Granada, is a Spanish football club in the city of Granada, in the autonomous community of Andalusia that plays in La Liga."
        self.assertEqual({ 'known_as': { 'granada' }, 'is': { 'spanish football club' }, 'is_in': { 'city', 'autonomous community' }, 'is_of': { 'granada', 'andalusia' }, 'plays_in': { 'la liga' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'known_as': { 'granada' }, 'is': { 'football club' }, 'is_in': { 'city', 'community' }, 'is_of': { 'granada', 'andalusia' }, 'plays_in': { 'la liga' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Naked Harbour (Finnish: Vuosaari) is a 2012 Finnish drama film directed by Aku Louhimies."
        self.assertEqual({ 'is': { '2012 finnish drama film' }, 'directed_by': { 'aku louhimies' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'drama film' }, 'directed_by': { 'aku louhimies' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUE_NP(self):
        """
        Test extracting values that are noun phrases.
        """

        sentence = """VR Kanojo (VR カノジョ) is a virtual reality social simulation game made by Illusion, released in February 2017
                      for the HTC Vive and Oculus Rift on Microsoft Windows PCs."""
        self.assertEqual({ 'is': { 'social simulation game' }, 'made_by': { 'illusion' }, 'released_in': { 'february 2017' },
                           'released_for': { 'htc vive', 'oculus rift' }, 'released_on': { 'microsoft windows pcs' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        # reality tagged as a noun/NN, not as an adjective /JJ
        self.assertEqual({ 'is': { 'reality social simulation game' }, 'made_by': { 'illusion' }, 'released_in': { 'february 2017' },
                           'released_for': { 'htc vive', 'oculus rift' }, 'released_on': { 'microsoft windows pcs' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUE_POS(self):
        """
        Test that if a value has a possessive, the object and subject are returned together.
        """

        sentence = "Asia (/ˈeɪʒə, ˈeɪʃə/ (audio speaker iconlisten)) is Earth's largest and most populous continent, located primarily in the Eastern and Northern Hemispheres."
        self.assertEqual({ 'is': { 'earth \'s largest and most populous continent' }, 'located_in': { 'eastern', 'northern hemispheres' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'continent' }, 'located_in': { 'eastern', 'northern hemispheres' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        # general tagged as an adjective/JJ by the POS tagger
        sentence = "Paul Charles François Adrien Henri Dieudonné Thiébault (14 December 1769, Berlin - 14 October 1846, Paris) was a general who fought in Napoleon I's army."
        self.assertEqual({ 'fought_in': { 'napoleon i \'s army' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'fought_in': { 'army' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_ENT_with_PRP(self):
        """
        Test that I is considered to be as part of the entity when it follows one.
        """

        sentence = "World War I, often abbreviated as WW I or WW1, also known as the First World War or the Great War, was an international conflict that began on 28 July 1914 and ended on 11 November 1918."
        self.assertEqual({ 'abbreviated_as': { 'ww i', 'ww1' }, 'known_as': { 'first world war', 'great war' }, 'was': { 'international conflict' }, 'began_on': { '28 july 1914' }, 'ended_on': { '11 november 1918' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'abbreviated_as': { 'ww i', 'ww1' }, 'known_as': { 'first world war', 'great war' }, 'was': { 'conflict' }, 'began_on': { '28 july 1914' }, 'ended_on': { '11 november 1918' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Paul Charles François Adrien Henri Dieudonné Thiébault (14 December 1769, Berlin - 14 October 1846, Paris) was a general who fought in Napoleon I's army."
        self.assertEqual({ 'fought_in': { 'napoleon i \'s army' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'fought_in': { 'army' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUES_CC_and(self):
        """
        Test extracting attributes which have _and_ conjunctions.
        """

        sentence = "Elon Reeve Musk FRS is an entrepreneur and business magnate."
        self.assertEqual({ 'is': { 'entrepreneur', 'business magnate' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'entrepreneur', 'business magnate' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Memphis Depay plays as a forward and midfielder."
        self.assertEqual({ 'plays_as': { 'forward', 'midfielder' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'plays_as': { 'forward', 'midfielder' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Joseph Robinette Biden Jr. is an American politician and the president-elect of the United States."
        self.assertEqual({ 'is': { 'american politician', 'president-elect' }, 'is_of': { 'united states' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'politician', 'president-elect' }, 'is_of': { 'united states' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUES_CC_or(self):
        """
        Test extracting attributes which have _or_ conjunctions.
        """

        sentence = "Memphis Depay is a footballer or rapper, depending on who you ask."
        self.assertEqual({ 'is': { 'footballer', 'rapper' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer', 'rapper' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Memphis Depay plays as a forward or midfielder."
        self.assertEqual({ 'plays_as': { 'forward', 'midfielder' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'plays_as': { 'forward', 'midfielder' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUES_multiple_CC(self):
        """
        Test extracting attributes which have multiple conjunctions.
        """

        sentence = "Jeffrey Preston Bezos is an American entrepreneur, media proprietor, investor and computer engineer and commercial astronaut."
        self.assertEqual({ 'is': { 'american entrepreneur', 'media proprietor', 'investor', 'computer engineer', 'commercial astronaut' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'entrepreneur', 'media proprietor', 'investor', 'computer engineer', 'astronaut' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Taipei, officially Taipei City, is the capital and a special municipality of Taiwan."
        self.assertEqual({ 'is': { 'capital', 'special municipality' }, 'is_of': { 'taiwan' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'capital', 'municipality' }, 'is_of': { 'taiwan' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "France, officially the French Republic, is a transcontinental country spanning Western Europe and overseas regions and territories in the Americas and the Atlantic, Pacific and Indian Oceans."
        self.assertEqual({ 'is': { 'transcontinental country' }, 'spanning': { 'western europe', 'overseas regions', 'territories' }, 'spanning_in': { 'americas', 'atlantic', 'pacific', 'indian oceans' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        # Indian tagged as an adjective/JJ, not a proper noun/NNP
        self.assertEqual({ 'is': { 'country' }, 'spanning': { 'western europe', 'regions', 'territories' }, 'spanning_in': { 'americas', 'atlantic', 'pacific', 'oceans' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUES_multiple_CC_with_oxford_comma(self):
        """
        Test extracting attributes which have multiple conjunctions.
        """

        sentence = "William Henry Gates III (born October 28, 1955) is an American business magnate, software developer, investor, author, and philanthropist."
        self.assertEqual({ 'is': { 'american business magnate', 'software developer', 'investor', 'author', 'philanthropist' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'business magnate', 'software developer', 'investor', 'author', 'philanthropist' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUES_CC(self):
        """
        Test extracting attributes which have conjunctions.
        """

        sentence = "Memphis Depay is a footballer, rapper and preacher."
        self.assertEqual({ 'is': { 'footballer', 'preacher', 'rapper' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'footballer', 'preacher', 'rapper' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Memphis Depay plays as a forward, winger and midfielder."
        self.assertEqual({ 'plays_as': { 'forward', 'winger', 'midfielder' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'plays_as': { 'forward', 'winger', 'midfielder' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUES_commas(self):
        """
        Test extracting attributes which have commas.
        """

        sentence = """Donetsk, formerly known as Aleksandrovka, Yuzivka (or Hughesovka), Stalin and Stalino,
                      is an industrial city in eastern Ukraine located on the Kalmius River in the disputed area of Donetsk Oblast."""
        self.assertEqual({ 'known_as': { 'aleksandrovka', 'yuzivka', 'stalin', 'stalino' }, 'is': { 'industrial city' },
                           'is_in': { 'eastern ukraine' }, 'located_on': { 'kalmius river' }, 'located_in': { 'disputed area' }, 'located_of': { 'donetsk oblast' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'known_as': { 'aleksandrovka', 'yuzivka', 'stalin', 'stalino' }, 'is': { 'city' },
                           'is_in': { 'ukraine' }, 'located_on': { 'kalmius river' }, 'located_in': { 'area' }, 'located_of': { 'donetsk oblast' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = """EMEA is a shorthand designation meaning Europe, the Middle East and Africa"""
        self.assertEqual({ 'is': { 'shorthand designation' }, 'meaning': { 'europe', 'middle east', 'africa' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'designation' }, 'meaning': { 'europe', 'middle east', 'africa' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Alexandra Talomaa (born 1975) is a Swedish songwriter who has written songs for A-Teens, Anders Fernette (previously Johansson), Backstreet Boys, Darin, Westlife and others."
        self.assertEqual({ 'is': { 'swedish songwriter' }, 'written': { 'songs' }, 'written_for': { 'a-teens', 'anders fernette', 'backstreet boys', 'darin', 'westlife', 'others' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'songwriter' }, 'written': { 'songs' }, 'written_for': { 'a-teens', 'anders fernette', 'backstreet boys', 'darin', 'westlife', 'others' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Marginella cleryi is a species of sea snail, a marine gastropod mollusk in the family Marginellidae, the margin snails."
        self.assertEqual({ 'is': { 'species' }, 'is_of': { 'sea snail', 'marine gastropod mollusk' }, 'is_in': { 'marginellidae', 'margin snails' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'species' }, 'is_of': { 'sea snail', 'gastropod mollusk' }, 'is_in': { 'marginellidae', 'margin snails' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Baitutan (Chinese: 白兔潭镇; pinyin: bái-tù-tán zhèn) is a town in the northern east of Liling City, Hunan, China."
        self.assertEqual({ 'is': { 'town' }, 'is_in': { 'northern east' }, 'is_of': { 'liling city', 'hunan', 'china' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'town' }, 'is_in': { 'east' }, 'is_of': { 'liling city', 'hunan', 'china' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUES_IN_between(self):
        """
        Test that when extracting a list of values with 'between' as the preposition, two values are extracted.
        """

        sentence = "Virginia, officially the Commonwealth of Virginia, is a state in the Mid-Atlantic and Southeastern regions of the United States, between the Atlantic Coast and the Appalachian Mountains."
        self.assertEqual({ 'is': { 'state' }, 'is_in': { 'mid-atlantic and southeastern regions' }, 'is_of': { 'united states' }, 'is_between': { 'atlantic coast', 'appalachian mountains' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        # Appalachian tagged as an adjective/JJ, not a proper noun/NNP
        self.assertEqual({ 'is': { 'state' }, 'is_in': { 'regions' }, 'is_of': { 'united states' }, 'is_between': { 'atlantic coast', 'mountains' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Wright Inlet is an ice-filled inlet receding westward between Cape Little and Cape Wheeler along the east coast of Palmer Land."
        self.assertEqual({ 'is': { 'receding westward' }, 'is_between': { 'cape little', 'cape wheeler' }, 'is_along': { 'east coast' }, 'is_of': { 'palmer land' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'receding westward' }, 'is_between': { 'cape little', 'cape wheeler' }, 'is_along': { 'coast' }, 'is_of': { 'palmer land' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUES_IN_appended_to_name(self):
        """
        Test that when extracting attributes with prepositions, the preposition is appended to the name.
        """

        sentence = "Memphis Depay plays as a forward, winger and midfielder."
        self.assertEqual({ 'plays_as': { 'forward', 'winger', 'midfielder' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'plays_as': { 'forward', 'winger', 'midfielder' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUES_IN_separate(self):
        """
        Test that when an attribute has several prepositions, the values are stored separately.
        """

        sentence = "Memphis Depay plays as a forward, winger and midfielder for Lyon."
        self.assertEqual({ 'plays_as': { 'forward', 'winger', 'midfielder' }, 'plays_for': { 'lyon' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'plays_as': { 'forward', 'winger', 'midfielder' }, 'plays_for': { 'lyon' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Olympique Lyonnais (French pronunciation: ​[ɔlɛ̃pik ljɔnɛ]), commonly referred to as simply Lyon (French pronunciation: ​[ljɔ̃]) or OL, is a French professional football club based in Lyon in Auvergne-Rhône-Alpes."
        self.assertEqual({ 'is': { 'french professional football club' }, 'referred_to': { 'lyon', 'ol' }, 'based_in': { 'lyon', 'auvergne-rhône-alpes' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'professional football club' }, 'referred_to': { 'lyon', 'ol' }, 'based_in': { 'lyon', 'auvergne-rhône-alpes' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        # Known as *Saint-Étienne* missed because the POS tagger identifies an end of a sentence after *A.S.S.E.*.
        sentence = "Association Sportive de Saint-Étienne Loire (French pronunciation: ​[sɛ̃t‿etjɛn lwaʁ]), commonly known as A.S.S.E. (French pronunciation: ​[a.ɛs.ɛs.ø]) or simply Saint-Étienne, is a professional football club based in Saint-Étienne in Auvergne-Rhône-Alpes, France."
        self.assertEqual({ 'known_as': { 'a.s.s.e' }, 'is': { 'professional football club' }, 'based_in': { 'saint-étienne', 'auvergne-rhône-alpes', 'france' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'known_as': { 'a.s.s.e' }, 'is': { 'football club' }, 'based_in': { 'saint-étienne', 'auvergne-rhône-alpes', 'france' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Brighton & Hove Albion Football Club (/ˈbraɪtən ... ˈhoʊv/), commonly referred to simply as Brighton, is an English professional football club based in the city of Brighton and Hove."
        self.assertEqual({ 'is': { 'english professional football club' }, 'based_in': { 'city' }, 'based_of': { 'brighton', 'hove' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'professional football club' }, 'based_in': { 'city' }, 'based_of': { 'brighton', 'hove' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

        sentence = "Lando Norris is a Belgian-British racing driver currently competing in Formula One with McLaren, racing under the British flag."
        self.assertEqual({ 'is': { 'belgian-british racing driver' }, 'competing_in': { 'formula one' }, 'competing_with': { 'mclaren' }, 'racing_under': { 'british flag' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'racing driver' }, 'competing_in': { 'formula one' }, 'competing_with': { 'mclaren' }, 'racing_under': { 'flag' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUES_split(self):
        """
        Test that when multiple attributes with the same name but split over different phrases, both are added to the same.
        """

        sentence = "Lawrence Joseph Ellison is an American businessman and investor who is the co-founder, executive chairman, chief technology officer and former chief executive officer of Oracle Corporation."
        self.assertEqual({ 'is': { 'american businessman', 'investor', 'co-founder', 'executive chairman', 'chief technology officer', 'former chief executive officer' }, 'is_of': { 'oracle corporation' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'is': { 'businessman', 'investor', 'co-founder', 'executive chairman', 'technology officer', 'executive officer' }, 'is_of': { 'oracle corporation' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)


    def test_extract_VALUES_TO(self):
        """
        Test that an attribute value may have *to* as a preposition.
        """

        sentence = "World War II or the Second World War, often abbreviated as WWII or WW2, was a global war that lasted from 1939 to 1945."
        self.assertEqual({ 'abbreviated_as': { 'wwii', 'ww2' }, 'was': { 'global war' }, 'lasted_from': { '1939' }, 'lasted_to': { '1945' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'abbreviated_as': { 'wwii', 'ww2' }, 'was': { 'war' }, 'lasted_from': { '1939' }, 'lasted_to': { '1945' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUES_PRP(self):
        """
        Test that a value may have a personal pronoun instead of a determiner.
        """

        sentence = "The eurozone, officially called the euro area, is a monetary union of 19 member states of the European Union (EU) that have adopted the euro as their primary currency and sole legal tender."
        self.assertEqual({ 'called': { 'euro area' }, 'is': { 'monetary union' }, 'is_of': { 'member states', 'european union' }, 'adopted': { 'euro' }, 'adopted_as': { 'primary currency', 'sole legal tender' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'called': { 'area' }, 'is': { 'union' }, 'is_of': { 'member states', 'european union' }, 'adopted': { 'euro' }, 'adopted_as': { 'currency', 'tender' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_VALUES_have_modifiers(self):
        """
        Text that all list of values may have their own modifiers.
        """

        sentence = """The attack on Pearl Harbor was a surprise military strike by the Imperial Japanese Navy Air Service
                      upon the United States against the naval base at Pearl Harbor in Honolulu, Territory of Hawaii,
                      just before 08:00, on Sunday, December 7, 1941."""
        self.assertEqual({ 'was': { 'military strike' }, 'was_by': { 'imperial japanese navy air service' },
                           'was_upon': { 'united states' }, 'was_against': { 'naval base' }, 'was_at': { 'pearl harbor' }, 'was_in': { 'territory', 'honolulu' }, 'was_of': { 'hawaii' },
                           'was_before': { '08:00' }, 'was_on': { 'sunday , december 7 , 1941' } },
                         LinguisticExtractor(head_only=False).extract(sentence).attributes)
        self.assertEqual({ 'was': { 'surprise military strike' }, 'was_by': { 'imperial japanese navy air service' },
                           'was_upon': { 'united states' }, 'was_against': { 'base' }, 'was_at': { 'pearl harbor' }, 'was_in': { 'territory', 'honolulu' }, 'was_of': { 'hawaii' },
                           'was_before': { '08:00' }, 'was_on': { 'sunday , december 7 , 1941' } },
                         LinguisticExtractor(head_only=True).extract(sentence).attributes)

    def test_extract_misc(self):
        """
        Test extracting attributes from real example strings.
        """

    def test_unsupported(self):
        """
        A graveyard of sentences that are not parsed completely and correctly.
        These are unsupported phrases in grammar.
        """

        extractor = LinguisticExtractor()

        """
        To add support, remove gerunds (VBG) from noun phrases.
        However, this would break phrases like *attacking midfielder*.
        """
        sentence = "Sigismondo Benini (18th century) was an Italian painter of the Baroque period, active in Lombardy, painting landscapes or vedute."
        profile = extractor.extract(sentence)
        # self.assertEqual({ 'was': { 'italian painter' }, 'was_of': { 'baroque period' }, 'active_in': { 'lombardy' }, 'painting': { 'landscapes', 'vedute' } }, profile.attributes)

        """
        To add support, allow prepositions (IN) from entities, but which would break  phrases such as *competing in Formula One with McLaren*.
        """
        sentence = "Anne, Princess Royal KG, KT, GCVO, QSO, CD (Anne Elizabeth Alice Louise; born 15 August 1950), is the second child and only daughter of Queen Elizabeth II and Prince Philip, Duke of Edinburgh."
        profile = extractor.extract(sentence, remove_parentheses=True)
        # self.assertEqual({ 'is': { 'second child', 'only daughter' }, 'is_of': { 'queen elizabeth ii', 'prince philip', 'duke of edinburgh' } }, profile.attributes)

        """
        To add support, either remove coordinating conjunctions (CC) and commas from modifiers.
        Or, preferably, separate adjectives into groups (split on coordinating conjunctions and commas) and attach them separately to the head noun.
        However, this would lead to plural nouns (*mid-atlantic regions*, *southeastern regions*).
        """
        sentence = "Virginia, officially the Commonwealth of Virginia, is a state in the Mid-Atlantic and Southeastern regions of the United States, between the Atlantic Coast and the Appalachian Mountains."
        profile = extractor.extract(sentence)
        # self.assertEqual({ 'is': { 'state' }, 'is_in': { 'mid-atlantic regions', 'southeastern regions' }, 'is_of': { 'united states' }, 'is_between': { 'atlantic coast', 'appalachian mountains' } }, profile.attributes)

        sentence = "Donald John Trump is the 45th and current president of the United States of America."
        profile = extractor.extract(sentence)
        # self.assertEqual({ 'is': { '45th and current president' }, 'is_of': { 'united states of america' } }, profile.attributes)

        """
        To add support for ``referred_to``, add support for multiple ``IN`` or ``TO`` in ``VALUES``, but which opens a pandora's box.

        To add support for *Lyon*, as opposed to *simply Lyon*, disallow ``MOD`` from ``ENT``, which would, however, also reject **Indian Ocean**.
        Alternatively, only keep the modifier if it is a proper noun.

        To add support for *Lyon*, as opposed to *Lyon in Auvergne-Rhône-Alpes*, disallow ``IN`` in ``ENT``, but which would then reject *United States of America*.
        """
        sentence = "Olympique Lyonnais (French pronunciation: ​[ɔlɛ̃pik ljɔnɛ]), commonly referred to as simply Lyon (French pronunciation: ​[ljɔ̃]) or OL, is a French professional football club based in Lyon in Auvergne-Rhône-Alpes."
        profile = extractor.extract(sentence)
        # self.assertEqual({ 'referred_to': { 'lyon', 'ol' } 'is': { 'french professional football club' }, 'based_in': { 'lyon', 'auvergne-rhône-alpes' } }, profile.attributes)
