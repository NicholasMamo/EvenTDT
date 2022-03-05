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

    def test_remove_parentheses_original(self):
        """
        Test that removing the parentheses reconstructs the sentence with overwriting the original string.
        """

        extractor = LinguisticExtractor()

        sentence = "Pope Francis (Latin: Franciscus; Italian: Francesco; Spanish: Francisco; born Jorge Mario Bergoglio,[b] 17 December 1936) is the head of the Catholic Church and sovereign of the Vatican City State since 2013."
        clean = extractor._remove_parentheses(sentence)
        self.assertEqual("Pope Francis (Latin: Franciscus; Italian: Francesco; Spanish: Francisco; born Jorge Mario Bergoglio,[b] 17 December 1936) is the head of the Catholic Church and sovereign of the Vatican City State since 2013.", sentence)
        profile = extractor.extract(sentence, remove_parentheses=True)
        self.assertEqual("Pope Francis (Latin: Franciscus; Italian: Francesco; Spanish: Francisco; born Jorge Mario Bergoglio,[b] 17 December 1936) is the head of the Catholic Church and sovereign of the Vatican City State since 2013.", sentence)
        self.assertEqual({ 'is': { 'head' }, 'is_of': { 'catholic church', 'sovereign', 'vatican city state' }, 'is_since':{ '2013' } }, profile.attributes)

    def test_remove_parentheses_none(self):
        """
        Test that a text without parentheses is unchanged when removing parentheses.
        """

        extractor = LinguisticExtractor()

        sentence = "Europe is a continent, also recognised as part of Eurasia, located entirely in the Northern Hemisphere and mostly in the Eastern Hemisphere."
        self.assertEqual(sentence, extractor._remove_parentheses(sentence))
        profile = extractor.extract(sentence, remove_parentheses=True)
        self.assertEqual({ 'is': { 'continent' }, 'recognised_as': { 'part' }, 'recognised_of': { 'eurasia' }, 'located_in': { 'northern hemisphere', 'eastern hemisphere' } }, profile.attributes)

    def test_remove_parentheses(self):
        """
        Test that a text with parentheses is cleaned.
        """

        extractor = LinguisticExtractor()

        sentence = "Kylian Mbappé Lottin (born 20 December 1998) is a French professional footballer who plays as a forward for Ligue 1 club Paris Saint-Germain and the France national team."
        self.assertEqual("Kylian Mbappé Lottin is a French professional footballer who plays as a forward for Ligue 1 club Paris Saint-Germain and the France national team.", extractor._remove_parentheses(sentence))
        profile = extractor.extract(sentence, remove_parentheses=True)
        self.assertEqual({ 'is': { 'french professional footballer' }, 'plays_as': { 'forward' }, 'plays_for': { 'paris saint-germain', 'france national team' } }, profile.attributes)

    def test_remove_parentheses_multiple(self):
        """
        Test that when a text includes multiple parentheses, all of them are removed.
        """

        extractor = LinguisticExtractor()

        sentence = "The eurozone, officially called the euro area, is a monetary union of 19 member states of the European Union (EU) that have adopted the euro (€) as their primary currency and sole legal tender."
        self.assertEqual("The eurozone, officially called the euro area, is a monetary union of 19 member states of the European Union that have adopted the euro as their primary currency and sole legal tender.", extractor._remove_parentheses(sentence))
        profile = extractor.extract(sentence, remove_parentheses=True)
        self.assertEqual({ 'called': { 'euro area' }, 'is': { 'monetary union' }, 'is_of': { '19 member states', 'european union' }, 'adopted': { 'euro' }, 'adopted_as': { 'primary currency', 'sole legal tender' } }, profile.attributes)

        sentence = "Kyiv (/ˈkiːjɪv/ KEE-yiv,[10] /kiːv/ KEEV[11]) or Kiev (/ˈkiːɛv/ KEE-ev;[12][13] Ukrainian: Київ, romanized: Kyiv, pronounced [ˈkɪjiu̯] (audio speaker iconlisten)) is the capital and most populous city of Ukraine."
        self.assertEqual("Kyiv or Kiev is the capital and most populous city of Ukraine.", extractor._remove_parentheses(sentence))
        profile = extractor.extract(sentence, remove_parentheses=True)
        self.assertEqual({ 'is': { 'capital', 'most populous city' }, 'is_of': { 'ukraine' } }, profile.attributes)

    def test_remove_parentheses_phonemes(self):
        """
        Test that a text with parentheses containing phonemes are removed.
        """

        extractor = LinguisticExtractor()

        sentence = "Kyiv (/ˈkiːjɪv/ KEE-yiv,[10] /kiːv/ KEEV[11]) or Kiev (/ˈkiːɛv/ KEE-ev;[12][13] Ukrainian: Київ, romanized: Kyiv, pronounced [ˈkɪjiu̯] (audio speaker iconlisten)) is the capital and most populous city of Ukraine."
        self.assertEqual("Kyiv or Kiev is the capital and most populous city of Ukraine.", extractor._remove_parentheses(sentence))
        profile = extractor.extract(sentence, remove_parentheses=True)
        self.assertEqual({ 'is': { 'capital', 'most populous city' }, 'is_of': { 'ukraine' } }, profile.attributes)

    def test_remove_parentheses_keep(self):
        """
        Test that if parentheses are kept, they really aren't deleted.
        """

        extractor = LinguisticExtractor()

        sentence = "Anne, Princess Royal KG, KT, GCVO, QSO, CD (Anne Elizabeth Alice Louise; born 15 August 1950), is the second child and only daughter of Queen Elizabeth II and Prince Philip, Duke of Edinburgh."
        profile = extractor.extract(sentence, remove_parentheses=True)
        self.assertEqual({ 'is': { 'second child', 'only daughter' }, 'is_of': { 'queen elizabeth ii', 'prince philip', 'duke of edinburgh' } }, profile.attributes)

        sentence = "Anne, Princess Royal KG, KT, GCVO, QSO, CD (Anne Elizabeth Alice Louise; born 15 August 1950), is the second child and only daughter of Queen Elizabeth II and Prince Philip, Duke of Edinburgh."
        profile = extractor.extract(sentence, remove_parentheses=False)
        self.assertEqual({ 'born': { '15 august 1950' }, 'is': { 'second child', 'only daughter' }, 'is_of': { 'queen elizabeth ii', 'prince philip', 'duke of edinburgh' } }, profile.attributes)

    def test_remove_parentheses_nested(self):
        """
        Test that if a text has nested parameters, all of them are removed.

        Note that *Eastern* is tagged as a proper noun and is thus separate from the complete phrase, *Eastern and Northern Hemispheres*.
        """

        extractor = LinguisticExtractor()

        sentence = "Asia (/ˈeɪʒə, ˈeɪʃə/ (audio speaker iconlisten)) is Earth's largest and most populous continent, located primarily in the Eastern and Northern Hemispheres."
        self.assertEqual("Asia is Earth's largest and most populous continent, located primarily in the Eastern and Northern Hemispheres.", extractor._remove_parentheses(sentence))
        profile = extractor.extract(sentence, remove_parentheses=True)
        self.assertEqual({ 'is': { 'earth', 'earth \'s largest and most populous continent', 'largest and most populous continent' }, 'located_in': { 'eastern', 'northern hemispheres' } }, profile.attributes)

        sentence = "Lionel Andrés Messi (Spanish pronunciation: [ljoˈnel anˈdɾes ˈmesi] (audio speaker iconlisten); born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for Ligue 1 club Paris Saint-Germain and captains the Argentina national team."
        self.assertEqual("Lionel Andrés Messi, also known as Leo Messi, is an Argentine professional footballer who plays as a forward for Ligue 1 club Paris Saint-Germain and captains the Argentina national team.", extractor._remove_parentheses(sentence))
        profile = extractor.extract(sentence, remove_parentheses=True)
        self.assertEqual({ 'known_as': { 'leo messi' }, 'is': { 'argentine professional footballer' }, 'plays_as': { 'forward' }, 'plays_for': { 'paris saint-germain' }, 'captains': { 'argentina national team' } }, profile.attributes)

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

    def test_extract_with_lemmatization(self):
        """
        Test that when initializing the extractor with the lemmatizer, the attribute names are lemmatized.
        """

        extractor = LinguisticExtractor(lemmatize=False)
        sentence = "François Gérard Georges Nicolas Hollande is a French politician who served as president of France from 2012 to 2017."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'french politician' }, 'served_as': { 'president' }, 'served_of': { 'france' }, 'served_from': { '2012' }, 'served_to': { '2017'} }, profile.attributes)

        extractor = LinguisticExtractor(lemmatize=True)
        sentence = "François Gérard Georges Nicolas Hollande is a French politician who served as president of France from 2012 to 2017."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'be': { 'french politician' }, 'serve_as': { 'president' }, 'serve_of': { 'france' }, 'serve_from': { '2012' }, 'serve_to': { '2017'} }, profile.attributes)

    def test_extract_from_parentheses(self):
        """
        Test that the attributes may be extracted from parentheses (if the POS tagger does not mislabel them).
        """

        extractor = LinguisticExtractor()

        sentence = "Dale Owen Bennett (born 6 January 1990) is an English professional footballer, who played as a defender."
        profile = extractor.extract(sentence, remove_parentheses=False)
        self.assertEqual({ 'born': { '6 january 1990' }, 'is': { 'english professional footballer' }, 'played_as': { 'defender' } }, profile.attributes)

    def test_extract_with_periods(self):
        """
        Test extracting attributes from a sentence that has periods.
        """

        extractor = LinguisticExtractor()

        sentence = "Ampelokipoi Larissa F.C. (Greek: ΑΟ Αμπελοκήπων) is a football club based in Larissa, Thessaly, Greece and currently competes in the Larissa FCA league."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'football club' }, 'based_in': { 'larissa', 'thessaly', 'greece' }, 'competes_in': { 'larissa fca league' } }, profile.attributes)

    def test_extract_DATE_format_1(self):
        """
        Test extracting a date in the format DD MM YYYY.
        """

        extractor = LinguisticExtractor()

        sentence = "Emmanuel Jean-Michel Frédéric Macron is a French politician who has been serving as the president of France since 14 May 2017."
        profile = extractor.extract(sentence, name='Emmanuel Macron')
        self.assertEqual({ 'is': { 'french politician' }, 'serving_as': { 'president' }, 'serving_of': { 'france' }, 'serving_since': { '14 may 2017' } }, profile.attributes)

    def test_extract_DATE_format_2(self):
        """
        Test extracting a date in the format MM DD, YYYY.
        """

        extractor = LinguisticExtractor()

        sentence = "William Henry Gates III (born on October 28, 1955) is an American business magnate, software developer, investor, author, and philanthropist."
        profile = extractor.extract(sentence, remove_parentheses=False)
        self.assertEqual({ 'born_on': { 'october 28 , 1955' }, 'is': { 'american business magnate', 'software developer', 'investor', 'author', 'philanthropist' } }, profile.attributes)

    def test_extract_DATE_format_3(self):
        """
        Test extracting a date in the format dd, DD MM YYYY.
        """

        extractor = LinguisticExtractor()

        sentence = "The Normandy landings were the landing operations and associated airborne operations on Tuesday, 6 June 1944 of the Allied invasion of Normandy in Operation Overlord during World War II."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'were': { 'landing operations', 'associated airborne operations' }, 'were_on': { 'tuesday , 6 june 1944' }, 'were_of': { 'allied invasion', 'normandy in operation overlord during world war ii' } }, profile.attributes)

    def test_extract_DATE_TIME(self):
        """
        Text extracting a date that has a time acts like a number.
        """

        extractor = LinguisticExtractor()

        sentence = """The attack on Pearl Harbor was a surprise military strike by the Imperial Japanese Navy Air Service
                      upon the United States against the naval base at Pearl Harbor in Honolulu, Territory of Hawaii,
                      just before 08:00, on Sunday, December 7, 1941."""
        profile = extractor.extract(sentence)
        self.assertEqual({ 'was': { 'surprise military strike' }, 'was_by': { 'imperial japanese navy air service' },
                           'was_upon': { 'united states' }, 'was_against': { 'naval base' }, 'was_at': { 'pearl harbor in honolulu', 'territory of hawaii' },
                           'was_before': { '08:00' }, 'was_on': { 'sunday , december 7 , 1941' } }, profile.attributes)

    def test_extract_MOD_starts_with_number(self):
        """
        Test that a modifier may start with a number.
        """

        extractor = LinguisticExtractor()

        sentence = "The eurozone, officially called the euro area, is a monetary union of 19 member states of the European Union (EU) that have adopted the euro as their primary currency and sole legal tender."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'called': { 'euro area' }, 'is': { 'monetary union' }, 'is_of': { '19 member states', 'european union' }, 'adopted': { 'euro' }, 'adopted_as': { 'primary currency', 'sole legal tender' } }, profile.attributes)

    def test_extract_ENT_ends_number(self):
        """
        Test extracting an attribute value when it is an entity that ends with a number.
        """

        extractor = LinguisticExtractor()

        sentence = "Mark-Alexander Uth is a German footballer who plays as a striker for Bundesliga club Schalke 04."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'german footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'schalke 04' } }, profile.attributes)

    def test_extract_ENT_starts_number(self):
        """
        Test extracting an attribute value when it is an entity that starts with a number.
        """

        extractor = LinguisticExtractor()

        sentence = "Fabian Greilinger is a German professional footballer who plays as a winger for 1860 Munich."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'german professional footballer' }, 'plays_as': { 'winger' }, 'plays_for': { '1860 munich' } }, profile.attributes)

    def test_extract_ENT_has_number(self):
        """
        Test extracting an attribute value when it is an entity that has a number in the middle.
        """

        extractor = LinguisticExtractor()

        sentence = "Dennis Erdmann is a German professional footballer who plays as a defensive midfielder or attacking midfielder for TSV 1860 Munich."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'german professional footballer' }, 'plays_as': { 'defensive midfielder', 'attacking midfielder' }, 'plays_for': { 'tsv 1860 munich' } }, profile.attributes)

    def test_extract_ENT_with_IN(self):
        """
        Test extracting an entity with a preposition in it.
        """

        extractor = LinguisticExtractor()

        sentence = "Donald John Trump is the 45th and current president of the United States of America."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { '45th and current president' }, 'is_of': { 'united states of america' } }, profile.attributes)

        sentence = "Donald John Trump is the 45th, latest and current president of the United States of America."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { '45th , latest and current president' }, 'is_of': { 'united states of america' } }, profile.attributes)

        sentence = "Sallie Kim is currently a U.S. Magistrate Judge of the United States District Court for the Northern District of California."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'u.s. magistrate judge' }, 'is_of': { 'united states district court' }, 'is_for': { 'northern district of california' } }, profile.attributes)

        sentence = "The 2004 Kansas Jayhawks football team represented the University of Kansas in the 2004 NCAA Division I-A football season."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'represented': { 'university of kansas' }, 'represented_in': { '2004 ncaa division i-a football season' } }, profile.attributes)

        sentence = "Giuseppe Tartini was an Italian Baroque composer and violinist born in the Republic of Venice."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'was': { 'italian baroque composer', 'violinist' }, 'born_in': { 'republic of venice' } }, profile.attributes)

    def test_extract_ENT_with_MOD(self):
        """
        Test that an entity may be preceded by a modifier.
        """

        extractor = LinguisticExtractor()

        sentence = "France, officially the French Republic, is a transcontinental country spanning Western Europe and overseas regions and territories in the Americas and the Atlantic, Pacific and Indian Oceans."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'transcontinental country' }, 'spanning': { 'western europe', 'overseas regions', 'territories' }, 'spanning_in': { 'americas', 'atlantic', 'pacific', 'indian oceans' } }, profile.attributes)

    def test_extract_NAME_VBG(self):
        """
        Test that an attribute name may be a gerund.
        """

        extractor = LinguisticExtractor()

        sentence = "Emmanuel Jean-Michel Frédéric Macron is a French politician who has been serving as the president of France since 14 May 2017."
        profile = extractor.extract(sentence, name='Emmanuel Macron')
        self.assertEqual({ 'is': { 'french politician' }, 'serving_as': { 'president' }, 'serving_of': { 'france' }, 'serving_since': { '14 may 2017' } }, profile.attributes)

    def test_extract_NAME_VBD(self):
        """
        Test that an attribute name may be in the past.
        """

        extractor = LinguisticExtractor()

        sentence = "Dale Owen Bennett (born 6 January 1990) is an English professional footballer, who played as a defender."
        profile = extractor.extract(sentence, remove_parentheses=False)
        self.assertEqual({ 'born': { '6 january 1990' }, 'is': { 'english professional footballer' }, 'played_as': { 'defender' } }, profile.attributes)

    def test_extract_VALUE_DATE(self):
        """
        Test that a date is a valid attribute value.
        """

        extractor = LinguisticExtractor()

        sentence = "William Henry Gates III (born on October 28, 1955) is an American business magnate, software developer, investor, author, and philanthropist."
        profile = extractor.extract(sentence, remove_parentheses=False)
        self.assertEqual({ 'born_on': { 'october 28 , 1955' }, 'is': { 'american business magnate', 'software developer', 'investor', 'author', 'philanthropist' } }, profile.attributes)

        sentence = "Nicolas Paul Stéphane Sarközy de Nagy-Bocsa is a French politician who served as President of France from 16 May 2007 until 15 May 2012."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'french politician' }, 'served_as': { 'president of france' }, 'served_from': { '16 may 2007' }, 'served_until': { '15 may 2012' } }, profile.attributes)

    def test_extract_VALUE_CD(self):
        """
        Test that a number is a valid attribute value.
        """

        extractor = LinguisticExtractor()

        sentence = "François Gérard Georges Nicolas Hollande is a French politician who served as president of France from 2012 to 2017."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'french politician' }, 'served_as': { 'president' }, 'served_of': { 'france' }, 'served_from': { '2012' }, 'served_to': { '2017'} }, profile.attributes)

    def test_extract_VALUE_ENT_NP_head(self):
        """
        Test that when extracting values, if an entity is preceded by noun phrases, only the entity is retained.
        """

        extractor = LinguisticExtractor()

        sentence = "Lucas Tolentino Coelho de Lima known as Lucas Paquetá, is a Brazilian professional footballer who plays as an attacking midfielder for Ligue 1 club Lyon and the Brazil national team."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'known_as': { 'lucas paquetá' }, 'is': { 'brazilian professional footballer' }, 'plays_as': { 'attacking midfielder' }, 'plays_for': { 'lyon', 'brazil national team' } }, profile.attributes)

        sentence = "Spalacopsis stolata is a species of beetle in the family Cerambycidae."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'species' }, 'is_of': { 'beetle' }, 'is_in': { 'cerambycidae' } }, profile.attributes)

        # incorrect tagging of 'band/VBP'
        sentence = '"I Want Out" is a song by English rockabilly band Matchbox featuring Kirsty MacColl.'
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'song' }, 'is_by': { 'english' }, 'band': { 'matchbox' }, 'featuring': { 'kirsty maccoll' } }, profile.attributes)

        sentence = "Memphis Depay, also known simply as Memphis, is a Dutch professional footballer and rapper who plays as a forward for French football club Lyon and the Netherlands national team."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'known_as': { 'memphis' }, 'is': { 'dutch professional footballer', 'rapper' }, 'plays_as': { 'forward' }, 'plays_for': { 'lyon', 'netherlands national team' } }, profile.attributes)

        sentence = "Tinotenda \"Tino\" Kadewere is a Zimbabwean professional footballer who plays for Ligue 1 side Lyon and the Zimbabwe national team as a striker."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'zimbabwean professional footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'lyon', 'zimbabwe national team' } }, profile.attributes)

        sentence = "Thiago Henrique Mendes Ribeiro is a Brazilian professional footballer who plays as a central midfielder for French club Lyon."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'brazilian professional footballer' }, 'plays_as': { 'central midfielder' }, 'plays_for': { 'lyon' } }, profile.attributes)

        sentence = "Jason Grégory Marianne Denayer is a Belgian professional footballer who plays as a centre-back for French club Lyon and the Belgium national side."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'belgian professional footballer' }, 'plays_as': { 'centre-back' }, 'plays_for': { 'lyon', 'belgium national side' } }, profile.attributes)

        sentence = "Mathis Rayan Cherki (French pronunciation: ​[ʁajan ʃɛʁki]; Arabic: رايان شرقي; born 17 August 2003) is a French professional footballer who plays as attacking midfielder for Ligue 1 club Lyon."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'french professional footballer' }, 'plays_as': { 'attacking midfielder' }, 'plays_for': { 'lyon' } }, profile.attributes)

        sentence = "Romelu Menama Lukaku Bolingoli is a Belgian professional footballer who plays as a striker for Serie A club Inter Milan and the Belgium national team."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'belgian professional footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'inter milan', 'belgium national team' } }, profile.attributes)

        sentence = "Lautaro Javier Martínez is an Argentine professional footballer who plays as a striker for Italian club Inter Milan and the Argentina national team."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'argentine professional footballer' }, 'plays_as': { 'striker' }, 'plays_for': { 'inter milan', 'argentina national team' } }, profile.attributes)

    def test_extract_VALUE_JJ_NP(self):
        """
        Test that when extracting values, if a value has an adjective, both the adjective and the noun phrase are retained.
        """

        extractor = LinguisticExtractor()

        sentence = "Granada Club de Fútbol, S.A.D., known simply as Granada, is a Spanish football club in the city of Granada, in the autonomous community of Andalusia that plays in La Liga."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'known_as': { 'granada' }, 'is': { 'spanish football club' }, 'is_in': { 'city', 'autonomous community' }, 'is_of': { 'granada', 'andalusia' }, 'plays_in': { 'la liga' } }, profile.attributes)

        sentence = "Naked Harbour (Finnish: Vuosaari) is a 2012 Finnish drama film directed by Aku Louhimies."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { '2012 finnish drama film' }, 'directed_by': { 'aku louhimies' } }, profile.attributes)

    def test_extract_VALUE_NP(self):
        """
        Test extracting values that are noun phrases.
        """

        extractor = LinguisticExtractor()

        sentence = """VR Kanojo (VR カノジョ) is a virtual reality social simulation game made by Illusion, released in February 2017
                      for the HTC Vive and Oculus Rift on Microsoft Windows PCs."""
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'virtual reality social simulation game' }, 'made_by': { 'illusion' }, 'released_in': { 'february 2017' },
                           'released_for': { 'htc vive', 'oculus rift on microsoft windows pcs' } }, profile.attributes)

    def test_extract_VALUE_POS(self):
        """
        Test that if a value has a possessive, the object and subject are returned together and separately.
        """

        extractor = LinguisticExtractor()

        sentence = "Asia (/ˈeɪʒə, ˈeɪʃə/ (audio speaker iconlisten)) is Earth's largest and most populous continent, located primarily in the Eastern and Northern Hemispheres."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'earth', 'earth \'s largest and most populous continent', 'largest and most populous continent' }, 'located_in': { 'eastern', 'northern hemispheres' } }, profile.attributes)

        # general tagged as JJ by the POS tagger
        sentence = "Paul Charles François Adrien Henri Dieudonné Thiébault (14 December 1769, Berlin - 14 October 1846, Paris) was a general who fought in Napoleon I's army."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'fought_in': { 'napoleon i', 'army', 'napoleon i \'s army' } }, profile.attributes)

    def test_extract_ENT_with_PRP(self):
        """
        Test that I is considered to be as part of the entity when it follows one.
        """

        extractor = LinguisticExtractor()

        sentence = "World War I, often abbreviated as WW I or WW1, also known as the First World War or the Great War, was an international conflict that began on 28 July 1914 and ended on 11 November 1918."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'abbreviated_as': { 'ww i', 'ww1' }, 'known_as': { 'first world war', 'great war' }, 'was': { 'international conflict' }, 'began_on': { '28 july 1914' }, 'ended_on': { '11 november 1918' } }, profile.attributes)

        sentence = "Paul Charles François Adrien Henri Dieudonné Thiébault (14 December 1769, Berlin - 14 October 1846, Paris) was a general who fought in Napoleon I's army."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'fought_in': { 'napoleon i', 'army', 'napoleon i \'s army' } }, profile.attributes)

    def test_extract_VALUES_CC_and(self):
        """
        Test extracting attributes which have _and_ conjunctions.
        """

        extractor = LinguisticExtractor()

        sentence = "Elon Reeve Musk FRS is an entrepreneur and business magnate."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'entrepreneur', 'business magnate' } }, profile.attributes)

        sentence = "Memphis Depay plays as a forward and midfielder."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'plays_as': { 'forward', 'midfielder' } }, profile.attributes)

        sentence = "Joseph Robinette Biden Jr. is an American politician and the president-elect of the United States."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'american politician', 'president-elect' }, 'is_of': { 'united states' } }, profile.attributes)

    def test_extract_VALUES_CC_or(self):
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

    def test_extract_VALUES_multiple_CC(self):
        """
        Test extracting attributes which have multiple conjunctions.
        """

        extractor = LinguisticExtractor()

        sentence = "Jeffrey Preston Bezos is an American entrepreneur, media proprietor, investor and computer engineer and commercial astronaut."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'american entrepreneur', 'media proprietor', 'investor', 'computer engineer', 'commercial astronaut' } }, profile.attributes)

        sentence = "Taipei, officially Taipei City, is the capital and a special municipality of Taiwan."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'capital', 'special municipality' }, 'is_of': { 'taiwan' } }, profile.attributes)

        sentence = "France, officially the French Republic, is a transcontinental country spanning Western Europe and overseas regions and territories in the Americas and the Atlantic, Pacific and Indian Oceans."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'transcontinental country' }, 'spanning': { 'western europe', 'overseas regions', 'territories' }, 'spanning_in': { 'americas', 'atlantic', 'pacific', 'indian oceans' } }, profile.attributes)

    def test_extract_VALUES_multiple_CC_with_oxford_comma(self):
        """
        Test extracting attributes which have multiple conjunctions.
        """

        extractor = LinguisticExtractor()

        sentence = "William Henry Gates III (born October 28, 1955) is an American business magnate, software developer, investor, author, and philanthropist."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'american business magnate', 'software developer', 'investor', 'author', 'philanthropist' } }, profile.attributes)

    def test_extract_VALUES_CC(self):
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

    def test_extract_VALUES_commas(self):
        """
        Test extracting attributes which have commas.
        """

        extractor = LinguisticExtractor()

        sentence = """Donetsk, formerly known as Aleksandrovka, Yuzivka (or Hughesovka), Stalin and Stalino,
                      is an industrial city in eastern Ukraine located on the Kalmius River in the disputed area of Donetsk Oblast."""
        profile = extractor.extract(sentence)
        self.assertEqual({ 'known_as': { 'aleksandrovka', 'yuzivka', 'stalin', 'stalino' }, 'is': { 'industrial city' },
                           'is_in': { 'eastern ukraine' }, 'located_on': { 'kalmius river' }, 'located_in': { 'disputed area' }, 'located_of': { 'donetsk oblast' } }, profile.attributes)

        sentence = """EMEA is a shorthand designation meaning Europe, the Middle East and Africa"""
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'shorthand designation' }, 'meaning': { 'europe', 'middle east', 'africa' } }, profile.attributes)

        sentence = "Alexandra Talomaa (born 1975) is a Swedish songwriter who has written songs for A-Teens, Anders Fernette (previously Johansson), Backstreet Boys, Darin, Westlife and others."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'swedish songwriter' }, 'written': { 'songs' }, 'written_for': { 'a-teens', 'anders fernette', 'backstreet boys', 'darin', 'westlife', 'others' } }, profile.attributes)

    def test_extract_VALUES_IN_between(self):
        """
        Test that when extracting a list of values with 'between' as the preposition, two values are extracted.
        """

        extractor = LinguisticExtractor()
        sentence = "Virginia, officially the Commonwealth of Virginia, is a state in the Mid-Atlantic and Southeastern regions of the United States, between the Atlantic Coast and the Appalachian Mountains."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'state' }, 'is_in': { 'mid-atlantic and southeastern regions' }, 'is_of': { 'united states' }, 'is_between': { 'atlantic coast', 'appalachian mountains' } }, profile.attributes)

        sentence = "Wright Inlet is an ice-filled inlet receding westward between Cape Little and Cape Wheeler along the east coast of Palmer Land."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'ice-filled inlet receding westward' }, 'is_between': { 'cape little', 'cape wheeler' }, 'is_along': { 'east coast' }, 'is_of': { 'palmer land' } }, profile.attributes)

    def test_extract_VALUES_IN_appended_to_name(self):
        """
        Test that when extracting attributes with prepositions, the preposition is appended to the name.
        """

        extractor = LinguisticExtractor()

        sentence = "Memphis Depay plays as a forward, winger and midfielder."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'plays_as': { 'forward', 'winger', 'midfielder' } }, profile.attributes)

    def test_extract_VALUES_IN_separate(self):
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

    def test_extract_VALUES_split(self):
        """
        Test that when multiple attributes with the same name but split over different phrases, both are added to the same.
        """

        extractor = LinguisticExtractor()

        sentence = "Lawrence Joseph Ellison is an American businessman and investor who is the co-founder, executive chairman, chief technology officer and former chief executive officer of Oracle Corporation."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'is': { 'american businessman', 'investor', 'co-founder', 'executive chairman', 'chief technology officer', 'former chief executive officer' }, 'is_of': { 'oracle corporation' } }, profile.attributes)

    def test_extract_VALUES_TO(self):
        """
        Test that an attribute value may have *to* as a preposition.
        """

        extractor = LinguisticExtractor()

        sentence = "World War II or the Second World War, often abbreviated as WWII or WW2, was a global war that lasted from 1939 to 1945."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'abbreviated_as': { 'wwii', 'ww2' }, 'was': { 'global war' }, 'lasted_from': { '1939' }, 'lasted_to': { '1945' } }, profile.attributes)

    def test_extract_VALUES_PRP(self):
        """
        Test that a value may have a personal pronoun instead of a determiner.
        """

        extractor = LinguisticExtractor()

        sentence = "The eurozone, officially called the euro area, is a monetary union of 19 member states of the European Union (EU) that have adopted the euro as their primary currency and sole legal tender."
        profile = extractor.extract(sentence)
        self.assertEqual({ 'called': { 'euro area' }, 'is': { 'monetary union' }, 'is_of': { '19 member states', 'european union' }, 'adopted': { 'euro' }, 'adopted_as': { 'primary currency', 'sole legal tender' } }, profile.attributes)

    def test_extract_VALUES_have_modifiers(self):
        """
        Text that all list of values may have their own modifiers.
        """

        extractor = LinguisticExtractor()

        sentence = """The attack on Pearl Harbor was a surprise military strike by the Imperial Japanese Navy Air Service
                      upon the United States against the naval base at Pearl Harbor in Honolulu, Territory of Hawaii,
                      just before 08:00, on Sunday, December 7, 1941."""
        profile = extractor.extract(sentence)
        self.assertEqual({ 'was': { 'surprise military strike' }, 'was_by': { 'imperial japanese navy air service' },
                           'was_upon': { 'united states' }, 'was_against': { 'naval base' }, 'was_at': { 'pearl harbor in honolulu', 'territory of hawaii' },
                           'was_before': { '08:00' }, 'was_on': { 'sunday , december 7 , 1941' } }, profile.attributes)

    def test_extract_misc(self):
        """
        Test extracting attributes from real example strings.
        """

        extractor = LinguisticExtractor()

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
        To add support, disallow prepositions (IN) from entities, which would then break phrases such as *United States of America*.
        """
        sentence = "Lando Norris is a Belgian-British racing driver currently competing in Formula One with McLaren, racing under the British flag."
        profile = extractor.extract(sentence)
        # self.assertEqual({ 'is': { 'belgian-british racing driver' }, 'competing_in': { 'formula one' }, 'competing_with': { 'mclaren' }, 'racing_under': { 'british flag' } }, profile.attributes)

        """
        To add support, either remove coordinating conjunctions (CC) and commas from modifiers.
        Or, preferably, separate adjectives into groups (split on coordinating conjunctions and commas) and attach them separately to the head noun.
        However, this would lead to plural nouns (*mid-atlantic regions*, *southeastern regions*).
        """
        sentence = "Virginia, officially the Commonwealth of Virginia, is a state in the Mid-Atlantic and Southeastern regions of the United States, between the Atlantic Coast and the Appalachian Mountains."
        profile = extractor.extract(sentence)
        # self.assertEqual({ 'is': { 'state' }, 'is_in': { 'mid-atlantic regions', 'southeastern regions' }, 'is_of': { 'united states' }, 'is_between': { 'atlantic coast', 'appalachian mountains' } }, profile.attributes)
