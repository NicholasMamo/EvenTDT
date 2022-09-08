"""
Test the functionality of the model tool.
"""

import json
import os
import sys
import unittest

from datetime import datetime

paths = [ os.path.join(os.path.dirname(__file__), '..'),
           os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

import model
from eventdt.modeling.modelers import UnderstandingModeler

class TestModel(unittest.TestCase):
    """
    Test the functionality of the model tool.
    """

    def test_create_modeler_same_type(self):
        """
        Test that creating a modeler instantiates the correct type.
        """

        self.assertEqual(UnderstandingModeler, type(model.create_modeler(UnderstandingModeler)))