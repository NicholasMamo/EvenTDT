"""
Each class or instance can have multiple attributes.
The :class:`~attributes.profile.Profile` is a simple container for these attributes.
"""

from collections.abc import Iterable
import copy
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from objects import Attributable, Exportable
import nlp

class Profile(Attributable, Exportable):
    """
    The :class:`~attributes.profile.Profile` stores a list of attributes and their respective values.
    This class stores these attributes as a dictionary, which can be accessed directly.
    It expects attribute names to be strings, but values can have any datatype.

    :ivar name: The name of the entity that the profile represents.
    :vartype name: str
    :ivar text: The text from which the profile was created.
    :vartype text: str
    """

    def __init__(self, name=None, text=None, *args, **kwargs):
        """
        Initialize the profile with attributes.

        :param name: The name of the entity that the profile represents.
        :type name: str or None
        :param text: The text from which the profile was created.
        :type text: str
        """

        super(Profile, self).__init__(*args, **kwargs)
        self.name = name or ''
        self.text = text or ''

    def common(self, other):
        """
        Get the list of attributes that appear in this profile and the given profile.

        :param other: The second profile compare with the current one.
        :type other: :class:`~attributes.profile.Profile`

        :return: A list of attributes that are common among the two profiles.
        :rtype: set of str
        """

        return set(self.attributes).intersection(set(other.attributes))

    def matching(self, other, policy=any):
        """
        Get the list of attributes that appear in this profile and the given profile with the same values.

        This function can be used to calculate the Jaccard similarity as it gives the intersection of attributes between two profiles as long as they have the same value.

        :param other: The second profile compare with the current one.
        :type other: :class:`~attributes.profile.Profile`
        :param policy: A function to check the overlap between the two profiles when an attribute's values are iterable:

                       - If ``any`` is given, then it suffices for two profiles to share one value for a given attribute to match the attribute.
                       - If ``all`` is given, then the two profiles' values for a given attribute must be the same to match the attribute.

        :return: A list of attributes that are common among the two profiles and have the same values, based on the matching policy.
        :rtype: set of str
        """

        _matching = set()

        common = self.common(other)
        for attribute in common:
            # convert the attribute values into iterables if they aren't already (except for strings)
            v1, v2 = self.attributes[attribute], other.attributes[attribute]
            v1 = v1 if (isinstance(v1, Iterable) and not isinstance(v1, str)) else { v1 }
            v2 = v2 if (isinstance(v2, Iterable) and not isinstance(v2, str)) else { v2 }

            # check that any (or all) values in one profile's attribute exist in the other profile's attribute, and vice-versa
            if policy(v in v2 for v in v1) and policy(v in v1 for v in v2):
                _matching.add(attribute)

        return _matching

    def type(self):
        """
        Get the type of entity that the profile represents.

        The function uses a combination of heuristics.
        If the profile has an attribute that starts with `born`, for example, the function assumes that the profile represents a person.

        The function also assumes that the profile was created from a Wikipedia definition sentence.
        The assumption thus requires that the first words name the entity.

        :return: The type of named entity that the profile represents.
                 The types can be one of NLTK's, namely _PERSON_, _GPE_ or _ORGANIZATION_.
                 The function returns `None` if the profile could not be resolved to a type.
        :rtype: str or None
        """

        if any( attribute.startswith('born') for attribute in self.attributes ):
            return "PERSON"

        entities = nlp.entities(self.text)
        for entity, _type in entities:
            if self.text.startswith(entity):
                return _type

        return None

    def is_person(self):
        """
        Check whether the profile represents a person.

        :return: A boolean indicating whether the profile represents a person.
        :rtype: bool
        """

        return self.type() == "PERSON"

    def is_location(self):
        """
        Check whether the profile represents a location.

        :return: A boolean indicating whether the profile represents a location.
        :rtype: bool
        """

        return self.type() in [ "GPE", "GSP", "LOCATION"]

    def is_organization(self):
        """
        Check whether the profile represents an organization.

        :return: A boolean indicating whether the profile represents an organization.
        :rtype: bool
        """

        return self.type() == "ORGANIZATION"

    def filter(self, netype):
        """
        Filter the profile's attributes to retain only those attributes and values that match the given named entity type.

        :param netype: The type of named entity to extract, possibly more than one.
                       The function accepts the same types as NLTK, namely _PERSON_, _GPE_, _GSP_ or _LOCATION, or _ORGANIZATION_.
        :type netype: str or list of str

        :return: A new profile filtered to retain only those attributes and values that have the desired named entity type.
        :rtype: :class:`~attributes.profile.Profile`
        """

        profile = self.copy()

        netype = [ netype ] if type(netype) is str else netype
        entities = nlp.entities(self.text) # fetch all named entities and filter them later
        entities = [ entity for entity, _type in entities if _type in netype ]
        entities = [ entity.lower() for entity in entities ]

        # filter the copied profile
        profile.attributes = { attribute: { value for value in values
                                                  if value.lower() in entities }
                                          for attribute, values in profile.attributes.items()  }
        profile.attributes = { attribute: values for attribute, values in profile.attributes.items()
                                                 if values } # remove empty attributes
        return profile

    def to_array(self):
        """
        Export the :class:`~Profile` as ``dict``.
        This ``dict`` has three keys:

            1. The class name, used when re-creating the :class:`~Profile`,
            2. The name of the entity represented by this object,
            3. The source text from where the attributes where extracted, and
            4. The :class:`~Profile`'s attributes as a ``dict``.

        :return: The :class:`~Profile` as ``dict``.
        :rtype: dict
        """

        return {
            'class': str(Profile),
            'name': self.name,
            'text': self.text,
            'attributes': copy.deepcopy(self.attributes)
        }

    @staticmethod
    def from_array(array):
        """
        Create an instance of the :class:`~Profile` from the given ``dict``.
        This function expects the array to have been generated by the :func:`~Profile.to_array`, and must have these keys:

            1. The class name,
            2. The name of the entity represented by this object,
            3. The source text from where the attributes where extracted, and
            4. The :class:`~Profile`'s attributes as a ``dict``.

        :param array: The ``dict`` with the attributes to create the :class:`~Profile`.
        :type array: dict

        :return: A new instance of the :class:`~Profile` with the same attributes stored in the object.
        :rtype: :class:`~Profile`
        """

        return Profile(name=array.get('name'), text=array.get('text'),
                       attributes=copy.deepcopy(array.get('attributes')))

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
