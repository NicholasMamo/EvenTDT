"""
Exportable objects are normal objects that can be exported as a JSON string and loaded back.
"""

from abc import ABC, abstractmethod
import copy
import importlib
import json
from logger import logger
import re

class Exportable(ABC):
    """
    An abstract class of an object that can be exported as a JSON string and imported back.
    """

    ALIASES = { 'nlp.term_weighting': 'nlp.weighting',
                'summarization.timeline.timeline': 'summarization.timeline' }
    CLASS_PATTERN = re.compile('<class \'(.+)?\.?\'>')
    IMPORTED = { }

    unoptimized_hashing = False
    """
    A boolean indicating whether the :class:`~objects.exportable.Exportable` class has already reported unoptimized hashing.
    This boolean is set to ``True`` after the first warning to suppress repeated warnings.
    """

    @abstractmethod
    def to_array(self):
        """
        Export the object as a dictionary.

        :return: The object as a dictionary.
        :rtype: dict
        """

        pass

    @staticmethod
    @abstractmethod
    def from_array(array):
        """
        Create an instance of the object from the given dictionary.

        :param array: The dictionary with the attributes to create the object instance.
        :type array: dict

        :return: A new instance of an object with the same attributes stored in the object.
        :rtype: object
        """

        pass

    def copy(self):
        """
        Create a copy of the :class:`~Exportable` instance.

        :return: A copy of this :class:`~Exportable` instance.
        :rtype: :class:`~Exportable`
        """

        return self.from_array(self.to_array())

    @staticmethod
    def encode(data):
        """
        Try to encode the given data.
        This function expects a dictionary, a list or an object and checks if values are JSON serializable.
        If this is not possible, instances of :class:`~objects.exportable.Exportable` are converted to arrays.
        This is done through the :func:`~objects.exportable.Exportable.to_array` function.

        :param data: The data to encode.
        :type data: dict or list

        :return: The encoded data.
        :rtype: dict or list or object
        """

        data = copy.deepcopy(data)

        if type(data) is dict:
            # case 1: when a dictionary is given, encode all keys since some may represent an object
            for key in data:
                try:
                    data[key] = json.loads(json.dumps(data.get(key)))
                except TypeError:
                    if type(data[key]) in [ dict, list, set ]:
                        data[key] = Exportable.encode(data.get(key))
                    else:
                        data[key] = Exportable.encode(data.get(key).to_array())
        elif type(data) is list:
            # case 2: when a list is given, encode all items since some may represent an object
            for i, item in enumerate(data):
                try:
                    data[i] = json.loads(json.dumps(item))
                except TypeError:
                    if type(item) in [ dict, list, set ]:
                        data[i] = Exportable.encode(item)
                    else:
                        data[i] = Exportable.encode(item.to_array())
        elif type(data) is set:
            # case 3: when a set is given, encode it as a list (sets are not serializable)
            return Exportable.encode(list(data))
        else:
            # case 4: if any other object is given, try to encode it
            data = Exportable.encode(data.to_array())

        return data

    @staticmethod
    def decode(data):
        """
        A function that recursively decodes cached data.
        By decoded, it means that objects are created where necessary or possible.
        Only classes that inherit the :class:`~objects.exportable.Exportable` can be decoded.
        This is done through the :func:`~objects.exportable.Exportable.from_array` function.

        .. note::

            When decoding, the function expects either a dictionary or a list.
            JSON objects cannot be anything else.

        :param data: The data to decode.
        :type data: dict or list

        :return: A dictionary, list or object, but this time decoded.
        :rtype: dict or list or object
        """

        if type(data) not in ( dict, list ):
            return data

        _data = { } if type(data) is dict else [ ]

        if type(data) is dict and 'class' in data:
            """
            The first case is when the dictionary itself represents an object.
            """
            _module = Exportable.get_module(data.get('class'))
            module = Exportable.IMPORTED.get(_module, importlib.import_module(_module))
            Exportable.IMPORTED[_module] = module
            cls = getattr(module, Exportable.get_class(data.get('class')))
            _data = cls.from_array(data)
        elif type(data) is dict:
            """
            The second case is when a dictionary is given and all keys need to be decoded because some may represent an object.
            """
            for key in data:
                if type(data.get(key)) is dict and 'class' in data.get(key):
                    _module = Exportable.get_module(data.get(key).get('class'))
                    module = Exportable.IMPORTED.get(_module, importlib.import_module(_module))
                    Exportable.IMPORTED[_module] = module
                    cls = getattr(module, Exportable.get_class(data.get(key).get('class')))
                    _data[key] = cls.from_array(data.get(key))
                else:
                    _data[key] = Exportable.decode(data.get(key))
        elif type(data) is list:
            """
            The second case is when a list is given and all items need to be decoded because some may represent an object.
            """
            for item in data:
                if type(item) is dict and 'class' in item:
                    _module = Exportable.get_module(item.get('class'))
                    module = Exportable.IMPORTED.get(_module, importlib.import_module(_module))
                    Exportable.IMPORTED[_module] = module
                    cls = getattr(module, Exportable.get_class(item.get('class')))
                    _data.append(cls.from_array(item))
                else:
                    _data.append(Exportable.decode(item))

        return _data

    @staticmethod
    def get_module(cls):
        """
        Get the module name from the given path.

        :param cls: The full class name.
        :type cls: str

        :return: The module name.
        :rtype: str

        :raises ValueError: When the class name is invalid.
        """

        if not Exportable.CLASS_PATTERN.match(cls):
            raise ValueError(f"Invalid class name {cls}")

        path = Exportable.CLASS_PATTERN.findall(cls)[0]

        """
        If the path is an alias, replace it with the proper package name.
        """
        for alias in Exportable.ALIASES:
            if path.startswith(alias):
                path = path.replace(alias, Exportable.ALIASES[alias])

        path = path.split('.')

        return '.'.join(path[:-1])

    @staticmethod
    def get_class(cls):
        """
        Get the class name from the given path.

        :param cls: The full class name.
        :type cls: str

        :return: The class name.
        :rtype: str

        :raises ValueError: When the class name is invalid.
        """

        if not Exportable.CLASS_PATTERN.match(cls):
            raise ValueError(f"Invalid class name {cls}")

        path = Exportable.CLASS_PATTERN.findall(cls)[0].split('.')
        return path[-1]

    def __hash__(self):
        """
        Create an immutable hash of the Exportable instance.
        The function converts the object to an array, creates a JSON representation of it, and then hashes the string.

        :return: An intenger representation of the Exportable instance.
        :rtype: int
        """

        if not Exportable.unoptimized_hashing:
            logger.warning(f"Hashing { type(self) } with unoptimized function. Further warnings suppressed.")
            Exportable.unoptimized_hashing = True

        return hash(json.dumps(self.to_array()))
