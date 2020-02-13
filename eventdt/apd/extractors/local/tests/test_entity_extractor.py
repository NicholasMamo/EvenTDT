"""
Test the functionality of the entity extractor.
"""

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

class TestExtractors(unittest.TestCase):
	"""
	Test the implementation and results of the different extractors.
	"""

	def test_entity_extractor(self):
		"""
		Test the entity extractor with normal input.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"Liverpool falter against Tottenham Hotspur",
			"Mourinho under pressure as Tottenham follow with a loss",
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = EntityExtractor()
		candidates = extractor.extract(corpus)
		self.assertEqual(set([ "liverpool", "tottenham hotspur" ]), set(candidates[0]))
		self.assertEqual(set([ "mourinho", "tottenham" ]), set(candidates[1]))

	def test_empty_corpus(self):
		"""
		Test the entity extractor with an empty corpus.
		"""

		extractor = EntityExtractor()
		candidates = extractor.extract([ ])
		self.assertFalse(len(candidates))

	def test_return_length(self):
		"""
		Test that the entity extractor returns as many token sets as the number of documents given.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"Liverpool falter against Tottenham Hotspur",
			"",
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = EntityExtractor()
		candidates = extractor.extract(corpus)
		self.assertEqual(2, len(candidates))
		self.assertEqual(set([ "liverpool", "tottenham hotspur" ]), set(candidates[0]))
		self.assertEqual(set([ ]), set(candidates[1]))

	def test_named_entity_at_start(self):
		"""
		Test that the entity extractor is capable of extracting named entities at the start of a sentence.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"Liverpool falter again",
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = EntityExtractor()
		candidates = extractor.extract(corpus)
		self.assertTrue("liverpool" in set(candidates[0]))

	def test_named_entity_at_end(self):
		"""
		Test that the entity extractor is capable of extracting named entities at the end of a sentence.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"Spiral continues for Lyon",
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = EntityExtractor()
		candidates = extractor.extract(corpus)
		self.assertTrue("lyon" in set(candidates[0]))

	def test_multiple_sentences(self):
		"""
		Test that the entity extractor is capable of extracting named entities from multiple sentences.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"The downward spiral continues for Lyon. Bruno Genesio under threat.",
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = EntityExtractor()
		candidates = extractor.extract(corpus)
		self.assertEqual(set([ "lyon", "bruno genesio" ]), set(candidates[0]))

	def test_repeated_named_entities(self):
		"""
		Test that the entity extractor does not filter named entities that appear multiple times.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"The downward spiral continues for Lyon. Lyon coach Bruno Genesio under threat.",
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = EntityExtractor()
		candidates = extractor.extract(corpus)
		self.assertEqual(set([ "lyon", "bruno genesio" ]), set(candidates[0]))

	def test_binary_named_entities(self):
		"""
		Test that the entity extractor does not consider the entity type when the binary option is turned off.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"The downward spiral continues for Lyon. Rudi Garcia under threat.",
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = EntityExtractor()
		candidates = extractor.extract(corpus, binary=False)
		self.assertEqual(set([ "lyon", "rudi", "garcia" ]), set(candidates[0])) # 'Rudi' and 'Garcia' mistakenly have different types

		candidates = extractor.extract(corpus, binary=True)
		self.assertEqual(set([ "lyon", "rudi garcia" ]), set(candidates[0]))

	def test_comma_separated_entities(self):
		"""
		Test that comma-separated named entities are returned individually.
		"""

		"""
		Create the test data.
		"""
		tokenizer = Tokenizer(stem=False)
		posts = [
			"Memphis Depay, Oumar Solet, Leo Dubois and Youssouf Kone all out injured",
		]
		corpus = [ Document(post, tokenizer.tokenize(post)) for post in posts ]

		extractor = EntityExtractor()
		candidates = extractor.extract(corpus)
		self.assertEqual(set([ "memphis depay", "oumar solet", 'leo dubois', 'youssouf kone' ]), set(candidates[0]))
