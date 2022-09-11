"""
Test the functionality of the package functions.
"""

from datetime import datetime
import json
import os
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from modeling import EventModel
from modeling.modelers import *
from summarization.timeline import Timeline

class TestPackage(unittest.TestCase):
    """
    Test the functionality of the package functions.
    """

    def test_model_returns_all_nodes(self):
        """
        Test that the event modeler returns one event model for each node in a timeline.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'), 'r') as f:
            timeline = Timeline.from_array(json.loads(''.join(f.readlines()))['timeline'])
            modeler = DummyEventModeler()
            self.assertEqual(len(timeline.nodes), len(modeler.model(timeline)))

    def test_model_returns_event_models(self):
        """
        Test that the event modeler returns a list of event models.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'), 'r') as f:
            timeline = Timeline.from_array(json.loads(''.join(f.readlines()))['timeline'])
            modeler = DummyEventModeler()
            self.assertEqual(list, type(modeler.model(timeline)))
            self.assertTrue(all( EventModel == type(model) for model in modeler.model(timeline) ))

    def test_model_stores_node_id(self):
        """
        Test that the event modeler stores a node_id alongside each event models.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', '#ParmaMilan-attributes.json'), 'r') as f:
            data = json.loads(''.join(f.readlines()))['timeline']
            timelines = [ Timeline.from_array(datum) for datum in data ]
            for timeline in timelines:
                ids = [ node.attributes.get('id') for node in timeline.nodes ]
                modeler = DummyEventModeler()
                node_ids = [ model.attributes.get('node_id') for model in modeler.model(timeline) ]
                self.assertTrue(any( ids ))
                self.assertEqual(ids, node_ids)
