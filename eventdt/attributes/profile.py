"""
Each class or instance can have multiple attributes.
The :class:`~attributes.profile.Profile` is a simple container for these attributes.
"""

class Profile(object):
    """
    The :class:`~attributes.profile.Profile` stores a list of attributes and their respective values.
    This class stores these attributes as a dictionary, which can be accessed directly.
    It expects attribute names to be strings, but values can be any datatype.

    :ivar attributes: The attributes stored in this profile.
                      The attribute name is the key, and the value is the corresponding attribute value.
    :vartype attributes: dict
    """

    def __init__(self, attributes=None):
        """
        Initialize the profile with attributes.

        :param attributes: The default attributes.
                           If ``None`` is given, an empty dictionary is initialized instead.
        :type attributes: None or dict
        """

        self.attributes = attributes or { }

    @property
    def attributes(self):
        """
        Get the attributes of this profile.

        :return: The attributes stored in this profile.
                 The attribute name is the key, and the value is the corresponding attribute value.
        :rtype: dict
        """

        return self.__attributes

    @attributes.setter
    def attributes(self, attributes):
        """
        Override the attributes in this profile.

        :param attributes: The new attributes.
                           If ``None`` is given, an empty dictionary is initialized instead.
        :type attributes: None or dict
        """

        self.__attributes = attributes or { }
