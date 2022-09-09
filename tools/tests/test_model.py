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
from eventdt.objects import Exportable
from tools import consume
from tools import concepts as clusters
from tools import participants as apd

class TestModel(unittest.TestCase):
    """
    Test the functionality of the model tool.
    """

    def test_is_own_models(self):
        """
        Test that checking whether an output was produced by this tool returns true when given its own output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'models', "#ParmaMilan.json")
        with open(file) as f:
            output = [ Exportable.decode(json.loads(line)) for line in f ]
            self.assertTrue(model.is_own(output))

    def test_is_own_other(self):
        """
        Test that checking whether an output was produced by this tool returns false when given another tool's output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', "bootstrapped.json")
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            self.assertFalse(model.is_own(output))

    def test_is_own_txt(self):
        """
        Test that checking whether an output was produced by this tool returns false when given a text file.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "gold.txt")
        self.assertFalse(model.is_own(file))

    def test_is_own_models_path(self):
        """
        Test that checking whether an output was produced by this tool returns true when given a path to a file containing its own output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'models', "#ParmaMilan.json")
        self.assertTrue(model.is_own(file))

    def test_is_own_other_path(self):
        """
        Test that checking whether an output was produced by this tool returns false when given a path to a file containing another tool's output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', "bootstrapped.json")
        self.assertFalse(model.is_own(file))

    def test_is_own_returns_bool(self):
        """
        Test that checking whether an output was produced by this tool returns a boolean.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', "bootstrapped.json")
        self.assertEqual(bool, type(model.is_own(file)))

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'models', "#ParmaMilan.json")
        self.assertEqual(bool, type(model.is_own(file)))

    def test_load_from_output(self):
        """
        Test that when loading models from the output of the tool, they are loaded correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'models', '#ParmaMilan.json')
        with open(file) as f:
            output = [ json.loads(line) for line in f ]
            models = model.load(output)
            original = [ Exportable.decode(line) for line in output ]
        self.assertEqual(Exportable.encode(original), Exportable.encode(models)) # encode the pair again since they will be essentially-different objects

    def test_load_from_path(self):
        """
        Test that when loading models from a filepath, they are loaded correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'models', '#ParmaMilan.json')
        with open(file) as f:
            original = [ Exportable.decode(json.loads(line)) for line in f ]
        models = model.load(file)
        self.assertEqual(Exportable.encode(original), Exportable.encode(models)) # encode the pair again since they will be essentially-different objects

    def test_load_returns_list_of_models(self):
        """
        Test that when loading models from a filepath, the function returns a list of models.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'models', '#ParmaMilan.json')
        models = model.load(file)
        self.assertEqual(list, type(models))
        self.assertTrue(all( EventModel.__name__ == type(model).__name__ for model in models ))

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

        modeler = model.create_modeler(UnderstandingModeler, with_ner=True)
        self.assertTrue(modeler.with_ner)

    def test_create_modeler_without_NER(self):
        """
        Test that creating a modeler stores the NER preference.
        """

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

    def test_model_stream_override_false(self):
        """
        Test that when modeling timelines without overriding the What, certain models can have multiple What.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', "#ParmaMilan-simplified.json")

        concepts = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "concepts.json")
        concepts = clusters.load(concepts)
        modeler = model.create_modeler(UnderstandingModeler, concepts=concepts)

        models = model.model(modeler, [ file ], stream_override=False)
        self.assertTrue(any( len(model.what) > 1 for model in models ))

    def test_model_stream_override_false_all(self):
        """
        Test that when modeling timelines without overriding the What, all event models have, at least, one What (in case of a streamed timeline).
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', "#ParmaMilan-simplified.json")

        concepts = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "concepts.json")
        concepts = clusters.load(concepts)
        modeler = model.create_modeler(UnderstandingModeler, concepts=concepts)

        models = model.model(modeler, [ file ], stream_override=False)
        self.assertTrue(all( model.what for model in models ))

    def test_model_stream_override_true_returns_list_of_list(self):
        """
        Test that when modeling timelines and overriding the What, the models' what are returned as a list of list.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', "#ParmaMilan-simplified.json")

        concepts = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "concepts.json")
        concepts = clusters.load(concepts)
        modeler = model.create_modeler(UnderstandingModeler, concepts=concepts)

        models = model.model(modeler, [ file ], stream_override=False)
        self.assertTrue(all( list is type(model.what) for model in models ))
        self.assertTrue(all( list is type(concept) for model in models for concept in model.what ))

    def test_model_stream_override_all(self):
        """
        Test that when modeling timelines and overriding the What, all models have exactly one topic.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', "#ParmaMilan-simplified.json")

        concepts = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "concepts.json")
        concepts = clusters.load(concepts)
        modeler = model.create_modeler(UnderstandingModeler, concepts=concepts)

        models = model.model(modeler, [ file ], stream_override=True)
        self.assertTrue(all( model.what for model in models ))

    def test_model_stream_override_true_returns_list_of_list(self):
        """
        Test that when modeling timelines and overriding the What, the models' what are returned as a list of list.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', "#ParmaMilan-simplified.json")

        concepts = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "concepts.json")
        concepts = clusters.load(concepts)
        modeler = model.create_modeler(UnderstandingModeler, concepts=concepts)

        models = model.model(modeler, [ file ], stream_override=True)
        self.assertTrue(all( list is type(model.what) for model in models ))
        self.assertTrue(all( list is type(concept) for model in models for concept in model.what ))

    def test_model_stream_override_true(self):
        """
        Test that when modeling timelines and overriding the What, the event models are aligned with each timeline's topic.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', "#ParmaMilan-simplified.json")

        concepts = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "concepts.json")
        concepts = clusters.load(concepts)
        modeler = model.create_modeler(UnderstandingModeler, concepts=concepts)

        models = model.model(modeler, [ file ], stream_override=True)
        splits = [ [ split ] for split, timeline in zip(consume.load_splits(file), consume.load(file))
                             for node in timeline.nodes ]
        what = [ model.what for model in models ]
        self.assertEqual(splits, what)

    def test_model_stream_override_true_subset(self):
        """
        Test that when modeling timelines and overriding the What, the event models' What is a subset of the original (non-overriden) event models' What. 
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', "#ParmaMilan-simplified.json")

        concepts = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "concepts.json")
        concepts = clusters.load(concepts)
        modeler = model.create_modeler(UnderstandingModeler, concepts=concepts)

        original = model.model(modeler, [ file ], stream_override=False)
        original_what = [ json.dumps(sorted(model.what)) for model in original ]

        override = model.model(modeler, [ file ], stream_override=True)
        override_what = [ json.dumps(sorted(model.what)) for model in override ]

        self.assertTrue(all( a[0] in b or 'EXCLUDED' in a[0]
                             for a, b in zip(override_what, original_what) ))