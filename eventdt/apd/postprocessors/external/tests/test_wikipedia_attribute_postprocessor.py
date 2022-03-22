"""
Test the functionality of the :class:`~apd.postprocessors.wikipedia_attribute_postprocessor.WikipediaAttributePostprocessor`.
"""

import os
import random
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from apd.postprocessors.external.wikipedia_attribute_postprocessor import WikipediaAttributePostprocessor
from attributes import Profile
from attributes.extractors import LinguisticExtractor

class TestWikipediaAttributePostprocessor(unittest.TestCase):
    """
    Test the functionality of the :class:`~apd.postprocessors.wikipedia_attribute_postprocessor.WikipediaAttributePostprocessor`.
    """

    def test_init_with_extractor(self):
        """
        Test that the constructor creates an extractor.
        """

        postprocessor = WikipediaAttributePostprocessor()
        self.assertTrue(postprocessor.extractor)
        self.assertEqual(LinguisticExtractor, type(postprocessor.extractor))

    def test_postprocess_none(self):
        """
        Test that postprocessing no participants returns an empty dictionary.
        """

        postprocessor = WikipediaAttributePostprocessor()
        self.assertEqual({ }, postprocessor.postprocess([ ]))

    def test_postprocess_returns_dict(self):
        """
        Test that postprocessing returns a dictionary.
        """

        participants = [ 'Nevada', 'New York (state)' ]

        postprocessor = WikipediaAttributePostprocessor()
        self.assertEqual(dict, type(postprocessor.postprocess(participants)))

    def test_postprocess_participants_keys(self):
        """
        Test that postprocessing returns the participants as the dictionary's keys.
        """

        participants = [ 'Nevada', 'New York (state)' ]

        postprocessor = WikipediaAttributePostprocessor()
        postprocessed = postprocessor.postprocess(participants)
        self.assertTrue(all( str == type(key) for key in postprocessed.keys() ))

    def test_postprocess_profiles_values(self):
        """
        Test that postprocessing returns profiles as the dictionary's values.
        """

        participants = [ 'Nevada', 'New York (state)' ]

        postprocessor = WikipediaAttributePostprocessor()
        postprocessed = postprocessor.postprocess(participants)
        self.assertTrue(all( Profile == type(value) for value in postprocessed.values() ))

    def test_postprocess_all_participants(self):
        """
        Test that postprocessing returns all participants.
        """

        participants = [ 'Nevada', 'Texas', 'Alaska', 'New York (state)' ]

        postprocessor = WikipediaAttributePostprocessor()
        postprocessed = postprocessor.postprocess(participants)
        self.assertEqual(set(participants), set(postprocessed.keys()))

    def test_postprocess_same_order(self):
        """
        Test that postprocessing returns all participants in the original order.
        """

        participants = [ 'Nevada', 'Texas', 'Alaska', 'New York (state)' ]

        postprocessor = WikipediaAttributePostprocessor()
        postprocessed = postprocessor.postprocess(participants)
        self.assertEqual(participants, list(postprocessed.keys()))

    def test_build_profiles_none(self):
        """
        Test that building a profile for no participants returns a dictionary.
        """

        postprocessor = WikipediaAttributePostprocessor()
        profiles = postprocessor._build_profiles([ ])
        self.assertEqual({ }, profiles)

    def test_build_profiles_from_list(self):
        """
        Test that building a profile from a list constructs profiles for each participant.
        """

        participants = [ 'Nevada', 'New York (state)' ]

        postprocessor = WikipediaAttributePostprocessor()
        profiles = postprocessor._build_profiles(participants)
        self.assertEqual(participants, list(profiles.keys()))

    def test_build_profiles_return_dict(self):
        """
        Test that building a profile returns a dictionary.
        """

        participants = [ 'Nevada', 'New York (state)' ]

        postprocessor = WikipediaAttributePostprocessor()
        profiles = postprocessor._build_profiles(participants)
        self.assertEqual(dict, type(profiles))

    def test_build_profiles_title_key(self):
        """
        Test that building a profile returns the page titles as keys.
        """

        participants = [ 'Nevada', 'New York (state)' ]

        postprocessor = WikipediaAttributePostprocessor()
        profiles = postprocessor._build_profiles(participants)
        self.assertTrue(all( str == type(key) for key in profiles.keys() ))
        self.assertEqual(participants, list(profiles.keys()))

    def test_build_profiles_profile_value(self):
        """
        Test that building a profile returns the profiles as values.
        """

        participants = [ 'Nevada', 'New York (state)' ]

        postprocessor = WikipediaAttributePostprocessor()
        profiles = postprocessor._build_profiles(participants)
        self.assertTrue(all(Profile == type(value) for value in profiles.values()))

    def test_build_profiles_all_titles(self):
        """
        Test that building a profile returns a profile for each title.
        """

        participants = [ 'Nevada', 'New York (state)' ]

        postprocessor = WikipediaAttributePostprocessor()
        profiles = postprocessor._build_profiles(participants)
        self.assertTrue(all( title in profiles.keys() for title in participants ))
        self.assertTrue(all( title in participants for title in profiles.keys() ))

    def test_build_profiles_nonexistent_page(self):
        """
        Test that building a profile for a page that doesn't exist still returns a profile.
        """

        title = ''.join( random.choice(string.ascii_letters) for i in range(20))

        postprocessor = WikipediaAttributePostprocessor()
        profiles = postprocessor._build_profiles([ title ])
        self.assertEqual(title, profiles[title].name)
        self.assertEqual('', profiles[title].text)
        self.assertEqual({ }, profiles[title].attributes)

    def test_build_profiles_first_sentence(self):
        """
        Test that building a profile uses only the text from the first sentence.
        """

        participants = [ 'Alaska' ]

        postprocessor = WikipediaAttributePostprocessor()
        profiles = postprocessor._build_profiles(participants)
        self.assertEqual('Alaska', profiles['Alaska'].name)
        self.assertEqual("Alaska ( (listen); Aleut: Alax̂sxax̂; Inupiaq: Alaasikaq; Alutiiq: Alas'kaaq; Yup'ik: Alaskaq; Tlingit: Anáaski) is a state located in the Western United States on the northwest extremity of North America.",
                         profiles['Alaska'].text)
        self.assertEqual({ 'is': { 'state' }, 'located_in': { 'western united states' }, 'located_on': { 'northwest extremity' }, 'located_of': { 'north america' } }, profiles['Alaska'].attributes)

    def test_build_profiles_with_name(self):
        """
        Test that building a profile returns a profile with the title as the profile's name.
        """

        participants = [ 'Nevada', 'New York (state)' ]

        postprocessor = WikipediaAttributePostprocessor()
        profiles = postprocessor._build_profiles(participants)
        self.assertTrue(all( profile.name == title for title, profile in profiles.items() ))

    def test_build_profiles_with_text(self):
        """
        Test that building a profile returns a profile with the title as the profile's name.
        """

        participants = [ 'Nevada', 'New York (state)' ]

        postprocessor = WikipediaAttributePostprocessor()
        profiles = postprocessor._build_profiles(participants)
        self.assertTrue(all( profile.text for profile in profiles.values() ))

    def test_build_profiles_ignores_redirects(self):
        """
        Test that building profiles ignores redirects and returns only the original titles.
        """

        participants = [ 'Education in Alaska' ]

        postprocessor = WikipediaAttributePostprocessor()
        profiles = postprocessor._build_profiles(participants)
        self.assertEqual(set(participants), set(profiles.keys()))
        self.assertFalse('Alaska' in profiles)

    def test_build_profiles_redirects_with_attributes(self):
        """
        Test that building profiles of pages that redirect still returns a profile with attributes from the redirect target.
        """

        postprocessor = WikipediaAttributePostprocessor()

        participants = [ 'Alaska' ]
        target = postprocessor._build_profiles(participants)

        participants = [ 'Education in Alaska' ]
        source = postprocessor._build_profiles(participants)
        self.assertEqual(target['Alaska'].attributes, source['Education in Alaska'].attributes)

    def test_build_profiles_with_parentheses(self):
        """
        Test that building profiles retains text in parentheses.
        """

        postprocessor = WikipediaAttributePostprocessor()

        participants = [ 'Jennet Conant' ]
        profiles = postprocessor._build_profiles(participants)
        self.assertEqual({ 'born': { 'july 15 , 1959' }, 'is': { 'american non-fiction author', 'journalist' } },
                         profiles['Jennet Conant'].attributes)
