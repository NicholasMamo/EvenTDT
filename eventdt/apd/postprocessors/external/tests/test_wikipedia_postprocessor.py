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
        self.assertEqual(set(participants), set(postprocessor.postprocess(participants)))

    def test_postprocess_dict_returns_dict(self):
        """
        Test that post-processing a dictionary returns another dictionary.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=False, remove_brackets=True, surname_only=False)
        participants = { 'Kone': 'Youssouf Koné (footballer, born 1995)', 'Pedro': 'Pedro (footballer, born 1987)' }
        postprocessed = postprocessor.postprocess(participants)
        self.assertEqual(dict, type(postprocessed))

    def test_postprocess_list_returns_list(self):
        """
        Test that post-processing a list returns another list.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=False, remove_brackets=True, surname_only=False)
        participants = [ 'Youssouf Koné (footballer, born 1995)', 'Pedro (footballer, born 1987)' ]
        postprocessed = postprocessor.postprocess(participants)
        self.assertEqual(list, type(postprocessed))

    def test_postprocess_dict_same_as_list(self):
        """
        Test that when post-processing a dictioanry, the output is identical to post-processing a list.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=True, remove_brackets=True, surname_only=True)
        participants = [ 'Youssouf Koné (footballer, born 1995)', 'Pedro (footballer, born 1987)' ]
        postprocessed_list = postprocessor.postprocess(participants)

        participants = { 'Kone': 'Youssouf Koné (footballer, born 1995)', 'Pedro': 'Pedro (footballer, born 1987)' }
        postprocessed_dict = postprocessor.postprocess(participants)

        self.assertEqual(postprocessed_list, list(postprocessed_dict.values()))

    def test_postprocess_dict_changes_values(self):
        """
        Test that when post-processing a dictionary, only the values change.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=True, remove_brackets=True, surname_only=True)
        participants = { 'Kone': 'Youssouf Koné (footballer, born 1995)', 'Pedro': 'Pedro (footballer, born 1987)' }
        postprocessed_dict = postprocessor.postprocess(participants)
        self.assertEqual(postprocessed_dict.keys(), participants.keys())

    def test_postprocess_dict_retains_alignment(self):
        """
        Test that when post-processing a dictionary, the keys are still bound to the same values.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=False, remove_brackets=True, surname_only=True)
        participants = { 'Koné': 'Youssouf Koné (footballer, born 1995)', 'Pedro': 'Pedro (footballer, born 1987)' }
        postprocessed_dict = postprocessor.postprocess(participants)
        self.assertTrue(all( key in value for key, value in postprocessed_dict.items() ))

    def test_postprocess_list_makes_copy(self):
        """
        Test that when post-processing, the original list does not change.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=True, remove_brackets=True, surname_only=True)
        participants = [ 'Youssouf Koné (footballer, born 1995)', 'Pedro (footballer, born 1987)' ]
        original = copy.deepcopy(participants)
        postprocessor.postprocess(participants)
        self.assertEqual(original, participants)

    def test_postprocess_dict_makes_copy(self):
        """
        Test that when post-processing, the original dictionary does not change.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=True, remove_brackets=True, surname_only=True)
        participants = { 'Kone': 'Youssouf Koné (footballer, born 1995)', 'Pedro': 'Pedro (footballer, born 1987)' }
        original = copy.deepcopy(participants)
        postprocessor.postprocess(participants)
        self.assertEqual(original, participants)

    def test_surname_only_organization(self):
        """
        Test that organizations are retained without any changes.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Apple Inc.' ]
        self.assertEqual(set(participants), set(postprocessor.postprocess(participants)))

    def test_surname_only_location(self):
        """
        Test that locations are retained without any changes.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Hell, California' ]
        self.assertEqual(set(participants), set(postprocessor.postprocess(participants)))

    def test_surname_only_person(self):
        """
        Test that persons are reduced to surnames.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Memphis Depay' ]
        self.assertEqual([ 'Depay' ], postprocessor.postprocess(participants))

    def test_surname_only_person_no_name(self):
        """
        Test that persons are reduced to surnames only if they have a first name.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Pedro (footballer, born 1987)' ]
        self.assertEqual([ 'Pedro' ], postprocessor.postprocess(participants))

    def test_surname_only_person_word(self):
        """
        Test that persons are reduced to surnames only if the surname is not a word.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Martin Terrier' ]
        self.assertEqual(participants, postprocessor.postprocess(participants))

    def test_surname_only_person_with_accent(self):
        """
        Test that persons with accents in their names are reduced to surnames.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Bertrand Traoré' ]
        self.assertEqual([ 'Traore' ], postprocessor.postprocess(participants))

    def test_surname_only_person_with_multiple_components(self):
        """
        Test that persons with multiple components in their names retain all but the first component.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'David De Gea' ]
        self.assertEqual([ 'De Gea'], postprocessor.postprocess(participants))

    def test_surname_only_person_with_brackets(self):
        """
        Test that persons with brackets in their names are reduced to surnames without the brackets.
        """

        postprocessor = WikipediaPostprocessor(surname_only=True)
        participants = [ 'Ronaldo (Brazilian footballer)', 'Moussa Dembélé (French footballer)' ]
        self.assertEqual([ 'Ronaldo', 'Dembele' ], postprocessor.postprocess(participants))

    def test_remove_brackets(self):
        """
        Test that participants with brackets lose them when the parameter is set.
        """

        postprocessor = WikipediaPostprocessor(remove_brackets=True)
        participants = [ 'Apple (Company)' ]
        self.assertEqual([ 'Apple' ], postprocessor.postprocess(participants))

    def test_no_remove_brackets(self):
        """
        Test that participants with brackets retain them when the parameter is not set.
        """

        postprocessor = WikipediaPostprocessor(remove_brackets=False)
        participants = [ 'Apple (Company)' ]
        self.assertEqual([ 'Apple (Company)' ], postprocessor.postprocess(participants))

    def test_remove_brackets_no_brackets(self):
        """
        Test that participants without brackets are returned as given.
        """

        postprocessor = WikipediaPostprocessor(remove_brackets=True)
        participants = [ 'Apple Inc.' ]
        self.assertEqual([ 'Apple Inc.' ], postprocessor.postprocess(participants))

    def test_remove_french_accents(self):
        """
        Test that French accents are removed from French participant names.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=True, surname_only=False)
        participants = [ 'Moussa Dembélé' ]
        self.assertEqual([ 'Moussa Dembele' ], postprocessor.postprocess(participants))

    def test_retain_french_accents(self):
        """
        Test that French accents are retained in French participant names when removal is disabled.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=False, surname_only=False)
        participants = [ 'Moussa Dembélé' ]
        self.assertEqual([ 'Moussa Dembélé' ], postprocessor.postprocess(participants))

    def test_remove_germanic_accents(self):
        """
        Test that Germanic accents are removed from Germanic participant names.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=True, surname_only=False)
        participants = [ 'Erling Braut Håland', 'Anel Ahmedhodžić',
                         'Alexander Kačaniklić', 'Robin Söder' ]
        self.assertEqual([ 'Erling Braut Haland', 'Anel Ahmedhodzic',
                            'Alexander Kacaniklic', 'Robin Soder' ], postprocessor.postprocess(participants))

    def test_retain_germanic_accents(self):
        """
        Test that Germanic accents are retained in Germanic participant names when removal is disabled.
        """

        postprocessor = WikipediaPostprocessor(remove_accents=False, surname_only=False)
        participants = [ 'Erling Braut Håland', 'Anel Ahmedhodžić',
                         'Alexander Kačaniklić', 'Robin Söder' ]
        self.assertEqual([ 'Erling Braut Håland', 'Anel Ahmedhodžić',
                            'Alexander Kačaniklić', 'Robin Söder' ], postprocessor.postprocess(participants))
