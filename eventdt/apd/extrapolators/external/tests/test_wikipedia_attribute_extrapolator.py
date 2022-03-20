"""
Test the functionality of the Wikipedia attribute extrapolator.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from apd.extrapolators.external.wikipedia_attribute_extrapolator import WikipediaAttributeExtrapolator
from attributes import Profile

class TestWikipediaAttributeExtrapolator(unittest.TestCase):
    """
    Test the implementation and results of the Wikipedia attribute extrapolator.
    """

    def test_init_default_prune(self):
        """
        Test that the default pruning value is 1 and accepts all attributes.
        """

        self.assertEqual(1, WikipediaAttributeExtrapolator().prune)

    def test_init_save_prune(self):
        """
        Test that the extrapolator saves the given prune value.
        """

        self.assertEqual(2, WikipediaAttributeExtrapolator(prune=2).prune)

    def test_extract_none(self):
        """
        Test that building a profile from an empty list of participants returns an empty dictionary.
        """

        extrapolator = WikipediaAttributeExtrapolator()
        self.assertEqual({ }, extrapolator.extrapolate([ ]))

        extrapolator = WikipediaAttributeExtrapolator()
        self.assertEqual({ }, extrapolator.extrapolate({ }))

    def test_extrapolate_from_list(self):
        """
        Test that when extrapolating with a list of participants, the extrapolator returns a dictionary.
        """

        # TODO: Make the test more robust and grounded

        extrapolator = WikipediaAttributeExtrapolator()
        extrapolated = extrapolator.extrapolate([ 'Nevada', 'New York (state)' ])
        self.assertEqual(dict, type(extrapolated))

    def test_extrapolate_from_dict(self):
        """
        Test that when extrapolating with a dictionary of participants, the extrapolator uses the values and returns a dictionary.
        """

        # TODO: Make the test more robust and grounded

        extrapolator = WikipediaAttributeExtrapolator()
        extrapolated = extrapolator.extrapolate({ 'Nevada': 'Nevada', 'New York': 'New York (state)' })
        self.assertEqual(dict, type(extrapolated))

    def test_extrapolate_returns_dict(self):
        """
        Test that extrapolating returns a dictionary.
        """

        extrapolator = WikipediaAttributeExtrapolator()
        extrapolated = extrapolator.extrapolate({ 'Nevada': 'Nevada', 'New York': 'New York (state)' })
        self.assertEqual(dict, type(extrapolated))

    def test_extrapolate_title_key(self):
        """
        Test that extrapolating returns the article titles as keys.
        """

        extrapolator = WikipediaAttributeExtrapolator()
        extrapolated = extrapolator.extrapolate({ 'Nevada': 'Nevada', 'New York': 'New York (state)' })
        self.assertTrue(all( str == type(key) for key in extrapolated.keys() ))

    def test_extrapolate_score_value(self):
        """
        Test that extrapolating returns the candidate scores as values.
        """

        extrapolator = WikipediaAttributeExtrapolator()
        extrapolated = extrapolator.extrapolate({ 'Nevada': 'Nevada', 'New York': 'New York (state)' })
        self.assertTrue(all( float == type(value) for value in extrapolated.values() ))

    def test_build_profiles_none(self):
        """
        Test that building a profile for no candidates returns a dictionary.
        """

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles([ ])
        self.assertEqual({ }, profiles)

        profiles = extrapolator._build_profiles({ })
        self.assertEqual({ }, profiles)

    def test_build_profiles_from_list(self):
        """
        Test that building a profile from a list constructs profiles for each element.
        """

        resolved = [ 'Nevada', 'New York (state)' ]

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles(resolved)
        self.assertEqual(resolved, list(profiles.keys()))

    def test_build_profiles_return_dict(self):
        """
        Test that building a profile returns a dictionary.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles(resolved.values())
        self.assertEqual(dict, type(profiles))

    def test_build_profiles_title_key(self):
        """
        Test that building a profile returns the page titles as keys.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles(resolved.values())
        self.assertTrue(all( str == type(key) for key in profiles.keys() ))
        self.assertEqual(list(resolved.values()), list(profiles.keys()))

    def test_build_profiles_profile_value(self):
        """
        Test that building a profile returns the profiles as values.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles(resolved.values())
        self.assertTrue(all(Profile == type(value) for value in profiles.values()))

    def test_build_profiles_all_titles(self):
        """
        Test that building a profile returns a profile for each title.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles(resolved.values())
        self.assertTrue(all( title in profiles.keys() for title in resolved.values() ))
        self.assertTrue(all( title in resolved.values() for title in profiles.keys() ))

    def test_build_profiles_with_name(self):
        """
        Test that building a profile returns a profile with the title as the profile's name.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles(resolved.values())
        self.assertTrue(all( profile.name == title for title, profile in profiles.items() ))

    def test_generate_candidates_none(self):
        """
        Test that when generating candidates from an empty list of participants, the function returns an empty dictionary.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        candidates = extrapolator._generate_candidates(resolved.values())
        self.assertEqual({ }, candidates)

    def test_generate_candidates_returns_dict(self):
        """
        Test that when generating candidates, the function returns an empty dictionary.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        candidates = extrapolator._generate_candidates(resolved.values())
        self.assertEqual(dict, type(candidates))

    def test_generate_candidates_title_key(self):
        """
        Test that when generating candidates, the page titles are the keys.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        candidates = extrapolator._generate_candidates(resolved.values())
        self.assertTrue(all( str == type(key) for key in candidates.keys() ))

    def test_generate_candidates_profile_value(self):
        """
        Test that when generating candidates, the profiles are the values.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        candidates = extrapolator._generate_candidates(resolved.values())
        self.assertTrue(all( Profile == type(value) for value in candidates.values() ))

    def test_score_and_rank_reference_none(self):
        """
        Test that when scoring candidates from an empty list of reference participants, the function returns an empty dictionary.
        This is because the scores should be zero.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }
        candidates = { 'Arizona': 'Arizona', 'Washington': 'Washington (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        scores = extrapolator._score_and_rank({ }, extrapolator._build_profiles(candidates.values()))
        self.assertEqual({ }, scores)

    def test_score_and_rank_candidates_none(self):
        """
        Test that when scoring candidates from an empty list of candidates, the function returns an empty dictionary.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }
        candidates = { 'Arizona': 'Arizona', 'Washington': 'Washington (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        scores = extrapolator._score_and_rank(extrapolator._build_profiles(resolved.values()), { })
        self.assertEqual({ }, scores)

    def test_score_and_rank_returns_dict(self):
        """
        Test that when scoring candidates, the function returns an empty dictionary.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }
        candidates = { 'Arizona': 'Arizona', 'Washington': 'Washington (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        scores = extrapolator._score_and_rank(extrapolator._build_profiles(resolved.values()), extrapolator._build_profiles(candidates.values()))
        self.assertEqual(dict, type(scores))

    def test_score_and_rank_title_key(self):
        """
        Test that when scoring candidates, the page titles are the keys.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }
        candidates = { 'Arizona': 'Arizona', 'Washington': 'Washington (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        scores = extrapolator._score_and_rank(extrapolator._build_profiles(resolved.values()), extrapolator._build_profiles(candidates.values()))
        self.assertTrue(all( str == type(key) for key in scores.keys() ))

    def test_score_and_rank_score_value(self):
        """
        Test that when scoring candidates, the scores are the values.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }
        candidates = { 'Arizona': 'Arizona', 'Washington': 'Washington (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        scores = extrapolator._score_and_rank(extrapolator._build_profiles(resolved.values()), extrapolator._build_profiles(candidates.values()))
        self.assertTrue(all( float == type(value) for value in scores.values() ))

    def test_score_and_rank_positive_scores(self):
        """
        Test that when scoring candidates, all scores are positive.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }
        candidates = { 'Arizona': 'Arizona', 'Washington': 'Washington (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        scores = extrapolator._score_and_rank(extrapolator._build_profiles(resolved.values()), extrapolator._build_profiles(candidates.values()))
        self.assertTrue(all( value > 0 for value in scores.values() ))

    def test_score_and_rank_all_candidates(self):
        """
        Test that when scoring and ranking candidates, all candidates with a positive score are returned.
        """

        # TODO: Implement after scoring

    def test_score_and_rank_all_candidates(self):
        """
        Test that when scoring and ranking candidates, all candidates with a positive score are returned.
        """

        # TODO: Implement after scoring
