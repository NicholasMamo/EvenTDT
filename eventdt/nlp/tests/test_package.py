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

class TestPackage(unittest.TestCase):
    """
    Run unit tests on the :mod:`~nlp` package functions.
    """

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
