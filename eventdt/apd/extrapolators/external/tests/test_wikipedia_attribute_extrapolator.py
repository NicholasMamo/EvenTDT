"""
Test the functionality of the Wikipedia attribute extrapolator.
"""

import os
import random
import string
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
        Test that the default pruning value is 0 and accepts all attributes.
        """

        self.assertEqual(0, WikipediaAttributeExtrapolator().prune)

    def test_init_save_prune(self):
        """
        Test that the extrapolator saves the given prune value.
        """

        self.assertEqual(2, WikipediaAttributeExtrapolator(prune=2).prune)

    def test_extract_none(self):
        """
        Test that building a profile from an empty list of participants returns an empty dictionary.
        """

        extrapolator = WikipediaAttributeExtrapolator(prune=0)
        self.assertEqual({ }, extrapolator.extrapolate([ ]))
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
        profiles = extrapolator._build_profiles(list(resolved.values()))
        self.assertEqual(dict, type(profiles))

    def test_build_profiles_title_key(self):
        """
        Test that building a profile returns the page titles as keys.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles(list(resolved.values()))
        self.assertTrue(all( str == type(key) for key in profiles.keys() ))
        self.assertEqual(list(resolved.values()), list(profiles.keys()))

    def test_build_profiles_profile_value(self):
        """
        Test that building a profile returns the profiles as values.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles(list(resolved.values()))
        self.assertTrue(all(Profile == type(value) for value in profiles.values()))

    def test_build_profiles_all_titles(self):
        """
        Test that building a profile returns a profile for each title.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles(list(resolved.values()))
        self.assertTrue(all( title in profiles.keys() for title in resolved.values() ))
        self.assertTrue(all( title in resolved.values() for title in profiles.keys() ))

    def test_build_profiles_nonexistent_page(self):
        """
        Test that building a profile for a page that doesn't exist still returns a profile.
        """

        title = ''.join( random.choice(string.ascii_letters) for i in range(20))

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles([ title ])
        self.assertEqual(title, profiles[title].name)
        self.assertEqual('', profiles[title].text)
        self.assertEqual({ }, profiles[title].attributes)

    def test_build_profiles_first_sentence(self):
        """
        Test that building a profile uses only the text from the first sentence.
        """

        resolved = { 'Alaska': 'Alaska' }

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles(list(resolved.values()))
        self.assertEqual('Alaska', profiles['Alaska'].name)
        self.assertEqual("Alaska ( (listen); Aleut: Alax̂sxax̂; Inupiaq: Alaasikaq; Alutiiq: Alas'kaaq; Yup'ik: Alaskaq; Tlingit: Anáaski) is a state located in the Western United States on the northwest extremity of North America.",
                         profiles['Alaska'].text)
        self.assertEqual({ 'is': { 'state' }, 'located_in': { 'western united states' }, 'located_on': { 'northwest extremity' }, 'located_of': { 'north america' } }, profiles['Alaska'].attributes)

    def test_build_profiles_with_name(self):
        """
        Test that building a profile returns a profile with the title as the profile's name.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles(list(resolved.values()))
        self.assertTrue(all( profile.name == title for title, profile in profiles.items() ))

    def test_build_profiles_with_text(self):
        """
        Test that building a profile returns a profile with the title as the profile's name.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        profiles = extrapolator._build_profiles(list(resolved.values()))
        self.assertTrue(all( profile.text for profile in profiles.values() ))

    def test_prune_none(self):
        """
        Test that pruning no profiles returns another empty dictionary.
        """

        resolved = { 'Nevada': 'Nevada', 'New York': 'New York (state)' }

        extrapolator = WikipediaAttributeExtrapolator()
        self.assertEqual({ }, extrapolator._prune({ }))

    def test_prune_return_dict(self):
        """
        Test that pruning returns a dictionary.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } }) }

        extrapolator = WikipediaAttributeExtrapolator()
        self.assertEqual(dict, type(extrapolator._prune(profiles)))

    def test_prune_title_key(self):
        """
        Test that pruning returns a dictionary whose keys are the titles.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } }) }

        extrapolator = WikipediaAttributeExtrapolator()
        pruned = extrapolator._prune(profiles)
        self.assertTrue(all( str == type(key) for key in pruned.keys() ))

    def test_prune_profile_value(self):
        """
        Test that pruning returns a dictionary whose values are the pruned profiles.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } }) }

        extrapolator = WikipediaAttributeExtrapolator()
        pruned = extrapolator._prune(profiles)
        self.assertTrue(all( Profile == type(value) for value in pruned.values() ))

    def test_prune_copy(self):
        """
        Test that pruning creates a copy of the profiles.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America') }

        extrapolator = WikipediaAttributeExtrapolator()
        pruned = extrapolator._prune(profiles)
        self.assertTrue(all( profiles[name] != pruned[name] for name in pruned ))
        self.assertTrue(all( profiles[name].name == pruned[name].name for name in pruned ))
        self.assertTrue(all( profiles[name].text == pruned[name].text for name in pruned ))

    def test_prune_original_unchanged(self):
        """
        Test that when pruning, the original candidates are not changed.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America'),
                     'Alaska': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                       name='Hawaii', text='Nevada is a state in the Western United States') }

        original = profiles['Nevada'].copy()
        extrapolator = WikipediaAttributeExtrapolator(prune=1)
        pruned = extrapolator._prune(profiles)
        self.assertNotEqual(original.attributes, pruned['Nevada'].attributes)
        self.assertEqual(original.attributes, profiles['Nevada'].attributes)

    def test_prune_all_profiles(self):
        """
        Test that pruning returns all profiles.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America') }

        extrapolator = WikipediaAttributeExtrapolator()
        pruned = extrapolator._prune(profiles)
        self.assertEqual(len(profiles), len(pruned))
        self.assertEqual(profiles.keys(), pruned.keys())

    def test_prune_none(self):
        """
        Test that pruning with no profiles raises no ``ValueError`` if the prune value is zero.
        """

        extrapolator = WikipediaAttributeExtrapolator(prune=0)
        self.assertEqual({ }, extrapolator._prune({ }))

    def test_prune_zero(self):
        """
        Test that pruning with a prune value of zero returns all profiles unchanged.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America'),
                     'Alaska': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                       name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator(prune=0)
        pruned = extrapolator._prune(profiles)
        self.assertTrue(all( set(profiles[name].attributes) == set(pruned[name].attributes)
                             for name in profiles ))

    def test_prune_few_profiles(self):
        """
        Test that pruning with a number of profiles that's smaller than the prune value raises a ``ValueError``.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America') }

        extrapolator = WikipediaAttributeExtrapolator(prune=1)
        self.assertRaises(ValueError, extrapolator._prune, profiles)

    def test_prune_frequency(self):
        """
        Test that pruning, the remaining attributes have a frequency higher than the prune value.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America'),
                     'Alaska': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                       name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator(prune=1)
        pruned = extrapolator._prune(profiles)
        freq = extrapolator._attribute_frequency(pruned)
        self.assertTrue(all( value > extrapolator.prune for value in freq.values() ))

    def test_all_attributes_from_empty(self):
        """
        Test that extracting attributes from an empty dictionary returns no attributes.
        """

        extrapolator = WikipediaAttributeExtrapolator()
        self.assertEqual(set(), extrapolator._all_attributes({ }))

    def test_all_attributes_return_set(self):
        """
        Test that extracting attributes returns a set.
        """

        extrapolator = WikipediaAttributeExtrapolator()
        self.assertEqual(set, type(extrapolator._all_attributes({ })))

    def test_all_attributes_all_from_one(self):
        """
        Test that extracting attributes from one profile returns all attributes in that profile.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America') }

        extrapolator = WikipediaAttributeExtrapolator()
        self.assertEqual(set(profiles['Nevada'].attributes), extrapolator._all_attributes(profiles))

    def test_all_attributes_from_multiple(self):
        """
        Test that extracting attributes from several profiles returns all profiles.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America'),
                     'Alaska': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                       name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        attributes = extrapolator._all_attributes(profiles)
        self.assertTrue(all( any(attribute in profile.attributes for profile in profiles.values())
                             for attribute in attributes ))
        self.assertTrue(all( attribute in attributes for profile in profiles.values() for attribute in profile.attributes ))

    def test_attribute_frequency_from_empty(self):
        """
        Test that calculating the attribute frequency from no profiles returns an empty dictionary.
        """

        extrapolator = WikipediaAttributeExtrapolator()
        self.assertEqual({ }, extrapolator._attribute_frequency({ }))

    def test_attribute_frequency_return_dict(self):
        """
        Test that calculating the attribute frequency returns a dictionary.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America') }

        extrapolator = WikipediaAttributeExtrapolator()
        self.assertEqual(dict, type(extrapolator._attribute_frequency(profiles)))

    def test_attribute_frequency_attribute_key(self):
        """
        Test that calculating the attribute frequency returns the attributes as keys.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America') }

        extrapolator = WikipediaAttributeExtrapolator()
        freq = extrapolator._attribute_frequency(profiles)
        self.assertTrue(all( str == type(key) for key in freq.keys() ))

    def test_attribute_frequency_frequency_value(self):
        """
        Test that calculating the attribute frequency returns integers as values.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America') }

        extrapolator = WikipediaAttributeExtrapolator()
        freq = extrapolator._attribute_frequency(profiles)
        self.assertTrue(all( int == type(value) for value in freq.values() ))

    def test_attribute_frequency_all_attributes(self):
        """
        Test that calculating the attribute frequency returns one value for all attribute.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America') }

        extrapolator = WikipediaAttributeExtrapolator()
        attributes = extrapolator._all_attributes(profiles)
        freq = extrapolator._attribute_frequency(profiles)
        self.assertEqual(attributes, set(freq))

    def test_attribute_frequency_positive(self):
        """
        Test that calculating the attribute frequency returns a positive, non-zero score for all attributes.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America'),
                     'Alaska': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                       name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        freq = extrapolator._attribute_frequency(profiles)
        self.assertTrue(all( _freq > 0 for _freq in freq.values() ))

    def test_attribute_frequency_one_profile(self):
        """
        Test that calculating the attribute frequency from one profile returns a dictionary with all values 1.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America') }

        extrapolator = WikipediaAttributeExtrapolator()
        freq = extrapolator._attribute_frequency(profiles)
        self.assertEqual(set(profiles['Nevada'].attributes), set(freq))
        self.assertTrue(all( _freq == 1 for _freq in freq.values() ))

    def test_attribute_frequency_several_profiles(self):
        """
        Test that calculating the attribute frequency from several profiles returns the correct scores.
        """

        profiles = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_of': { 'united states', 'america' } },
                                       name='Nevada', text='Nevada is a state of the United States of America'),
                     'Alaska': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                       name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        freq = extrapolator._attribute_frequency(profiles)
        self.assertEqual(2, freq['is'])
        self.assertEqual(1, freq['is_of'])
        self.assertEqual(1, freq['is_in'])

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

    def test_trim_candidates_none(self):
        """
        Test that trimming no candidates returns an empty dictionary.
        """

        reference = { 'Hawaii': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                        name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        self.assertEqual({ }, extrapolator._trim({ }, reference))

    def test_trim_reference_none(self):
        """
        Test that when trimming without reference profiles, all candidate profiles are returned but with no attributes.
        """

        candidates = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'west' }, 'is_of': { 'united states', 'america' } },
                                         name='Nevada', text='Nevada is a state in the West of the United States of America') }

        extrapolator = WikipediaAttributeExtrapolator()
        trimmed = extrapolator._trim(candidates, { })
        self.assertEqual(len(candidates), len(trimmed))
        self.assertNotEqual(candidates['Nevada'], trimmed['Nevada'])
        self.assertEqual(candidates['Nevada'].name, trimmed['Nevada'].name)
        self.assertEqual(candidates['Nevada'].text, trimmed['Nevada'].text)

    def test_trim_return_dict(self):
        """
        Test that when trimming, the function returns a dictionary.
        """

        candidates = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'west' }, 'is_of': { 'united states', 'america' } },
                                         name='Nevada', text='Nevada is a state in the West of the United States of America') }
        reference = { 'Hawaii': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                        name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        self.assertEqual(dict, type(extrapolator._trim(candidates, reference)))

    def test_trim_title_keys(self):
        """
        Test that when trimming, the profile titles are the keys.
        """

        candidates = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'west' }, 'is_of': { 'united states', 'america' } },
                                         name='Nevada', text='Nevada is a state in the West of the United States of America') }
        reference = { 'Hawaii': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                        name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        trimmed = extrapolator._trim(candidates, reference)
        self.assertTrue(all( str == type(key) for key in trimmed.keys() ))

    def test_trim_profile_values(self):
        """
        Test that when trimming, the profiles are the values.
        """

        candidates = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'west' }, 'is_of': { 'united states', 'america' } },
                                         name='Nevada', text='Nevada is a state in the West of the United States of America') }
        reference = { 'Hawaii': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                        name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        trimmed = extrapolator._trim(candidates, reference)
        self.assertTrue(all( Profile == type(value) for value in trimmed.values() ))

    def test_trim_copy(self):
        """
        Test that when trimming, the function creates a copy of the original profiles.
        """

        candidates = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'west' }, 'is_of': { 'united states', 'america' } },
                                         name='Nevada', text='Nevada is a state in the West of the United States of America') }
        reference = { 'Hawaii': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                        name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        trimmed = extrapolator._trim(candidates, reference)
        self.assertTrue(all( candidates[name] != trimmed[name] for name in trimmed ))
        self.assertTrue(all( candidates[name].name == trimmed[name].name for name in trimmed ))
        self.assertTrue(all( candidates[name].text == trimmed[name].text for name in trimmed ))

    def test_trim_original_unchanged(self):
        """
        Test that when trimming, the original candidates are not changed.
        """

        candidates = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'west' }, 'is_of': { 'united states', 'america' } },
                                         name='Nevada', text='Nevada is a state in the West of the United States of America') }
        reference = { 'Hawaii': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                        name='Hawaii', text='Nevada is a state in the Western United States') }

        original = candidates['Nevada'].copy()
        extrapolator = WikipediaAttributeExtrapolator()
        trimmed = extrapolator._trim(candidates, reference)
        # TODO: Uncomment after implementing
        # self.assertNotEqual(original.attributes, trimmed['Nevada'].attributes)
        self.assertEqual(original.attributes, candidates['Nevada'].attributes)

    def test_trim_all_candidates(self):
        """
        Test that trimming returns all candidates.
        """

        candidates = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'west' }, 'is_of': { 'united states', 'america' } },
                                         name='Nevada', text='Nevada is a state in the West of the United States of America') }
        reference = { 'Hawaii': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                        name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        trimmed = extrapolator._trim(candidates, reference)
        self.assertEqual(candidates.keys(), trimmed.keys())

    def test_score_and_rank_reference_none(self):
        """
        Test that when scoring candidates from an empty list of reference participants, the function returns an empty dictionary.
        This is because the scores should be zero.
        """

        candidates = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'west' }, 'is_of': { 'united states', 'america' } },
                                         name='Nevada', text='Nevada is a state in the West of the United States of America') }
        reference = { 'Hawaii': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                        name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        scores = extrapolator._score_and_rank(candidates, { })
        self.assertEqual({ }, scores)

    def test_score_and_rank_candidates_none(self):
        """
        Test that when scoring candidates from an empty list of candidates, the function returns an empty dictionary.
        """

        candidates = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'west' }, 'is_of': { 'united states', 'america' } },
                                         name='Nevada', text='Nevada is a state in the West of the United States of America') }
        reference = { 'Hawaii': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                        name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        scores = extrapolator._score_and_rank({ }, reference)
        self.assertEqual({ }, scores)

    def test_score_and_rank_returns_dict(self):
        """
        Test that when scoring candidates, the function returns an empty dictionary.
        """

        candidates = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'west' }, 'is_of': { 'united states', 'america' } },
                                         name='Nevada', text='Nevada is a state in the West of the United States of America') }
        reference = { 'Hawaii': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                        name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        scores = extrapolator._score_and_rank(candidates, reference)
        self.assertEqual(dict, type(scores))

    def test_score_and_rank_title_key(self):
        """
        Test that when scoring candidates, the page titles are the keys.
        """

        candidates = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'west' }, 'is_of': { 'united states', 'america' } },
                                         name='Nevada', text='Nevada is a state in the West of the United States of America') }
        reference = { 'Hawaii': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                        name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        scores = extrapolator._score_and_rank(candidates, reference)
        self.assertTrue(all( str == type(key) for key in scores.keys() ))

    def test_score_and_rank_score_value(self):
        """
        Test that when scoring candidates, the scores are the values.
        """

        candidates = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'west' }, 'is_of': { 'united states', 'america' } },
                                         name='Nevada', text='Nevada is a state in the West of the United States of America') }
        reference = { 'Hawaii': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                        name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        scores = extrapolator._score_and_rank(candidates, reference)
        self.assertTrue(all( float == type(value) for value in scores.values() ))

    def test_score_and_rank_positive_scores(self):
        """
        Test that when scoring candidates, all scores are positive.
        """

        candidates = { 'Nevada': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'west' }, 'is_of': { 'united states', 'america' } },
                                         name='Nevada', text='Nevada is a state in the West of the United States of America') }
        reference = { 'Hawaii': Profile(attributes={ 'is': { 'state' }, 'is_in': { 'western united states' } },
                                        name='Hawaii', text='Nevada is a state in the Western United States') }

        extrapolator = WikipediaAttributeExtrapolator()
        scores = extrapolator._score_and_rank(candidates, reference)
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
