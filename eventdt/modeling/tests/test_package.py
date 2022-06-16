"""
Test the functionality of the package functions.
"""

import json
import os
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from modeling import *

class TestPackage(unittest.TestCase):
    """
    Test the functionality of the package functions.
    """

    def test_event_model_init_empty(self):
        """
        Test that by default, the event model still stores the `five Ws and one H`.
        """

        model = EventModel()
        self.assertEqual({ 'who', 'what', 'where', 'when', 'why', 'how' }, set(model.attributes.keys()))

    def test_event_model_init_with_attributes(self):
        """
        Test that the event model accepts additional attributes in additional to the `five Ws and one H`.
        """

        model = EventModel(attributes={ 'version': 1 })
        self.assertEqual({ 'version', 'who', 'what', 'where', 'when', 'why', 'how' }, set(model.attributes.keys()))

    def test_event_model_init_no_overwrite(self):
        """
        Test that the event model does not overwrite any attributes.
        """

        model = EventModel(who='Truman', attributes={ 'version': 1 })
        self.assertEqual('Truman', model.who)
        self.assertEqual(1, model.version)
