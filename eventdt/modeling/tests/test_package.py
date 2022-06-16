"""
Test the functionality of the package functions.
"""

from datetime import datetime
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

    def test_event_model_copy(self):
        """
        Test that copying the event model includes all attributes.
        """

        model = EventModel(who='Truman', what='speech', where='Maryland',
                           when=datetime(1947, 6, 29), attributes={ 'version': 1 })

        copy = model.copy()
        self.assertEqual(model.who, copy.who)
        self.assertEqual(model.what, copy.what)
        self.assertEqual(model.where, copy.where)
        self.assertEqual(model.when, copy.when)
        self.assertEqual(model.why, copy.why)
        self.assertEqual(model.how, copy.how)

    def test_event_model_copy_attributes(self):
        """
        Test that the attributes are also copied.
        """

        model = EventModel(who='Truman', what='speech', where='Maryland',
                           when=datetime(1947, 6, 29), attributes={ 'version': 1 })
        copy = model.copy()
        self.assertEqual(model.attributes, copy.attributes)

    def test_event_model_copy_attributes_original(self):
        """
        Test that changing the copy's attributes does not affect the original's, and vice-versa.
        """

        model = EventModel(who='Truman', what='speech', where='Maryland',
                           when=datetime(1947, 6, 29), attributes={ 'version': 1 })
        copy = model.copy()

        copy.attributes['who'] = 'Harry Truman'
        self.assertEqual('Harry Truman', copy.who)
        self.assertEqual('Truman', model.who)

        model.attributes['who'] = 'Harry S. Truman'
        self.assertEqual('Harry Truman', copy.who)
        self.assertEqual('Harry S. Truman', model.who)

    def test_event_model_copy_nested_attributes_original(self):
        """
        Test that changing the copy's nested attributes does not affect the original's, and vice-versa.
        """

        model = EventModel(who='Truman', what='speech', where='Maryland',
                           when=datetime(1947, 6, 29), attributes={ 'version': { 'library': 'EvenTDT', 'version': 1 } })
        copy = model.copy()

        copy.attributes['version']['version'] = 2
        self.assertEqual(2, copy.version['version'])
        self.assertEqual(1, model.version['version'])

        model.attributes['version']['version'] = 2.2
        self.assertEqual(2, copy.version['version'])
        self.assertEqual(2.2, model.version['version'])

    def test_event_model_export(self):
        """
        Test exporting and importing an event model.
        """

        model = EventModel(who='Truman', what='speech', where='Maryland',
                           when=datetime(1947, 6, 29), attributes={ 'version': { 'library': 'EvenTDT', 'version': 1 } })
        exported = model.to_array()

        self.assertEqual(model.attributes, EventModel.from_array(exported).attributes)
        self.assertEqual(model.__dict__, EventModel.from_array(exported).__dict__)

    def test_event_model_export_attributes(self):
        """
        Test that exporting and importing event models includes attributes.
        """

        model = EventModel(who='Truman', what='speech', where='Maryland',
                           when=datetime(1947, 6, 29), attributes={ 'version': { 'library': 'EvenTDT', 'version': 1 } })
        exported = model.to_array()

        self.assertEqual(model.attributes, EventModel.from_array(exported).attributes)
        self.assertEqual(model.__dict__, EventModel.from_array(exported).__dict__)
