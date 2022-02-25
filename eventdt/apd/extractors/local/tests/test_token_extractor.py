"""
Test the functionality of the token extractor.
"""

import json
import os
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nltk.corpus import stopwords

from apd.extractors.local.token_extractor import TokenExtractor

from nlp.document import Document
from nlp.tokenizer import Tokenizer
import twitter

def ignore_warnings(test):
    """
    A decorator function used to ignore NLTK warnings
    From: http://www.neuraldump.net/2017/06/how-to-suppress-python-unittest-warnings/
    More about decorator functions: https://wiki.python.org/moin/PythonDecorators

    :param test: The test to perform.
    :type test: func

    :return: The function output.
    :rtype: obj
    """
    def perform_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            test(self, *args, **kwargs)
    return perform_test

class TestExtractors(unittest.TestCase):
    """
    Test the implementation and results of the token extractor.
    """

    @ignore_warnings
    def test_token_extractor_no_tokenizer(self):
        """
        Test that the token extractor without a tokenizer simply splits the text.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')

        extractor = TokenExtractor()
        candidates = extractor.extract(path)
        self.assertEqual(['Bayern', 'Munich', 'make', 'second', 'bid', 'worth',
                          'more', 'than', '£20m', 'for', '18-year-old',
                          'Chelsea', 'forward', 'Callum', 'Hudson-Odoi'], candidates[0])

    @ignore_warnings
    def test_empty_corpus(self):
        """
        Test the token extractor with an empty corpus.
        """

        extractor = TokenExtractor()
        candidates = extractor.extract(os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json'))
        self.assertFalse(len(candidates))

    @ignore_warnings
    def test_return_length(self):
        """
        Test that the token extractor returns as many token sets as the number of documents given.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')

        extractor = TokenExtractor()
        candidates = extractor.extract(path)
        self.assertEqual(100, len(candidates))

    @ignore_warnings
    def test_extract_with_custom_tokenizer(self):
        """
        Test that when a custom tokenizer is given, it is used instead of splitting the text.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')

        # create the extractor with a tokenizer that removes stopwords and applies stemming
        extractor = TokenExtractor(tokenizer=Tokenizer(stopwords=stopwords.words('english'), stem=True))
        candidates = extractor.extract(path)
        self.assertEqual(['bayern', 'munich', 'make', 'second', 'bid',
                          'worth', '£20m', 'year', 'old', 'chelsea',
                          'forward', 'callum', 'hudson', 'odoi'], candidates[0])

    @ignore_warnings
    def test_extract_full_text(self):
        """
        Test that the extractor uses the full text.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')

        extractor = TokenExtractor()
        candidates = extractor.extract(path)
        self.assertTrue(all( '…' not in tokens for tokens in candidates ))
        self.assertTrue(all( '…' not in token for tokens in candidates for token in tokens ))

    @ignore_warnings
    def test_extract_expands_mentions(self):
        """
        Test that the extractor expands mentions.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')

        extractor = TokenExtractor()
        candidates = extractor.extract(path)
        self.assertTrue(all( '@' not in tokens or 'bet' in tokens for tokens in candidates ))
        self.assertTrue(all( '@' not in token or 'bet' in tokens or 'Stream' in tokens for tokens in candidates for token in tokens ))

    @ignore_warnings
    def test_repeated_tokens(self):
        """
        Test that when no tokenizer is given, repeated tokens may appear multiple times.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')

        extractor = TokenExtractor()
        candidates = extractor.extract(path)
        self.assertEqual(2, candidates[1].count('Eden'))

    @ignore_warnings
    def test_repeated_tokens_with_custom_tokenizer(self):
        """
        Test that when a custom tokenizer is given, repeated tokens may appear multiple times.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')

        tokenizer = Tokenizer(stopwords=stopwords.words("english"), stem=False)
        extractor = TokenExtractor(tokenizer=tokenizer)
        candidates = extractor.extract(path)
        self.assertEqual(2, candidates[1].count('eden'))
