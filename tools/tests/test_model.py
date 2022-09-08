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
