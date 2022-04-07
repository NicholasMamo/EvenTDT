"""
Test the functionality of the Wikipedia postprocessor.
"""

import copy
import os
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nltk.corpus import stopwords

from apd.postprocessors.external.wikipedia_postprocessor import WikipediaPostprocessor

class TestWikipediaPostprocessor(unittest.TestCase):
    """
    Test the implementation and results of the WikipediaPostprocessor.
    """

    def test_trivial_postprocessing(self):
        """
        Test that when no configuration is given, the participants are returned as given.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=False, remove_brackets=False, surname_only=False)
        participants = [ 'Youssouf Koné (footballer, born 1995)', 'Pedro (footballer, born 1987)' ]
        postprocessed = postprocessor.postprocess(participants)
        self.assertEqual(set(participants), set(postprocessed))
        self.assertTrue(all( participant == _postprocessed
                             for participant, _postprocessed in postprocessed.items() ))

    def test_postprocess_returns_dict(self):
        """
        Test that post-processing returns a dictionary.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=False, remove_brackets=True, surname_only=False)
        participants = [ 'Youssouf Koné (footballer, born 1995)', 'Pedro (footballer, born 1987)' ]
        postprocessed = postprocessor.postprocess(participants)
        self.assertEqual(dict, type(postprocessed))

    def test_postprocess_all_participants(self):
        """
        Test that the post-processor returns all participants.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=False, remove_brackets=True, surname_only=False)
        participants = [ 'Eden Hazard', 'Chelsea F.C.', 'Maurizio Sarri' ]
        postprocessed = postprocessor.postprocess(participants)
        self.assertTrue(all( participant in postprocessed for participant in participants ))

    def test_postprocess_no_duplicates(self):
        """
        Test that the post-processor returns no duplicates.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=False, remove_brackets=True, surname_only=False)
        participants = [ 'Eden Hazard', 'Chelsea F.C.', 'Maurizio Sarri', 'Eden Hazard' ]
        postprocessed = postprocessor.postprocess(participants)
        self.assertEqual(len(postprocessed), len(set(participants)))
        self.assertEqual(sorted(set(postprocessed)), sorted(set(participants)))

    def test_postprocess_same_order(self):
        """
        Test that the post-processor returns the participants in teh same order.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=False, remove_brackets=True, surname_only=False)
        participants = [ 'Eden Hazard', 'Chelsea F.C.', 'Maurizio Sarri' ]
        postprocessed = postprocessor.postprocess(participants)
        self.assertEqual(participants, list(postprocessed))

    def test_postprocess_makes_copy(self):
        """
        Test that when post-processing, the original list does not change.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=True, remove_brackets=True, surname_only=True)
        participants = [ 'Youssouf Koné (footballer, born 1995)', 'Pedro (footballer, born 1987)' ]
        original = copy.deepcopy(participants)
        postprocessor.postprocess(participants)
        self.assertEqual(original, participants)

    def test_surname_only_organization(self):
        """
        Test that organizations are retained without any changes.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Apple Inc.' ]
        postprocessed = postprocessor.postprocess(participants)
        self.assertTrue(all( participant == _postprocessed
                             for participant, _postprocessed in postprocessed.items() ))

    def test_surname_only_location(self):
        """
        Test that locations are retained without any changes.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Hell, California' ]
        postprocessed = postprocessor.postprocess(participants)
        self.assertTrue(all( participant == _postprocessed
                             for participant, _postprocessed in postprocessed.items() ))

    def test_surname_only_person(self):
        """
        Test that persons are reduced to surnames.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Memphis Depay' ]
        self.assertEqual({ 'Memphis Depay': 'Depay' }, postprocessor.postprocess(participants))

    def test_surname_only_person_no_name(self):
        """
        Test that persons are reduced to surnames only if they have a first name.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Pedro (footballer, born 1987)' ]
        self.assertEqual({ 'Pedro (footballer, born 1987)': 'Pedro' }, postprocessor.postprocess(participants))

    def test_surname_only_person_word(self):
        """
        Test that persons are reduced to surnames only if the surname is not a word.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Martin Terrier' ]
        self.assertEqual({ 'Martin Terrier': 'Martin Terrier' }, postprocessor.postprocess(participants))

    def test_surname_only_person_with_accent(self):
        """
        Test that persons with accents in their names are reduced to surnames.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Bertrand Traoré' ]
        self.assertEqual({ 'Bertrand Traoré': 'Traore' }, postprocessor.postprocess(participants))

    def test_surname_only_person_with_multiple_components(self):
        """
        Test that persons with multiple components in their names retain all but the first component.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'David De Gea' ]
        self.assertEqual({ 'David De Gea': 'De Gea' }, postprocessor.postprocess(participants))

    def test_surname_only_person_with_brackets(self):
        """
        Test that persons with brackets in their names are reduced to surnames without the brackets.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Ronaldo (Brazilian footballer)', 'Moussa Dembélé (French footballer)' ]
        self.assertEqual({ 'Ronaldo (Brazilian footballer)': 'Ronaldo', 'Moussa Dembélé (French footballer)': 'Dembele' }, postprocessor.postprocess(participants))

    def test_remove_french_accents(self):
        """
        Test that French accents are removed from French participant names.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=True, surname_only=False)
        participants = [ 'Moussa Dembélé' ]
        self.assertEqual({ 'Moussa Dembélé': 'Moussa Dembele' }, postprocessor.postprocess(participants))

    def test_retain_french_accents(self):
        """
        Test that French accents are retained in French participant names when removal is disabled.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=False, surname_only=False)
        participants = [ 'Moussa Dembélé' ]
        self.assertEqual({ 'Moussa Dembélé': 'Moussa Dembélé' }, postprocessor.postprocess(participants))

    def test_remove_germanic_accents(self):
        """
        Test that Germanic accents are removed from Germanic participant names.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=True, surname_only=False)
        participants = [ 'Erling Braut Håland', 'Anel Ahmedhodžić',
                         'Alexander Kačaniklić', 'Robin Söder' ]
        self.assertEqual({ 'Erling Braut Håland': 'Erling Braut Haland', 'Anel Ahmedhodžić': 'Anel Ahmedhodzic',
                           'Alexander Kačaniklić': 'Alexander Kacaniklic', 'Robin Söder': 'Robin Soder' }, postprocessor.postprocess(participants))

    def test_retain_germanic_accents(self):
        """
        Test that Germanic accents are retained in Germanic participant names when removal is disabled.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=False, surname_only=False)
        participants = [ 'Erling Braut Håland', 'Anel Ahmedhodžić',
                         'Alexander Kačaniklić', 'Robin Söder' ]
        self.assertEqual({ 'Erling Braut Håland': 'Erling Braut Håland', 'Anel Ahmedhodžić': 'Anel Ahmedhodžić',
                           'Alexander Kačaniklić': 'Alexander Kačaniklić', 'Robin Söder': 'Robin Söder' }, postprocessor.postprocess(participants))
