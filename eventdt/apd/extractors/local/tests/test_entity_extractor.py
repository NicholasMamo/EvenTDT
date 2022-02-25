"""
Test the functionality of the entity extractor.
"""

import json
import os
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from apd.extractors.local.entity_extractor import EntityExtractor
from nlp.document import Document
from nlp.tokenizer import Tokenizer
import twitter

class TestExtractors(unittest.TestCase):
    """
    Test the implementation and results of the different extractors.
    """

    def test_entity_extractor(self):
        """
        Test the entity extractor with normal input.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')

        extractor = EntityExtractor()
        candidates = extractor.extract(path)
        self.assertEqual([ "Bayern Munich", "Chelsea", "Callum" ], candidates[0])
        self.assertEqual([ "Eden", "Maurizio Sarri", "CRYCHE" ], candidates[1])

    def test_empty_corpus(self):
        """
        Test the entity extractor with an empty corpus.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        extractor = EntityExtractor()
        candidates = extractor.extract(path)
        self.assertFalse(len(candidates))

    def test_return_length(self):
        """
        Test that the entity extractor returns as many token sets as the number of documents given.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = EntityExtractor()
        candidates = extractor.extract(path)
        self.assertEqual(100, len(candidates))

    def test_named_entity_at_start(self):
        """
        Test that the entity extractor is capable of extracting named entities at the start of a sentence.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = EntityExtractor()
        candidates = extractor.extract(path)

        corpus = [ ]
        with open(path) as f:
            for i, line in enumerate(f):
                tweet = json.loads(line)
                text = twitter.full_text(tweet)
                text = twitter.expand_mentions(text, tweet)
                corpus.append(text)

        self.assertTrue(any( text.startswith(entity) for entities, text in zip(candidates, corpus) for entity in entities ))

    def test_named_entity_at_end(self):
        """
        Test that the entity extractor is capable of extracting named entities at the end of a sentence.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = EntityExtractor()
        candidates = extractor.extract(path)

        corpus = [ ]
        with open(path) as f:
            for i, line in enumerate(f):
                tweet = json.loads(line)
                text = twitter.full_text(tweet)
                text = twitter.expand_mentions(text, tweet)
                corpus.append(text)

        self.assertTrue(any( text.endswith(entity) for entities, text in zip(candidates, corpus) for entity in entities ))

    def test_multiple_sentences(self):
        """
        Test that the entity extractor is capable of extracting named entities from multiple sentences.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = EntityExtractor()
        candidates = extractor.extract(path)
        self.assertEqual([ "Bayern Munich", "Chelsea", "Callum" ], candidates[0])

    def test_repeated_named_entities(self):
        """
        Test that the entity extractor does not filter named entities that appear multiple times.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = EntityExtractor(binary=False)
        candidates = extractor.extract(path)
        self.assertEqual(2, candidates[1].count('Eden'))

    def test_binary_named_entities(self):
        """
        Test that the entity extractor does not consider the entity type when the binary option is turned off.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')

        extractor = EntityExtractor(binary=False)
        candidates = extractor.extract(path)
        self.assertEqual([ "Bayern", "Munich", "Chelsea", "Callum" ], candidates[0]) # Bayern and Munich have different types

        extractor = EntityExtractor(binary=True)
        candidates = extractor.extract(path)
        self.assertEqual([ "Bayern Munich", "Chelsea", "Callum" ], candidates[0]) # Bayern and Munich have different types, but it doesn't matter here

    def test_comma_separated_entities(self):
        """
        Test that comma-separated named entities are returned individually.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = EntityExtractor()
        candidates = extractor.extract(path)
        self.assertEqual([ "Bayern Munich", "Chelsea", "Callum" ], candidates[0])

    def test_extract_from_text(self):
        """
        Test that the entity extractor's named entities do appear in the corresponding tweet.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')

        extractor = EntityExtractor()
        candidates = extractor.extract(path)
        with open(path) as f:
            for i, line in enumerate(f):
                tweet = json.loads(line)
                text = twitter.full_text(tweet)
                text = twitter.expand_mentions(text, tweet)

                self.assertTrue(all( candidate in text or '\n' in text for candidate in candidates[i] ))
