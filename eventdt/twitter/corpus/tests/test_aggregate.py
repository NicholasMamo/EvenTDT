"""
Test the functionality of the aggregation functions.
"""

import json
import os
import sys
import unittest

from datetime import datetime

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from nlp.tokenizer import Tokenizer
from twitter.corpus.aggregate import *
from vsm import vector_math
import twitter

class TestAggregate(unittest.TestCase):
	"""
	Test the functionality of the aggregation functions.
	"""

	def test_volume_empty_bin(self):
		"""
		Test that the volume of an empty bin is 0.
		"""

		self.assertEqual(0, volume([ ]))

	def test_volume_all(self):
		"""
		Test that the overall volume is the length of the bin.
		"""

		self.assertEqual(10, volume(range(0, 10)))

	def test_volume_track(self):
		"""
		Test that the volume of a tracked keyword looks in the document's dimensions.
		"""

		self.assertEqual(1, volume([ Document('a', { 'b': 1 }) ], track='b'))

	def test_volume_track_no_matches(self):
		"""
		Test that the volume of a tracked keyword returns 0 if there are no matches.
		"""

		self.assertEqual(0, volume([ Document('a', { 'b': 1 }) ], track='a'))

	def test_volume_track_matches(self):
		"""
		Test that the volume of a tracked keyword returns the number of matches.
		"""

		self.assertEqual(1, volume([ Document('a', { 'b': 1 }),
									 Document('a', { 'c': 1 }) ], track='b'))

	def test_to_documents_tweet(self):
		"""
		Test that when creating a document from a tweet, the tweet is saved as an attribute.
		"""

		tokenizer = Tokenizer()
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			tweet = json.loads(f.readline())
			document = to_documents([ tweet ], tokenizer)[0]
			self.assertEqual(tweet, document.attributes['tweet'])

	def test_to_documents_ellipsis(self):
		"""
		Test that when the text has an ellipsis, the full text is used.
		"""

		tokenizer = Tokenizer()
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				if '…' in tweet['text']:
					document = to_documents([ tweet ], tokenizer)[0]

					"""
					Make an exception for a special case.
					"""
					if not ('retweeted_status' in tweet and tweet['retweeted_status']['id_str'] == '1238513167573147648'):
						self.assertFalse(document.text.endswith('…'))

	def test_to_documents_quoted(self):
		"""
		Test that when the tweet is a quote, the text is used, not the quoted tweet's text.
		"""

		tokenizer = Tokenizer()
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				if 'retweeted_status' in tweet:
					timestamp = tweet['timestamp_ms']
					tweet = tweet['retweeted_status']
					tweet['timestamp_ms'] = timestamp

				if 'quoted_status' in tweet:
					document = to_documents([ tweet ], tokenizer)[0]

					if 'extended_tweet' in tweet:
						self.assertEqual(tweet["extended_tweet"].get("full_text", tweet.get("text", "")), document.text)
					else:
						self.assertEqual(tweet.get('text'), document.text)

	def test_to_documents_retweeted(self):
		"""
		Test that when the tweet is a quote, the retweet's text is used.
		"""

		tokenizer = Tokenizer()
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				if 'retweeted_status' in tweet:
					document = to_documents([ tweet ], tokenizer)[0]

					retweet = tweet['retweeted_status']
					if 'extended_tweet' in retweet:
						self.assertEqual(retweet["extended_tweet"].get("full_text", retweet.get("text", "")), document.text)
					else:
						self.assertEqual(retweet.get('text'), document.text)

					"""
					Tweets shouldn't start with 'RT'.
					"""
					self.assertFalse(document.text.startswith('RT'))

	def test_to_documents_normal(self):
		"""
		Test that when the tweet is not a quote or retweet, the full text is used.
		"""

		tokenizer = Tokenizer()
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				if not 'retweeted_status' in tweet and not 'quoted_status' in tweet:
					document = to_documents([ tweet ], tokenizer)[0]

					if 'extended_tweet' in tweet:
						self.assertEqual(tweet["extended_tweet"].get("full_text", tweet.get("text", "")), document.text)
					else:
						self.assertEqual(tweet.get('text'), document.text)

					"""
					There should be no ellipsis in the text now.
					"""
					self.assertFalse(document.text.endswith('…'))

	def test_to_documents_normalized(self):
		"""
		Test that the documents are returned normalized.
		"""

		tokenizer = Tokenizer()
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				document = to_documents([ tweet ], tokenizer)[0]
				self.assertEqual(1, round(vector_math.magnitude(document), 10))

	def test_to_documents_all(self):
		"""
		Test that when a list of documents are given, they are all converted to documents.
		"""

		tokenizer = Tokenizer()
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = to_documents(tweets, tokenizer)
			self.assertEqual(len(tweets), len(documents))

	def test_to_documents_order(self):
		"""
		Test that when a list of documents are given, the correct order is retained,
		This test checks that the tweets are assigned correctly.
		"""

		tokenizer = Tokenizer()
		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			documents = to_documents(tweets, tokenizer)
			for (tweet, document) in zip(tweets, documents):
				self.assertEqual(tweet, document.attributes['tweet'])

	def test_aggregate_timestamps(self):
		"""
		Test that when aggregating the corpus, the correct timestamps are processed.
		"""

		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			volume = aggregate(f, bin_size=1)

			f.seek(0)
			lines = f.readlines()
			tweets = [ json.loads(line) for line in lines ]
			timestamps = set([ twitter.extract_timestamp(tweet) for tweet in tweets ])
			self.assertEqual(timestamps, set(volume))

	def test_aggregate_count(self):
		"""
		Test that the total count of the aggregation is equivalent to the corpus length.
		"""

		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			volume = aggregate(f, bin_size=1)

			f.seek(0)
			lines = f.readlines()
			self.assertEqual(len(lines), sum([ volume[bin]['*'] for bin in volume ]))

	def test_aggregate_reverse_count(self):
		"""
		Test that when aggregating a reversed corpus, the correct count is still used.
		"""

		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			lines = reversed(f.readlines())
			volume = aggregate(lines, bin_size=1)

			f.seek(0)
			lines = f.readlines()
			self.assertEqual(len(lines), sum([ volume[bin]['*'] for bin in volume ]))

			tweets = [ json.loads(line) for line in lines ]
			timestamps = set([ twitter.extract_timestamp(tweet) for tweet in tweets ])
			self.assertEqual(timestamps, set(volume))

	def test_aggregate_track_keyword(self):
		"""
		Test that when tracking keywords, there is an entry for it at each timestamp.
		"""

		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			volume = aggregate(f, bin_size=1, track='coronaviru')

			self.assertTrue(all([ 'coronaviru' in volume[bin] for bin in volume ]))

	def test_aggregate_track_nonexistent_keyword(self):
		"""
		Test that when tracking keywords that do not exist in the corpus, they still have a volume of zero.
		"""

		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			volume = aggregate(f, bin_size=1, track='terrier')

			self.assertTrue(all([ 'terrier' in volume[bin] for bin in volume ]))
			self.assertEqual(0, sum([ volume[bin]['terrier'] for bin in volume ]))

	def test_aggregate_custom_tokenizer(self):
		"""
		Test that when a custom tokenizer is given, it is used.
		"""

		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			volume = aggregate(f, bin_size=1, track=[ 'coronaviru', 'coronavirus' ])

			self.assertTrue(all([ 'coronaviru' in volume[bin] for bin in volume ]))
			self.assertTrue(all([ volume[bin]['coronaviru'] > 0 for bin in volume ]))
			self.assertTrue(all([ volume[bin]['coronavirus'] == 0 for bin in volume ]))

			f.seek(0)
			tokenizer = Tokenizer(stem=False)
			volume = aggregate(f, bin_size=1, track=[ 'coronaviru', 'coronavirus' ], tokenizer=tokenizer)

			self.assertTrue(all([ 'coronaviru' in volume[bin] for bin in volume ]))
			self.assertTrue(all([ volume[bin]['coronaviru'] == 0 for bin in volume ]))
			self.assertTrue(all([ volume[bin]['coronavirus'] > 0 for bin in volume ]))

	def test_bin_size(self):
		"""
		Test that when setting the bin size, the tweets are segmented correctly.
		"""

		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			volume = aggregate(f, bin_size=5, track=[ 'coronaviru', 'coronavirus' ])
			self.assertEqual(3, len(volume))
			self.assertTrue(all(timestamp % 5 == 0 for timestamp in volume))

			for timestamp in volume:
				count = 0
				f.seek(0)
				for line in f.readlines():
					tweet = json.loads(line)
					time = twitter.extract_timestamp(tweet)
					if 0 <= time - timestamp < 5:
						count += 1
				self.assertEqual(count, volume[timestamp]['*'])
