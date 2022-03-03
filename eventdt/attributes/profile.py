"""
Each class or instance can have multiple attributes.
The :class:`~attributes.profile.Profile` is a simple container for these attributes.
"""

from collections.abc import Iterable
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from objects import Attributable

class Profile(Attributable):
    """
    The :class:`~attributes.profile.Profile` stores a list of attributes and their respective values.
    This class stores these attributes as a dictionary, which can be accessed directly.
    It expects attribute names to be strings, but values can be any datatype.

    :ivar name: The name of the entity that the profile represents.
    :vartype name: str
    :ivar attributes: The attributes stored in this profile.
                      The attribute name is the key, and the value is the corresponding attribute value.
    :vartype attributes: dict
    """

    def __init__(self, name=None, *args, **kwargs):
        """
        Initialize the profile with attributes.

        :param name: The name of the entity that the profile represents.
        :type name: str or None
        """

        super(Profile, self).__init__(*args, **kwargs)
        self.name = name or ''

    def common(self, other):
        """
        Get the list of attributes that are shared between this profile and the given profile.

        :param other: The second profile compare with the current one.
        :type other: :class:`~attributes.profile.Profile`

        :return: A list of attributes that are common among the two profiles.
        :rtype: set of str
        """

        return set(self.attributes).intersection(set(other.attributes))

    def match(self, other, policy=any):
        """
        Get a list of attributes that are common between this profile and the other profile.

        :param other: The second profile compare with the current one.
        :type other: :class:`~attributes.profile.Profile`
        :param policy: A function to check the overlap between the two profiles when an attribute's values are iterable:

                       - If ``any`` is given, then it suffices for two profiles to share one value for a given attribute to match the attribute.
                       - If ``all`` is given, then the two profiles' values for a given attribute must be the same to match the attribute.

        :return: A list of attributes that are common among the two profiles and have the same values, based on the matching policy.
        :rtype: set of str
        """

        matching = set()

        common = self.common(other)
        for attribute in common:
            # convert the attribute values into iterables if they aren't already (except for strings)
            v1, v2 = self.attributes[attribute], other.attributes[attribute]
            v1 = v1 if (isinstance(v1, Iterable) and not isinstance(v1, str)) else { v1 }
            v2 = v2 if (isinstance(v2, Iterable) and not isinstance(v2, str)) else { v2 }

            # check that any (or all) values in one profile's attribute exist in the other profile's attribute, and vice-versa
            if policy(v in v2 for v in v1) and policy(v in v1 for v in v2):
                matching.add(attribute)

        return matching

    def __str__(self):
        """
        Get the string representation of the profile.
        This function returns the profile name, if it is set, and a list of attributes.

        :return: The string representation of the summary.
        :rtype: str
        """

        _str = ''

        title = self.name or super().__str__()
        _str += f"{ title }\n"
        _str += f"{ '-' * len(title) }\n"
        _str += '\n'

        for attribute, value in self.attributes.items():
            _str += f"    { attribute }: { str(value) }\n"

        return _str
