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

        profile = Profile(None)
        self.assertEqual({ }, profile.attributes)

    def test_init_default_attributes(self):
        """
        Test that when providing default attributes, they are stored.
        """

        profile = Profile({ 'known_as': 'Memphis', 'age': 26 })
        self.assertEqual({ 'known_as': 'Memphis', 'age': 26 }, profile.attributes)

    def test_attributes_overwrite(self):
        """
        Test that setting the attributes overwrites the previous attributes.
        """

        profile = Profile({ 'known_as': 'Memphis', 'age': 26 })
        self.assertEqual({ 'known_as': 'Memphis', 'age': 26 }, profile.attributes)

        profile.attributes = { 'name': 'Memphis Depay' }
        self.assertEqual({ 'name': 'Memphis Depay' }, profile.attributes)

    def test_attributes_overwrite_none(self):
        """
        Test that overwriting the attributes with ``None`` creates an empty dictionary of attributes.
        """

        profile = Profile({ 'known_as': 'Memphis', 'age': 26 })
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

        profile = Profile({ 'known_as': 'Memphis Depay', 'age': 26 })
        self.assertEqual({ 'known_as': 'Memphis Depay', 'age': 26 }, profile.attributes)

        profile.attributes['known_as'] = 'Memphis'
        self.assertEqual({ 'known_as': 'Memphis', 'age': 26 }, profile.attributes)

    def test_attributes_remove(self):
        """
        Test removing an existing attribute from a profile.
        """

        profile = Profile({ 'known_as': 'Memphis Depay', 'age': 26 })
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

        p1, p2 = Profile(), Profile({ 'plays_as': { 'striker' } })
        self.assertEqual(set(), p1.common(p2))
        self.assertEqual(set(), p2.common(p1))

    def test_common_none(self):
        """
        Test that when two profiles share no attributes, no common attributes are returned.
        """

        p1, p2 = Profile({ 'plays_for': { 'lyon' } }), Profile({ 'plays_as': { 'striker' } })
        self.assertEqual(set(), p1.common(p2))
        self.assertEqual(set(), p2.common(p1))

    def test_common_in_both(self):
        """
        Test that the common attributes actually exist in both profiles.
        """

        p1, p2 = Profile({ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile({ 'plays_as': { 'striker' } })
        self.assertTrue(all( attribute in p1.attributes and attribute in p2.attributes for attribute in p1.common(p2) ))
        self.assertTrue(all( attribute in p1.attributes and attribute in p2.attributes for attribute in p2.common(p1) ))

    def test_common_ignores_values(self):
        """
        Test that the common attributes ignores the value of attributes.
        """

        p1, p2 = Profile({ 'plays_for': { 'lyon' }, 'plays_as': { 'midfielder' } }), Profile({ 'plays_as': { 'striker' } })
        self.assertFalse(p1.attributes['plays_as'] == p2.attributes['plays_as'])
        self.assertEqual({ 'plays_as' }, p1.common(p2))
        self.assertEqual({ 'plays_as' }, p2.common(p1))

    def test_common_excludes_uncommon(self):
        """
        Test that the attributes that appear in only one profile are excluded.
        """

        p1, p2 = Profile({ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile({ 'plays_as': { 'striker' } })
        self.assertFalse('plays_for' in p1.common(p2))
        self.assertFalse('plays_for' in p2.common(p1))

    def test_common_set(self):
        """
        Test that getting the common attributes in two profiles returns an set.
        """

        p1, p2 = Profile({ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile({ 'plays_as': { 'striker' } })
        self.assertEqual(set, type(p1.common(p2)))
        self.assertEqual(set, type(p2.common(p1)))

    def test_common_symmetric(self):
        """
        Test that when getting the common attributes in two profiles, the order does not matter.
        """

        p1, p2 = Profile({ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile({ 'plays_as': { 'striker' } })
        self.assertEqual(p1.common(p2), p2.common(p1))

    def test_match_empty(self):
        """
        Test that getting the matching attributes in two empty profiles returns an empty set.
        """

        p1, p2 = Profile(), Profile()
        self.assertEqual(set(), p1.match(p2))

    def test_match_one_empty(self):
        """
        Test that getting the matching attributes and one profile is empty, the function returns an empty set.
        """

        p1, p2 = Profile(), Profile({ 'plays_as': { 'striker' } })
        self.assertEqual(set(), p1.match(p2))
        self.assertEqual(set(), p2.match(p1))

    def test_match_none(self):
        """
        Test that when two profiles share no attributes, no match attributes are returned.
        """

        p1, p2 = Profile({ 'plays_for': { 'lyon' } }), Profile({ 'plays_as': { 'striker' } })
        self.assertEqual(set(), p1.match(p2))
        self.assertEqual(set(), p2.match(p1))

    def test_match_in_both(self):
        """
        Test that the matching attributes actually exist in both profiles.
        """

        p1, p2 = Profile({ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile({ 'plays_as': { 'striker' } })
        self.assertTrue(all( attribute in p1.attributes and attribute in p2.attributes for attribute in p1.match(p2) ))
        self.assertTrue(all( attribute in p1.attributes and attribute in p2.attributes for attribute in p2.match(p1) ))

    def test_match_common(self):
        """
        Test that the matching attributes are actually common.
        """

        p1, p2 = Profile({ 'plays_as': { 'striker' } }), Profile({ 'plays_as': { 'striker' } })
        self.assertTrue(p1.match(p2))
        self.assertTrue(all( attribute in p1.common(p2) for attribute in p1.match(p2) ))

    def test_match_returns_attributes(self):
        """
        Test that when matching attributes, the attribute names are returned.
        """

        p1, p2 = Profile({ 'plays_as': { 'striker' } }), Profile({ 'plays_as': { 'striker' } })
        self.assertTrue(p1.match(p2))
        self.assertTrue(all( attribute in p1.attributes for attribute in p1.match(p2) ))
        self.assertTrue(all( attribute in p2.attributes for attribute in p1.match(p2) ))

    def test_match_excludes_unmatch(self):
        """
        Test that the attributes that appear in only one profile are excluded.
        """

        p1, p2 = Profile({ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile({ 'plays_as': { 'striker' } })
        self.assertFalse('plays_for' in p1.match(p2))
        self.assertFalse('plays_for' in p2.match(p1))

    def test_match_set(self):
        """
        Test that getting the matching attributes in two profiles returns an set.
        """

        p1, p2 = Profile({ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile({ 'plays_as': { 'striker' } })
        self.assertEqual(set, type(p1.match(p2)))
        self.assertEqual(set, type(p2.match(p1)))

    def test_match_symmetric(self):
        """
        Test that when getting the matching attributes in two profiles, the order does not matter.
        """

        p1, p2 = Profile({ 'plays_for': { 'lyon' }, 'plays_as': { 'striker' } }), Profile({ 'plays_as': { 'striker' } })
        self.assertEqual(p1.match(p2), p2.match(p1))

    def test_match_numbers(self):
        """
        Test that when matching numbers, attributes are matched correctly.
        """

        p1, p2 = Profile({ 'age': 26 }), Profile({ 'age': 26 })
        self.assertEqual({ 'age' }, p1.match(p2))

    def test_match_numbers_policy_irrelevant(self):
        """
        Test that when matching numbers, the policy has no effect.
        """

        p1, p2 = Profile({ 'age': 26 }), Profile({ 'age': 26 })
        self.assertEqual({ 'age' }, p1.match(p2, policy=any))
        self.assertEqual(p1.match(p2, policy=any), p1.match(p2, policy=all))

    def test_match_strings(self):
        """
        Test that when matching strings, attributes are matched correctly.
        """

        p1, p2 = Profile({ 'plays_as': 'striker' }), Profile({ 'plays_as': 'striker' })
        self.assertEqual({ 'plays_as' }, p1.match(p2))

    def test_match_strings_not_iterable(self):
        """
        Test that strings are not treated as iterables.
        """

        p1, p2 = Profile({ 'plays_in': 'all' }), Profile({ 'plays_in': 'al' })
        self.assertEqual(set(), p1.match(p2))
        p1, p2 = Profile({ 'plays_in': 'all' }), Profile({ 'plays_in': 'all' })
        self.assertEqual({ 'plays_in' }, p1.match(p2))

    def test_match_strings_policy_irrelevant(self):
        """
        Test that when matching strings, the policy has no effect.
        """

        p1, p2 = Profile({ 'plays_as': 'striker' }), Profile({ 'plays_as': 'striker' })
        self.assertEqual({ 'plays_as' }, p1.match(p2, policy=any))
        self.assertEqual(p1.match(p2, policy=any), p1.match(p2, policy=all))

    def test_match_set_policy(self):
        """
        Test that when matching sets of values, the policy has an effect.
        """

        p1, p2 = Profile({ 'plays_as': { 'striker', 'midfielder' }, 'plays_for': { 'lyon' } }), Profile({ 'plays_as': { 'striker', 'defender' }, 'plays_for': { 'marseille' } })
        self.assertEqual({ 'plays_as' }, p1.match(p2, policy=any))
        self.assertEqual(set(), p1.match(p2, policy=all))

    def test_match_list_policy(self):
        """
        Test that when matching lists of values, the policy has an effect.
        """

        p1, p2 = Profile({ 'plays_as': [ 'striker', 'midfielder' ], 'plays_for': [ 'lyon' ] }), Profile({ 'plays_as': [ 'striker', 'defender' ], 'plays_for': [ 'marseille' ] })
        self.assertEqual({ 'plays_as' }, p1.match(p2, policy=any))
        self.assertEqual(set(), p1.match(p2, policy=all))

    def test_match_list_policy(self):
        """
        Test that when matching lists of values, the policy has an effect.
        """

        p1, p2 = Profile({ 'plays_as': [ 'striker', 'midfielder' ], 'plays_for': [ 'lyon' ] }), Profile({ 'plays_as': [ 'striker', 'defender' ], 'plays_for': [ 'marseille' ] })
        self.assertEqual({ 'plays_as' }, p1.match(p2, policy=any))
        self.assertEqual(set(), p1.match(p2, policy=all))

    def test_match_iterable_symmetric(self):
        """
        Test that when matching an iterable, both sides are checked.
        """

        p1, p2 = Profile({ 'plays_as': [ 'striker' ] }), Profile({ 'plays_as': [ 'striker', 'defender' ] })
        self.assertEqual({ 'plays_as' }, p1.match(p2, policy=any))
        self.assertEqual(set(), p1.match(p2, policy=all))
