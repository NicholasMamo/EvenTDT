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

from modeling import EventModel
from modeling.modelers import UnderstandingModeler
from summarization.timeline import Timeline
from summarization.timeline.nodes import DocumentNode

class TestUnderstandingModeler(unittest.TestCase):
    """
    Test the functionality of the :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler` class.
    """

    def test_when_uses_created_at(self):
        """
        Test that extracting the When simply uses the node's `created_at` attribute.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ ]))

        modeler = UnderstandingModeler()
        models = modeler.model(timeline)
        self.assertTrue(all( model.when[0] == node.created_at for model, node in zip(models, timeline.nodes) ))
