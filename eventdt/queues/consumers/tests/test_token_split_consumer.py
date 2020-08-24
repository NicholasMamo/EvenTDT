"""
Test the functionality of the token split consumer.
"""

import asyncio
import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
	sys.path.append(path)

from logger import logger
from nlp import Document, Tokenizer
from nlp.weighting import TF
from objects.exportable import Exportable
from queues import Queue
from queues.consumers.algorithms import ELDConsumer
from queues.consumers.token_split_consumer import TokenSplitConsumer
from vsm import vector_math

logger.set_logging_level(logger.LogLevel.WARNING)

class TestTokenSplitConsumer(unittest.TestCase):
	"""
	Test the implementation of the token split consumer.
	"""

	def async_test(f):
		def wrapper(*args, **kwargs):
			coro = asyncio.coroutine(f)
			future = coro(*args, **kwargs)
			loop = asyncio.get_event_loop()
			loop.run_until_complete(future)
		return wrapper

	def test_init_custom_tokenizer(self):
		"""
		Test that when creating the token split consumer with a custom tokenizer, it is used instead of the default one.
		"""

		splits = [ ('tackl'), ('goal') ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
		self.assertTrue(consumer.tokenizer.stem)
		tokenizer = Tokenizer(stem=False)
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, tokenizer=tokenizer)
		self.assertFalse(consumer.tokenizer.stem)

	def test_init_list_of_list_splits(self):
		"""
		Test that when providing a list of list for splits, they are unchanged.
		"""

		splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
		self.assertEqual(splits, consumer.splits)

	def test_init_list_of_tuple_splits(self):
		"""
		Test that when providing a list of tuples for splits, they are converted into lists.
		"""

		splits = [ ( 'yellow', 'card' ), ( 'foul', 'tackl' ) ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
		self.assertEqual([ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ], consumer.splits)

	def test_init_list_of_str_splits(self):
		"""
		Test that when providing a list of strings for splits, they are converted into lists.
		"""

		splits = [ 'yellow', 'card' ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
		self.assertEqual([ [ 'yellow' ], [ 'card' ] ], consumer.splits)

	def test_init_mixed_splits(self):
		"""
		Test that when providing a mix of splits, they are converted into lists.
		"""

		splits = [ 'book', [ 'yellow', 'card' ], ( 'foul', 'tackl' ) ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
		self.assertEqual([ [ 'book' ], [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ], consumer.splits)

	def test_init_consumer_splits(self):
		"""
		Test that the token split consumer creates as many consumers as the number of splits.
		"""

		splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
		self.assertEqual(2, len(consumer.splits))
		self.assertEqual(2, len(consumer.consumers))

	def test_init_default_scheme(self):
		"""
		Test that the default term-weighting scheme is TF.
		"""

		splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
		self.assertEqual(TF, type(consumer.scheme))

	def test_init_consumers_arguments(self):
		"""
		Test that when passing on extra arguments to the token split consumer, they are passed on to the consumer.
		"""

		splits = [ (0, 50), (50, 100) ]
		consumer = TokenSplitConsumer(Queue(), splits, ZhaoConsumer)
		self.assertTrue(all( 5 == _consumer.periodicity for _consumer in consumer.consumers ))

		consumer = TokenSplitConsumer(Queue(), splits, ZhaoConsumer, periodicity=10)
		self.assertTrue(all( 10 == _consumer.periodicity for _consumer in consumer.consumers ))

	def test_preprocess_creates_documents(self):
		"""
		Test that when pre-processing tweets, the function creates documents.
		"""

		splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
			for line in f:
				tweet = json.loads(line)
				self.assertEqual(Document, type(consumer._preprocess(tweet)))

	def test_preprocess_uses_scheme(self):
		"""
		Test that when pre-processing tweets, the function uses the term-weighting scheme.
		"""

		trivial = True

		"""
		Create the consumer with a TF-IDF scheme.
		"""
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
			idf = Exportable.decode(json.loads(f.readline()))['tfidf']

		"""
		Tokenize all of the tweets.
		Words like 'hazard' should have a greater weight than more common words, like 'goal'.
		"""
		splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, scheme=idf)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
			for line in f:
				document = consumer._preprocess(json.loads(line))
				if 'hazard' in document.dimensions and 'goal' in document.dimensions:
					trivial = False
					self.assertGreater(document.dimensions['hazard'], document.dimensions['goal'])

		if trivial:
			logger.warning("Trivial test")

	def test_preprocess_normalizes_documents(self):
		"""
		Test that when pre-processing tweets, the returned documents are normalized.
		"""

		"""
		Create the consumer with a TF-IDF scheme.
		"""
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
			idf = Exportable.decode(json.loads(f.readline()))['tfidf']

		"""
		Tokenize all of the tweets.
		Words like 'hazard' should have a greater weight than more common words, like 'goal'.
		"""
		splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, scheme=idf)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
			for line in f:
				document = consumer._preprocess(json.loads(line))
				self.assertEqual(1, round(vector_math.magnitude(document), 10))

	def test_preprocess_with_text(self):
		"""
		Test that when pre-processing tweets, the returned documents have non-empty text.
		"""

		"""
		Create the consumer with a TF-IDF scheme.
		"""
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
			idf = Exportable.decode(json.loads(f.readline()))['tfidf']

		"""
		Tokenize all of the tweets.
		Words like 'hazard' should have a greater weight than more common words, like 'goal'.
		"""
		splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, scheme=idf)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
			for line in f:
				document = consumer._preprocess(json.loads(line))
				self.assertTrue(document.text)

	def test_preprocess_with_full_text(self):
		"""
		Test that when pre-processing tweets, the returned documents use the full text.
		"""

		"""
		Create the consumer with a TF-IDF scheme.
		"""
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
			idf = Exportable.decode(json.loads(f.readline()))['tfidf']

		"""
		Tokenize all of the tweets.
		Words like 'hazard' should have a greater weight than more common words, like 'goal'.
		"""
		splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, scheme=idf)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
			for line in f:
				document = consumer._preprocess(json.loads(line))
				self.assertFalse(document.text.endswith('…'))

	def test_preprocess_with_tweet(self):
		"""
		Test that when pre-processing tweets, the returned documents include the original tweet.
		"""

		"""
		Create the consumer with a TF-IDF scheme.
		"""
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
			idf = Exportable.decode(json.loads(f.readline()))['tfidf']

		"""
		Tokenize all of the tweets.
		Words like 'hazard' should have a greater weight than more common words, like 'goal'.
		"""
		splits = [ [ 'yellow', 'card' ], [ 'foul', 'tackl' ] ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, scheme=idf)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
			for line in f:
				tweet = json.loads(line)
				document = consumer._preprocess(tweet)
				self.assertEqual(tweet, document.attributes['tweet'])

	def test_satisfies_any(self):
		"""
		Test that when validating tweets using the ``any`` function, only one token needs to be in the document for it to be valid.
		"""

		trivial = True

		"""
		Create the consumer with a TF-IDF scheme.
		"""
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
			idf = Exportable.decode(json.loads(f.readline()))['tfidf']

		"""
		Tokenize all of the tweets.
		Words like 'hazard' should have a greater weight than more common words, like 'goal'.
		"""
		splits = [ [ 'chelsea', 'cfc' ] ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, matches=any, scheme=idf)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
			for line in f:
				"""
				If the document contains either of the tokens, it should succeed.
				Otherwise, the function should fail.
				"""
				document = consumer._preprocess(json.loads(line))
				if splits[0][0] in document.dimensions or splits[0][1] in document.dimensions:
					trivial = False
					self.assertTrue(consumer._satisfies(document, splits[0]))
				else:
					self.assertFalse(consumer._satisfies(document, splits[0]))

		if trivial:
			logger.warning("Trivial test")

	def test_satisfies_all(self):
		"""
		Test that when validating tweets using the ``all`` function, all tokens need to be in the document for it to be valid.
		"""

		trivial = True

		"""
		Create the consumer with a TF-IDF scheme.
		"""
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')) as f:
			idf = Exportable.decode(json.loads(f.readline()))['tfidf']

		"""
		Tokenize all of the tweets.
		Words like 'hazard' should have a greater weight than more common words, like 'goal'.
		"""
		splits = [ [ 'chelsea', 'cfc' ] ]
		consumer = TokenSplitConsumer(Queue(), splits, ELDConsumer, matches=all, scheme=idf)
		with open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'CRYCHE-500.json')) as f:
			for line in f:
				"""
				If the document contains both tokens, it should succeed.
				Otherwise, the function should fail.
				"""
				document = consumer._preprocess(json.loads(line))
				if splits[0][0] in document.dimensions and splits[0][1] in document.dimensions:
					trivial = False
					self.assertTrue(consumer._satisfies(document, splits[0]))
				else:
					self.assertFalse(consumer._satisfies(document, splits[0]))

		if trivial:
			logger.warning("Trivial test")
