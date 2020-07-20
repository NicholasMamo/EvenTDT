"""
Test the functionality of the TwitterNER entity extractor.
"""

import os
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from apd.extractors.local.twitterner_entity_extractor import TwitterNEREntityExtractor

from nlp.document import Document
from nlp.tokenizer import Tokenizer

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
