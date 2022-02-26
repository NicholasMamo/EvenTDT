"""
Test the functionality of the NER participant detector.
"""

import os
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
           os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from logger import logger
from ner_participant_detector import NERParticipantDetector
from nlp.document import Document
from nlp.tokenizer import Tokenizer

logger.set_logging_level(logger.LogLevel.WARNING)

class TestNERParticipantDetector(unittest.TestCase):
    """
    Test the implementation and results of the NER participant detector.
    """

    def test_extract_named_entities(self):
        """
        Test extracting named entities.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        detector = NERParticipantDetector()
        _, _, _, resolved, _, _ = detector.detect(corpus=path)

        self.assertTrue('chelsea' in resolved)

    def test_named_entity_sorting(self):
        """
        Test that the named entities are sorted in descending order of their frequency.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        detector = NERParticipantDetector()
        _, scored, _, resolved, _, _ = detector.detect(corpus=path)

        self.assertTrue(all( scored[list(resolved.keys())[i]] >= scored[list(resolved.keys())[i + 1]]
                             for i in range(len(resolved) - 1) ))
