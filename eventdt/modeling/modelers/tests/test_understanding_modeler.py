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
from modeling import EventModel
from modeling.modelers import UnderstandingModeler
from summarization.timeline import Timeline
from summarization.timeline.nodes import DocumentNode

class TestUnderstandingModeler(unittest.TestCase):
    """
    Test the functionality of the :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler` class.
    """

    def mock_participants(self):
        """
        Create a list of mock participants that represent the Who and the Where.
        """

        corpus = [
            "Max Emilian Verstappen (born 30 September 1997) is a Belgian-Dutch racing driver and the 2021 Formula One World Champion.",
            "Pierre Gasly (French pronunciation: ​[pjɛʁ ɡasli]; born 7 February 1996) is a French racing driver, currently competing in Formula One under the French flag, racing for Scuderia AlphaTauri.",
            "Lance Strulovitch,[2] (born 29 October 1998) better known as Lance Stroll, is a Canadian-Belgian[3] racing driver competing under the Canadian flag in Formula One.",
            "The Circuit Gilles Villeneuve (also spelled Circuit Gilles-Villeneuve in French) is a 4.361 km (2.710 mi) motor racing circuit in Montreal, Quebec, Canada.",
            "Montreal (/ˌmʌntriˈɔːl/ (listen) MUN-tree-AWL; officially Montréal, French: [mɔ̃ʁeal] (listen)) is the second-most populous city in Canada and most populous city in the Canadian province of Quebec.",
        ]

        extractor = LinguisticExtractor()
        return [ extractor.extract(text) for text in corpus ]

    def test_init_saves_participants(self):
        """
        Test that on initialization, the class saves the participants if given.
        """

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants)
        self.assertEqual(participants, modeler.participants)

    def test_when_uses_created_at(self):
        """
        Test that extracting the When simply uses the node's `created_at` attribute.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ ]))

        modeler = UnderstandingModeler()
        models = modeler.model(timeline)
        self.assertTrue(all( model.when[0] == node.created_at for model, node in zip(models, timeline.nodes) ))
