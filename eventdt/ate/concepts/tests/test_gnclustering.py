"""
Test the functionality of the :class:`~ate.concepts.gnclustering.GNClustering` class.
"""

import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate.concepts import DummyTermClusteringAlgorithm

class TestGNClustering(unittest.TestCase):
    """
    Test the functionality of the :class:`~ate.concepts.gnclustering.GNClustering` class.
    """

    pass
