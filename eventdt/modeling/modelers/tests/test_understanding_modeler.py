"""
Test the functionality of the :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler` class.
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

from attributes.extractors import LinguisticExtractor
from attributes import Profile
from modeling import EventModel
from modeling.modelers import UnderstandingModeler
from nlp import Document
from summarization.timeline import Timeline
from summarization.timeline.nodes import DocumentNode

class TestUnderstandingModeler(unittest.TestCase):
    """
    Test the functionality of the :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler` class.
    """

    def mock_participants(self):
        """
        Create a list of mock participants that represent the Who and the Where.

        :return: A dictionary with the participant names as keys and the profiles as values.
        :rtype: dict
        """

        corpus = {
            "Max Verstappen": "Max Emilian Verstappen (born 30 September 1997) is a Belgian-Dutch racing driver and the 2021 Formula One World Champion.",
            "Pierre Gasly": "Pierre Gasly (French pronunciation: ​[pjɛʁ ɡasli]; born 7 February 1996) is a French racing driver, currently competing in Formula One under the French flag, racing for Scuderia AlphaTauri.",
            "Lance Stroll": "Lance Strulovitch,[2] (born 29 October 1998) better known as Lance Stroll, is a Canadian-Belgian[3] racing driver competing under the Canadian flag in Formula One.",
            "George Russell (racing driver)": "George William Russell (/rʌsəl/; born 15 February 1998) is a British racing driver currently competing in Formula One for Mercedes.",
            "Circuit Gilles Villeneuve": "The Circuit Gilles Villeneuve (also spelled Circuit Gilles-Villeneuve in French) is a 4.361 km (2.710 mi) motor racing circuit in Montreal, Quebec, Canada.",
            "Montreal": "Montreal (/ˌmʌntriˈɔːl/ (listen) MUN-tree-AWL; officially Montréal, French: [mɔ̃ʁeal] (listen)) is the second-most populous city in Canada and most populous city in the Canadian province of Quebec.",
        }

        extractor = LinguisticExtractor()
        return { name: extractor.extract(text, name=name) for name, text in corpus.items() }

    def test_init_saves_participants(self):
        """
        Test that on initialization, the class saves the participants if given.
        """

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        for participant, copy in zip(participants.values(), modeler.participants.values()):
            self.assertEqual(participant.attributes, copy.attributes)

    def test_init_saves_participants_as_dicts(self):
        """
        Test that on initialization, the class saves the participants as dictionaries if given.
        """

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        self.assertEqual(dict, type(modeler.participants))

    def test_init_preprocesses_participants(self):
        """
        Test that on initialization, the class pre-processes the participants if given.
        """

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        self.assertTrue(any( '(' in participant.name and not '(' in copy.name
                             for participant, copy in zip(participants.values(), modeler.participants.values()) ))

    def test_init_copies_participants(self):
        """
        Test that on initialization, the class makes a copy of the participants if given.
        """

        participants = self.mock_participants()
        participant = participants['Max Verstappen']
        original = participant.copy()

        modeler = UnderstandingModeler(participants=participants.values())
        copy = modeler.participants['Max Verstappen']

        copy.attributes['test'] = { True }
        self.assertFalse('test' in participant.attributes)

        participant.attributes['test'] = { False }
        self.assertTrue(copy.test)

    def test_who_returns_list(self):
        """
        Test that the Who returns a list of profiles.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual(list, type(models))
        self.assertTrue(all( list == type(model.who) for model in models ))
        self.assertTrue(all( Profile == type(profile) for model in models for profile in model.who ))

    def test_who_matches_participants(self):
        """
        Test that the Who correctly identifies participants in the text.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ participants['Max Verstappen'].name },
                         { participant.name for participant in models[0].who })

    def test_who_count_participants(self):
        """
        Test that the Who correctly identifies participants in the text.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix."),
            Document(text="Max Verstappen wins the first Grand Prix of the season."),
            Document(text="France's Pierre Gasly finishes second despite slow start."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ participants['Max Verstappen'].name },
                         { participant.name for participant in models[0].who })

    def test_who_unrecognized_participants(self):
        """
        Test that if no participant matches the Who, the function returns an empty list.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Yuki Tsunoda wins the Grand Prix.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].who)

    def test_who_threshold_inclusive(self):
        """
        Test that the Who's 50% threshold is inclusive.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix."),
            Document(text="The Dutch wins the first Grand Prix of the season.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual(participants['Max Verstappen'].name, models[0].who[0].name)

    def test_who_repeated_participant(self):
        """
        Test that if a participant appears multiple times in one document, it is only counted once.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Max Verstappen's done it! Max Verstappen wins the Grand Prix."),
            Document(text="The Dutch wins the first Grand Prix of the season."),
            Document(text="The inaugural Grand Prix is over, and it goes Dutch.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].who)

    def test_who_multiple(self):
        """
        Test that a model's Who may have several participants.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix, Pierre Gasly the runner-up."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ participants['Max Verstappen'].name, participants['Pierre Gasly'].name },
                         { participant.name for participant in models[0].who })

    def test_when_uses_created_at(self):
        """
        Test that extracting the When simply uses the node's `created_at` attribute.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ ]))

        modeler = UnderstandingModeler()
        models = modeler.model(timeline)
        self.assertTrue(all( model.when[0] == node.created_at for model, node in zip(models, timeline.nodes) ))
