"""
Test the functionality of the base extrapolator.
"""

import copy
import os
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from apd.extrapolators.extrapolator import Extrapolator

class TestExtrapolator(unittest.TestCase):
    """
    Test the implementation and results of the Extrapolator.
    """

    def test_extrapolator_returns_dict(self):
        """
        Test that the extrapolator returns a dictionary.
        """

        extrapolator = Extrapolator()
        self.assertEqual(dict, type(extrapolator.extrapolate({ })))

    def test_extrapolator_returns_empty(self):
        """
        Test that the base extrapolator returns no new participants.
        """

        extrapolator = Extrapolator()
        self.assertFalse(extrapolator.extrapolate({ }))
