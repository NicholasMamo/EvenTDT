"""
There is a wide variety of attribute extraction methods.
Therefore there is little common ground to create a generic extractor.
The basic idea of this class is that all extractors do something and extract attributes for one class or one instance at a time.
The functionality revolves around the :class:`~attributes.extractors.Extractor`'s :func:`~attributes.extractors.Extractor.extract` method.
"""

from abc import ABC, abstractmethod
import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '..', '..')
if path not in sys.path:
    sys.path.append(path)

from attributes.profile import Profile

class Extractor(ABC):
    """
    The :class:`~attributes.extractors.Extractor` is an abstract class that revolves around its :func:`~attributes.extractors.Extractor.extract` function.
    All it necessitates is that all extractors perform a task and ultimately return a :class:`~attributes.profile.Profile` with attributes.
    """

    @abstractmethod
    def extract(self, *args, **kwargs):
        """
        Extract attributes for a class or instance.
        Class or instance details are specified using arguments.
        At the end, the function returns a :class:`~attributes.profile.Profile`.

        :return: A profile of attributes for a class or an instance.
        :rtype: :class:`~attributes.profile.Profile`
        """

        pass
        
from .linguistic import LinguisticExtractor
