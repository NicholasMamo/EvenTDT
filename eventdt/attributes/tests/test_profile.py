"""
Run unit tests on the :class:`~attributes.profile.Profile` class.
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '..', '..')
if path not in sys.path:
    sys.path.append(path)

from attributes.profile import Profile
from attributes.extractors import LinguisticExtractor

class TestProfile(unittest.TestCase):
    """
    Test the :class:`~attributes.profile.Profile` class.
    """

    def test_init_attributes_empty(self):
        """
        Test that the attributes are initially empty.
        """

        profile = Profile()
        self.assertEqual({ }, profile.attributes)

    def test_init_attributes_none(self):
        """
        Test that the attributes are initially set to an empty dictionary when ``None`` is given.
        """

        profile = Profile(attributes=None)
        self.assertEqual({ }, profile.attributes)

    def test_init_default_attributes(self):
        """
        Test that when providing default attributes, they are stored.
        """

        profile = Profile(attributes={ 'known_as': 'Memphis', 'age': 26 })
        self.assertEqual({ 'known_as': 'Memphis', 'age': 26 }, profile.attributes)

    def test_init_default_name_empty(self):
        """
        Test that by default, the name is empty.
        """

        profile = Profile()
        self.assertEqual(str, type(profile.name))
        self.assertEqual('', profile.name)

    def test_init_name(self):
        """
        Test that when initializing a profile with a name, it is saved.
        """

        profile = Profile('profile name')
        self.assertEqual('profile name', profile.name)

    def test_init_default_text_empty(self):
        """
        Test that by default, the text is empty.
        """

        profile = Profile()
        self.assertEqual(str, type(profile.text))
        self.assertEqual('', profile.text)

    def test_init_text(self):
        """
        Test that when initializing a profile with a text, it is saved.
        """

        profile = Profile(text='profile text')
        self.assertEqual('profile text', profile.text)

    def test_attributes_overwrite(self):
        """
        Test that setting the attributes overwrites the previous attributes.
        """

        profile = Profile(attributes={ 'known_as': 'Memphis', 'age': 26 })
        self.assertEqual({ 'known_as': 'Memphis', 'age': 26 }, profile.attributes)

        profile.attributes = { 'name': 'Memphis Depay' }
        self.assertEqual({ 'name': 'Memphis Depay' }, profile.attributes)

    def test_attributes_overwrite_none(self):
        """
        Test that overwriting the attributes with ``None`` creates an empty dictionary of attributes.
        """

        profile = Profile(attributes={ 'known_as': 'Memphis', 'age': 26 })
        self.assertEqual({ 'known_as': 'Memphis', 'age': 26 }, profile.attributes)

        profile.attributes = None
        self.assertEqual({ }, profile.attributes)

    def test_attributes_add(self):
        """
        Test adding a new attribute to a profile.
        """

        profile = Profile()
        self.assertEqual({ }, profile.attributes)

        profile.attributes['name'] = 'Memphis Depay'
        self.assertEqual({ 'name': 'Memphis Depay' }, profile.attributes)

    def test_attributes_update(self):
        """
        Test update an existing attribute in a profile.
        """

        profile = Profile(attributes={ 'known_as': 'Memphis Depay', 'age': 26 })
        self.assertEqual({ 'known_as': 'Memphis Depay', 'age': 26 }, profile.attributes)

        profile.attributes['known_as'] = 'Memphis'
        self.assertEqual({ 'known_as': 'Memphis', 'age': 26 }, profile.attributes)

    def test_attributes_remove(self):
        """
        Test removing an existing attribute from a profile.
        """

        profile = Profile(attributes={ 'known_as': 'Memphis Depay', 'age': 26 })
        self.assertEqual({ 'known_as': 'Memphis Depay', 'age': 26 }, profile.attributes)

        del profile.attributes['age']
        self.assertEqual({ 'known_as': 'Memphis Depay' }, profile.attributes)

    def test_common_empty(self):
        """
        Test that getting the common attributes in two empty profiles returns an empty set.
        """

        p1, p2 = Profile(), Profile()
        self.assertEqual(set(), p1.common(p2))

    def test_common_one_empty(self):
        """
        Test that getting the common attributes and one profile is empty, the function returns an empty set.
        """

        p1, p2 = Profile(), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertEqual(set(), p1.common(p2))
        self.assertEqual(set(), p2.common(p1))

    def test_common_none(self):
        """
        Test that when two profiles share no attributes, no common attributes are returned.
        """

        p1, p2 = Profile(attributes={ 'plays_for': { 'lyon' } }), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertEqual(set(), p1.common(p2))
        self.assertEqual(set(), p2.common(p1))

    def test_common_in_both(self):
        """
        Test that the common attributes actually exist in both profiles.
        """

        p1, p2 = Profile(attributes={ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertTrue(all( attribute in p1.attributes and attribute in p2.attributes for attribute in p1.common(p2) ))
        self.assertTrue(all( attribute in p1.attributes and attribute in p2.attributes for attribute in p2.common(p1) ))

    def test_common_ignores_values(self):
        """
        Test that the common attributes ignores the value of attributes.
        """

        p1, p2 = Profile(attributes={ 'plays_for': { 'lyon' }, 'plays_as': { 'midfielder' } }), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertFalse(p1.attributes['plays_as'] == p2.attributes['plays_as'])
        self.assertEqual({ 'plays_as' }, p1.common(p2))
        self.assertEqual({ 'plays_as' }, p2.common(p1))

    def test_common_excludes_uncommon(self):
        """
        Test that the attributes that appear in only one profile are excluded.
        """

        p1, p2 = Profile(attributes={ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertFalse('plays_for' in p1.common(p2))
        self.assertFalse('plays_for' in p2.common(p1))

    def test_common_set(self):
        """
        Test that getting the common attributes in two profiles returns an set.
        """

        p1, p2 = Profile(attributes={ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertEqual(set, type(p1.common(p2)))
        self.assertEqual(set, type(p2.common(p1)))

    def test_common_symmetric(self):
        """
        Test that when getting the common attributes in two profiles, the order does not matter.
        """

        p1, p2 = Profile(attributes={ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertEqual(p1.common(p2), p2.common(p1))

    def test_matching_empty(self):
        """
        Test that getting the matching attributes in two empty profiles returns an empty set.
        """

        p1, p2 = Profile(), Profile()
        self.assertEqual(set(), p1.matching(p2))

    def test_matching_one_empty(self):
        """
        Test that getting the matching attributes and one profile is empty, the function returns an empty set.
        """

        p1, p2 = Profile(), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertEqual(set(), p1.matching(p2))
        self.assertEqual(set(), p2.matching(p1))

    def test_matching_none(self):
        """
        Test that when two profiles share no attributes, no matching attributes are returned.
        """

        p1, p2 = Profile(attributes={ 'plays_for': { 'lyon' } }), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertEqual(set(), p1.matching(p2))
        self.assertEqual(set(), p2.matching(p1))

    def test_matching_in_both(self):
        """
        Test that the matching attributes actually exist in both profiles.
        """

        p1, p2 = Profile(attributes={ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertTrue(all( attribute in p1.attributes and attribute in p2.attributes for attribute in p1.matching(p2) ))
        self.assertTrue(all( attribute in p1.attributes and attribute in p2.attributes for attribute in p2.matching(p1) ))

    def test_matching_common(self):
        """
        Test that the matching attributes are actually common.
        """

        p1, p2 = Profile(attributes={ 'plays_as': { 'striker' } }), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertTrue(p1.matching(p2))
        self.assertTrue(all( attribute in p1.common(p2) for attribute in p1.matching(p2) ))

    def test_matching_returns_attributes(self):
        """
        Test that when matching attributes, the attribute names are returned.
        """

        p1, p2 = Profile(attributes={ 'plays_as': { 'striker' } }), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertTrue(p1.matching(p2))
        self.assertTrue(all( attribute in p1.attributes for attribute in p1.matching(p2) ))
        self.assertTrue(all( attribute in p2.attributes for attribute in p1.matching(p2) ))

    def test_matching_excludes_unmatch(self):
        """
        Test that the attributes that appear in only one profile are excluded.
        """

        p1, p2 = Profile(attributes={ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertFalse('plays_for' in p1.matching(p2))
        self.assertFalse('plays_for' in p2.matching(p1))

    def test_matching_set(self):
        """
        Test that getting the matching attributes in two profiles returns an set.
        """

        p1, p2 = Profile(attributes={ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertEqual(set, type(p1.matching(p2)))
        self.assertEqual(set, type(p2.matching(p1)))

    def test_matching_symmetric(self):
        """
        Test that when getting the matching attributes in two profiles, the order does not matter.
        """

        p1, p2 = Profile(attributes={ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile(attributes={ 'plays_as': { 'striker' } })
        self.assertEqual(p1.matching(p2), p2.matching(p1))

    def test_matching_numbers(self):
        """
        Test that when matching numbers, attributes are matched correctly.
        """

        p1, p2 = Profile(attributes={ 'age': 26 }), Profile(attributes={ 'age': 26 })
        self.assertEqual({ 'age' }, p1.matching(p2))

    def test_matching_numbers_policy_irrelevant(self):
        """
        Test that when matching numbers, the policy has no effect.
        """

        p1, p2 = Profile(attributes={ 'age': 26 }), Profile(attributes={ 'age': 26 })
        self.assertEqual({ 'age' }, p1.matching(p2, policy=any))
        self.assertEqual(p1.matching(p2, policy=any), p1.matching(p2, policy=all))

    def test_matching_strings(self):
        """
        Test that when matching strings, attributes are matched correctly.
        """

        p1, p2 = Profile(attributes={ 'plays_as': 'striker' }), Profile(attributes={ 'plays_as': 'striker' })
        self.assertEqual({ 'plays_as' }, p1.matching(p2))

    def test_matching_strings_not_iterable(self):
        """
        Test that strings are not treated as iterables.
        """

        p1, p2 = Profile(attributes={ 'plays_in': 'all' }), Profile(attributes={ 'plays_in': 'al' })
        self.assertEqual(set(), p1.matching(p2))
        p1, p2 = Profile(attributes={ 'plays_in': 'all' }), Profile(attributes={ 'plays_in': 'all' })
        self.assertEqual({ 'plays_in' }, p1.matching(p2))

    def test_matching_strings_policy_irrelevant(self):
        """
        Test that when matching strings, the policy has no effect.
        """

        p1, p2 = Profile(attributes={ 'plays_as': 'striker' }), Profile(attributes={ 'plays_as': 'striker' })
        self.assertEqual({ 'plays_as' }, p1.matching(p2, policy=any))
        self.assertEqual(p1.matching(p2, policy=any), p1.matching(p2, policy=all))

    def test_matching_set_policy(self):
        """
        Test that when matching sets of values, the policy has an effect.
        """

        p1, p2 = Profile(attributes={ 'plays_as': { 'striker', 'midfielder' }, 'plays_for': { 'lyon' } }), Profile(attributes={ 'plays_as': { 'striker', 'defender' }, 'plays_for': { 'marseille' } })
        self.assertEqual({ 'plays_as' }, p1.matching(p2, policy=any))
        self.assertEqual(set(), p1.matching(p2, policy=all))

    def test_matching_list_policy(self):
        """
        Test that when matching lists of values, the policy has an effect.
        """

        p1, p2 = Profile(attributes={ 'plays_as': [ 'striker', 'midfielder' ], 'plays_for': [ 'lyon' ] }), Profile(attributes={ 'plays_as': [ 'striker', 'defender' ], 'plays_for': [ 'marseille' ] })
        self.assertEqual({ 'plays_as' }, p1.matching(p2, policy=any))
        self.assertEqual(set(), p1.matching(p2, policy=all))

    def test_matching_list_policy(self):
        """
        Test that when matching lists of values, the policy has an effect.
        """

        p1, p2 = Profile(attributes={ 'plays_as': [ 'striker', 'midfielder' ], 'plays_for': [ 'lyon' ] }), Profile(attributes={ 'plays_as': [ 'striker', 'defender' ], 'plays_for': [ 'marseille' ] })
        self.assertEqual({ 'plays_as' }, p1.matching(p2, policy=any))
        self.assertEqual(set(), p1.matching(p2, policy=all))

    def test_matching_iterable_symmetric(self):
        """
        Test that when matching an iterable, both sides are checked.
        """

        p1, p2 = Profile(attributes={ 'plays_as': [ 'striker' ] }), Profile(attributes={ 'plays_as': [ 'striker', 'defender' ] })
        self.assertEqual({ 'plays_as' }, p1.matching(p2, policy=any))
        self.assertEqual(set(), p1.matching(p2, policy=all))

    def test_type_returns_str(self):
        """
        Test that the type of a profile is returned as a string.
        """

        text = "Max Emilian Verstappen (born 30 September 1997) is a Belgian-Dutch[2] racing driver and the 2021 Formula One World Champion."
        profile = LinguisticExtractor().extract(text)
        self.assertEqual(str, type(profile.type()))

    def test_type_empty_profile(self):
        """
        Test that an empty profile has no type.
        """

        profile = Profile()
        self.assertEqual(None, profile.type())

    def test_type_born_heuristic(self):
        """
        Test that a profile that has a `born` attribute automatically gets the type of a person.
        """

        profile = Profile(attributes={ 'born': [ '1958' ] })
        self.assertEqual("PERSON", profile.type())

    def test_type_born_PRP_heuristic(self):
        """
        Test that a profile that has a `born` attribute automatically gets the type of a person.
        """

        profile = Profile(attributes={ 'born_in': [ 'louisiana' ] })
        self.assertEqual("PERSON", profile.type())

    def test_type_from_text(self):
        """
        Test that if no heuristics apply, the profile's type is determined from the text.
        """

        text = "Max Emilian Verstappen (born 30 September 1997) is a Belgian-Dutch[2] racing driver and the 2021 Formula One World Champion."
        profile = LinguisticExtractor().extract(text)
        self.assertTrue('born' not in profile.attributes)
        self.assertEqual('PERSON', profile.type())

        text = "Salzburg (Austrian German: [ˈsaltsbʊʁk], German: [ˈzaltsbʊʁk] (listen);[note 1] literally \"Salt-Mountain\"; Austro-Bavarian: Soizbuag) is the fourth-largest city in Austria."
        profile = LinguisticExtractor().extract(text)
        self.assertEqual('GPE', profile.type())

    def test_type_not_start(self):
        """
        Test that if no heuristics apply and the profile's text does not start with a recognized named entity, but the named entity appears later, it inherits the found type.
        """

        text = "Red Bull Racing, also simply known as Red Bull or RBR and competing as Oracle Red Bull Racing, is a Formula One racing team, racing under an Austrian licence and based in the United Kingdom."
        profile = LinguisticExtractor().extract(text)
        self.assertEqual("ORGANIZATION", profile.type())

    def test_type_unknown(self):
        """
        Test that if no heuristics apply and the profile's text does not start with a recognized named entity, its type is taken to be `None`.
        """

        text = "The GP2 Series was a form of open wheel motor racing introduced in 2005 following the discontinuation of the long-term Formula One feeder series, Formula 3000."
        profile = LinguisticExtractor().extract(text)
        self.assertEqual(None, profile.type())

    def test_is_person_returns_bool(self):
        """
        Test that the function to check whether a profile represents a person returns a boolean.
        """

        text = "Max Emilian Verstappen (born 30 September 1997) is a Belgian-Dutch[2] racing driver and the 2021 Formula One World Champion."
        profile = LinguisticExtractor().extract(text)
        self.assertEqual(bool, type(profile.is_person()))

    def test_is_person_true(self):
        """
        Test that the function to check whether a profile represents a person returns `True` if the profile represents a person.
        """

        text = "Max Emilian Verstappen (born 30 September 1997) is a Belgian-Dutch[2] racing driver and the 2021 Formula One World Champion."
        profile = LinguisticExtractor().extract(text)
        self.assertTrue(profile.is_person())

    def test_is_person_false(self):
        """
        Test that the function to check whether a profile represents a person returns `False` if the profile does not represent a person.
        """

        text = "Red Bull Racing, also simply known as Red Bull or RBR and competing as Oracle Red Bull Racing, is a Formula One racing team, racing under an Austrian licence and based in the United Kingdom."
        profile = LinguisticExtractor().extract(text)
        self.assertFalse(profile.is_person())

    def test_is_person_same_as_type(self):
        """
        Test that the function to check whether a profile represents a person returns the same output as the type function.
        """

        corpus = [ "Red Bull Racing, also simply known as Red Bull or RBR and competing as Oracle Red Bull Racing, is a Formula One racing team, racing under an Austrian licence and based in the United Kingdom.",
                   "Max Emilian Verstappen (born 30 September 1997) is a Belgian-Dutch[2] racing driver and the 2021 Formula One World Champion.",
                   "The GP2 Series was a form of open wheel motor racing introduced in 2005 following the discontinuation of the long-term Formula One feeder series, Formula 3000.",
                   "Salzburg (Austrian German: [ˈsaltsbʊʁk], German: [ˈzaltsbʊʁk] (listen);[note 1] literally \"Salt-Mountain\"; Austro-Bavarian: Soizbuag) is the fourth-largest city in Austria." ]

        for text in corpus:
            profile = LinguisticExtractor().extract(text)
            self.assertEqual(profile.is_person(), (profile.type() == "PERSON"))

    def test_is_location_returns_bool(self):
        """
        Test that the function to check whether a profile represents a location returns a boolean.
        """

        text = "Max Emilian Verstappen (born 30 September 1997) is a Belgian-Dutch[2] racing driver and the 2021 Formula One World Champion."
        profile = LinguisticExtractor().extract(text)
        self.assertEqual(bool, type(profile.is_location()))

    def test_is_location_true(self):
        """
        Test that the function to check whether a profile represents a location returns `True` if the profile represents a location.
        """

        text = "Salzburg (Austrian German: [ˈsaltsbʊʁk], German: [ˈzaltsbʊʁk] (listen);[note 1] literally \"Salt-Mountain\"; Austro-Bavarian: Soizbuag) is the fourth-largest city in Austria."
        profile = LinguisticExtractor().extract(text)
        self.assertTrue(profile.is_location())

    def test_is_location_false(self):
        """
        Test that the function to check whether a profile represents a location returns `False` if the profile does not represent a location.
        """

        text = "Red Bull Racing, also simply known as Red Bull or RBR and competing as Oracle Red Bull Racing, is a Formula One racing team, racing under an Austrian licence and based in the United Kingdom."
        profile = LinguisticExtractor().extract(text)
        self.assertFalse(profile.is_location())

    def test_is_location_same_as_type(self):
        """
        Test that the function to check whether a profile represents a location returns the same output as the type function.
        """

        corpus = [ "Red Bull Racing, also simply known as Red Bull or RBR and competing as Oracle Red Bull Racing, is a Formula One racing team, racing under an Austrian licence and based in the United Kingdom.",
                   "Max Emilian Verstappen (born 30 September 1997) is a Belgian-Dutch[2] racing driver and the 2021 Formula One World Champion.",
                   "The GP2 Series was a form of open wheel motor racing introduced in 2005 following the discontinuation of the long-term Formula One feeder series, Formula 3000.",
                   "Salzburg (Austrian German: [ˈsaltsbʊʁk], German: [ˈzaltsbʊʁk] (listen);[note 1] literally \"Salt-Mountain\"; Austro-Bavarian: Soizbuag) is the fourth-largest city in Austria.",
                   "Austria, officially the Republic of Austria, is a landlocked country in the southern part of Central Europe, situated at Eastern Alps." ]

        for text in corpus:
            profile = LinguisticExtractor().extract(text)
            self.assertEqual(profile.is_location(), (profile.type() == "GPE" or profile.type() == "GSP"))

    def test_is_organization_returns_bool(self):
        """
        Test that the function to check whether a profile represents an organization returns a boolean.
        """

        text = "Max Emilian Verstappen (born 30 September 1997) is a Belgian-Dutch[2] racing driver and the 2021 Formula One World Champion."
        profile = LinguisticExtractor().extract(text)
        self.assertEqual(bool, type(profile.is_organization()))

    def test_is_organization_true(self):
        """
        Test that the function to check whether a profile represents an organization returns `True` if the profile represents an organization.
        """

        text = "Red Bull Racing, also simply known as Red Bull or RBR and competing as Oracle Red Bull Racing, is a Formula One racing team, racing under an Austrian licence and based in the United Kingdom."
        profile = LinguisticExtractor().extract(text)
        self.assertTrue(profile.is_organization())

    def test_is_organization_false(self):
        """
        Test that the function to check whether a profile represents an organization returns `False` if the profile does not represent an organization.
        """

        text = "Salzburg (Austrian German: [ˈsaltsbʊʁk], German: [ˈzaltsbʊʁk] (listen);[note 1] literally \"Salt-Mountain\"; Austro-Bavarian: Soizbuag) is the fourth-largest city in Austria."
        profile = LinguisticExtractor().extract(text)
        self.assertFalse(profile.is_organization())

    def test_is_organization_same_as_type(self):
        """
        Test that the function to check whether a profile represents an organization returns the same output as the type function.
        """

        corpus = [ "Red Bull Racing, also simply known as Red Bull or RBR and competing as Oracle Red Bull Racing, is a Formula One racing team, racing under an Austrian licence and based in the United Kingdom.",
                   "Max Emilian Verstappen (born 30 September 1997) is a Belgian-Dutch[2] racing driver and the 2021 Formula One World Champion.",
                   "The GP2 Series was a form of open wheel motor racing introduced in 2005 following the discontinuation of the long-term Formula One feeder series, Formula 3000.",
                   "Salzburg (Austrian German: [ˈsaltsbʊʁk], German: [ˈzaltsbʊʁk] (listen);[note 1] literally \"Salt-Mountain\"; Austro-Bavarian: Soizbuag) is the fourth-largest city in Austria." ]

        for text in corpus:
            profile = LinguisticExtractor().extract(text)
            self.assertEqual(profile.is_organization(), (profile.type() == "ORGANIZATION"))

    def test_export(self):
        """
        Test exporting and importing :class:`~attributes.profile.Profile`.
        """

        profile = Profile('Test entity', 'Source text', { 'x': 3 })
        exported = profile.to_array()
        self.assertEqual(profile.attributes, Profile.from_array(exported).attributes)
        self.assertEqual(profile.__dict__, Profile.from_array(exported).__dict__)

    def test_export_name(self):
        """
        Test that exporting and importing :class:`~attributes.profile.Profile` includes the name.
        """

        name = 'Test entity'
        profile = Profile(name=name, attributes={ 'x': 3 })
        exported = profile.to_array()
        self.assertEqual(name, Profile.from_array(exported).name)
        self.assertEqual(profile.__dict__, Profile.from_array(exported).__dict__)

    def test_export_text(self):
        """
        Test that exporting and importing :class:`~attributes.profile.Profile` includes the text.
        """

        text = 'Source text'
        profile = Profile(text=text, attributes={ 'x': 3 })
        exported = profile.to_array()
        self.assertEqual(text, Profile.from_array(exported).text)
        self.assertEqual(profile.__dict__, Profile.from_array(exported).__dict__)

    def test_copy_attributes_original(self):
        """
        Test that changing the copy's attributes does not affect the original's, and vice-versa.
        """

        profile = Profile(text='Source text', attributes={ 'y': True, 'z': False })
        copy = profile.copy()

        copy.attributes['y'] = False
        self.assertFalse(copy.attributes['y'])
        self.assertTrue(profile.attributes['y'])

        profile.attributes['z'] = True
        self.assertFalse(copy.attributes['z'])
        self.assertTrue(profile.attributes['z'])

    def test_copy_nested_attributes_original(self):
        """
        Test that changing the copy's nested attributes does not affect the original's, and vice-versa.
        """

        profile = Profile(text='Source text', attributes={ 'y': { 'a': True }, 'z': { 'b': False } })
        copy = profile.copy()

        copy.attributes['y']['a'] = False
        self.assertFalse(copy.attributes['y']['a'])
        self.assertTrue(profile.attributes['y']['a'])

        profile.attributes['z']['b'] = True
        self.assertFalse(copy.attributes['z']['b'])
        self.assertTrue(profile.attributes['z']['b'])

    def test_copy_text_original(self):
        """
        Test that changing the copy's text does not affect the original's, and vice-versa.
        """

        text = 'Source text'
        profile = Profile(text=text, attributes={ 'x': 3 })
        copy = profile.copy()

        copy.text = 'lorem ipsum'
        self.assertEqual('lorem ipsum', copy.text)
        self.assertEqual(text, profile.text)

        profile.text = 'dolor sit amet'
        self.assertEqual('lorem ipsum', copy.text)
        self.assertEqual('dolor sit amet', profile.text)

    def test_copy_name_original(self):
        """
        Test that changing the copy's name does not affect the original's, and vice-versa.
        """

        name = 'Source'
        profile = Profile(name=name, attributes={ 'x': 3 })
        copy = profile.copy()

        copy.name = 'lorem ipsum'
        self.assertEqual('lorem ipsum', copy.name)
        self.assertEqual(name, profile.name)

        profile.name = 'dolor sit amet'
        self.assertEqual('lorem ipsum', copy.name)
        self.assertEqual('dolor sit amet', profile.name)
