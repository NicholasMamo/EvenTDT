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
from eventdt.modeling import EventModel
from eventdt.modeling.modelers import UnderstandingModeler
from tools import consume
from tools import concepts as clusters
from tools import participants as apd

class TestModel(unittest.TestCase):
    """
    Test the functionality of the model tool.
    """

    def test_create_modeler_same_type(self):
        """
        Test that creating a modeler instantiates the correct type.
        """

        self.assertEqual(UnderstandingModeler, type(model.create_modeler(UnderstandingModeler)))

    def test_create_modeler_with_participants(self):
        """
        Test that creating a modeler stores the participants.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', "participants.json")
        participants = apd.load(file)

        modeler = model.create_modeler(UnderstandingModeler, participants=participants)
        self.assertEqual(len(participants), len(modeler.participants))
        self.assertEqual(modeler._preprocess_participants(participants).keys(), modeler.participants.keys())

    def test_create_modeler_with_concepts(self):
        """
        Test that creating a modeler stores the concepts.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "concepts.json")
        concepts = clusters.load(file)

        modeler = model.create_modeler(UnderstandingModeler, concepts=concepts)
        self.assertEqual(len(concepts), len(modeler.concepts))
        self.assertEqual(concepts, modeler.concepts)

    def test_create_modeler_with_NER(self):
        """
        Test that creating a modeler stores the NER preference.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "concepts.json")
        concepts = clusters.load(file)

        modeler = model.create_modeler(UnderstandingModeler, with_ner=True)
        self.assertTrue(modeler.with_ner)

    def test_create_modeler_without_NER(self):
        """
        Test that creating a modeler stores the NER preference.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "concepts.json")
        concepts = clusters.load(file)

        modeler = model.create_modeler(UnderstandingModeler, with_ner=False)
        self.assertFalse(modeler.with_ner)

    def test_model_returns_list_of_models(self):
        """
        Test that modeling a timeline returns a list of event models.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', "#ParmaMilan-simplified.json")

        modeler = model.create_modeler(UnderstandingModeler)
        models = model.model(modeler, [ file ])
        self.assertEqual(list, type(models))
        self.assertTrue(all( EventModel.__name__ == type(model).__name__ for model in models ))

    def test_model_one_timeline(self):
        """
        Test that modeling a timeline creates one event model per timeline node.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', "#ParmaMilan-simplified.json")

        modeler = model.create_modeler(UnderstandingModeler)
        models = model.model(modeler, [ file ])
        self.assertEqual(len([ node for timeline in consume.load(file)
                                    for node in timeline.nodes ]), len(models))

    def test_model_multiple_timelines(self):
        """
        Test that modeling multiple timelines creates one event model per node per timeline.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', "#ParmaMilan-simplified.json") ] * 2

        modeler = model.create_modeler(UnderstandingModeler)
        models = model.model(modeler, files)
        self.assertEqual(len([ node for file in files
                                    for timeline in consume.load(file)
                                    for node in timeline.nodes ]),
                         len(models))
