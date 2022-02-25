"""
Test the functionality of the TwitterNER entity extractor.
"""

import json
import os
import re
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from apd.extractors.local.twitterner_entity_extractor import TwitterNEREntityExtractor
from nlp.document import Document
from nlp.tokenizer import Tokenizer
import twitter

class TestTwitterNERExtractor(unittest.TestCase):
    """
    Test the functionality of the TwitterNER entity extractor.
    """

    def test_ner_extractor(self):
        """
        Test that the NER extractor is available even before creating the TwitterNEREntityExtractor.
        """

        self.assertTrue(TwitterNEREntityExtractor.ner)

    def test_init_ner_extractor(self):
        """
        Test that when creating a TwitterNER entity extractor, the existing NER extractor is already available.
        """

        self.assertTrue(TwitterNEREntityExtractor.ner)

    def test_extract_example(self):
        """
        Test extracting the entities using the example tweet from the GitHub repository.
        """

        extractor = TwitterNEREntityExtractor()
        candidates = extractor.extract("Beautiful day in Chicago! Nice to get away from the Florida heat.")
        self.assertEqual([ 'chicago', 'florida' ], candidates[0])

    def test_extract(self):
        """
        Test the entity extractor with normal input.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TwitterNEREntityExtractor()
        candidates = extractor.extract(path)
        self.assertEqual([ 'bayern munich', 'chelsea' ], candidates[0])
        self.assertEqual([ 'eden', 'maurizio sarri' ], candidates[1])

    def test_extract_empty_corpus(self):
        """
        Test that when extracting the entities from an empty corpus, an empty list is returned.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        extractor = TwitterNEREntityExtractor()
        self.assertFalse(extractor.extract(path))

    def test_extract_return_length(self):
        """
        Test that the TwitterNER entity extractor returns as many candidate sets as the number of documents given.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TwitterNEREntityExtractor()
        candidates = extractor.extract(path)
        self.assertEqual(100, len(candidates))

    def test_extract_named_entity_at_start(self):
        """
        Test that the TwitterNER entity extractor is capable of extracting named entities at the start of a sentence.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TwitterNEREntityExtractor()
        candidates = extractor.extract(path)

        corpus = [ ]
        with open(path) as f:
            for i, line in enumerate(f):
                tweet = json.loads(line)
                text = twitter.full_text(tweet)
                text = twitter.expand_mentions(text, tweet)
                corpus.append(text)

        self.assertTrue(any( text.lower().startswith(entity) for entities, text in zip(candidates, corpus) for entity in entities ))

    def test_extract_named_entity_at_end(self):
        """
        Test that the TwitterNER entity extractor is capable of extracting named entities at the end of a sentence.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TwitterNEREntityExtractor()
        candidates = extractor.extract(path)

        corpus = [ ]
        with open(path) as f:
            for i, line in enumerate(f):
                tweet = json.loads(line)
                text = twitter.full_text(tweet)
                text = twitter.expand_mentions(text, tweet)
                corpus.append(text)

        self.assertTrue(any( text.lower().startswith(entity) for entities, text in zip(candidates, corpus) for entity in entities ))

    def test_extract_multiple_sentences(self):
        """
        Test that the TwitterNER entity extractor is capable of extracting named entities from multiple sentences.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TwitterNEREntityExtractor()
        candidates = extractor.extract(path)
        # It would be fine in terms of numbers if Sarri had just used Moses, Ampadu and Hudson-Odoi in the Europa League and Carabao Cup. Treatment of Moses, a viable and experienced squad player, is self-defeating. Hudson-Odoi is likely to leave now. Very sad waste.
        self.assertEqual(2, candidates[2].count('moses'))

    def test_extract_repeated_named_entities(self):
        """
        Test that the TwitterNER entity extractor does not filter named entities that appear multiple times.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TwitterNEREntityExtractor()
        candidates = extractor.extract(path)
        self.assertEqual(2, candidates[2].count('moses'))

    def test_extract_multiword_entities(self):
        """
        Test that the TwitterNER entity extractor is capable of extracting multi-word entities.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TwitterNEREntityExtractor()
        candidates = extractor.extract(path)
        self.assertEqual([ 'bayern munich', 'chelsea' ], candidates[0])
        self.assertEqual([ 'eden', 'maurizio sarri' ], candidates[1])

    def test_extract_comma_separated_entities(self):
        """
        Test that comma-separated named entities are returned individually.
        """

        extractor = TwitterNEREntityExtractor()
        candidates = extractor.extract("Memphis Depay, Leo Dubois, Martin Terrier and Karl Toko Ekambi all out injured")
        self.assertEqual([ "memphis depay", 'leo dubois', 'martin terrier', 'karl toko ekambi' ], candidates[0])

    def test_extract_order(self):
        """
        Test that the named entities are returned in the correct order.
        """

        extractor = TwitterNEREntityExtractor()
        candidates = extractor.extract("Memphis Depay, Leo Dubois, Martin Terrier and Karl Toko Ekambi all out injured")
        self.assertEqual([ "memphis depay", 'leo dubois', 'martin terrier', 'karl toko ekambi' ], candidates[0])

    def test_extract_from_text(self):
        """
        Test that TwitterNER's named entities do appear in the corresponding tweet.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        extractor = TwitterNEREntityExtractor()
        candidates = extractor.extract(path)
        with open(path) as f:
            for i, line in enumerate(f):
                tweet = json.loads(line)
                text = twitter.full_text(tweet)
                text = twitter.expand_mentions(text, tweet)

                self.assertTrue(all( candidate in text.lower() or '\n' in text for candidate in candidates[i] ))
