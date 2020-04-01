"""
The Zhao et al. consumer is based on the implementation by the same authors.
The algorithm revolves around the :class:`~tdt.algorithms.zhao.Zhao` algorithm.

.. note::

	Implementation based on the algorithm presented in `Human as Real-Time Sensors of Social and Physical Events: A Case Study of Twitter and Sports Games by Zhao et al. (2011) <https://arxiv.org/abs/1106.4300>`_.
"""

import asyncio
import math
import os
import sys
import time

from nltk.corpus import stopwords

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from .buffered_consumer import SimulatedBufferedConsumer

from nlp.document import Document
from nlp.tokenizer import Tokenizer

from logger import logger

from summarization.algorithms import MMR

from tdt.algorithms import Zhao
from tdt.nutrition import MemoryNutritionStore

class ZhaoConsumer(SimulatedBufferedConsumer):
	"""
	The Zhao et al. consumer is based on the implementation by the same authors.
	The algorithm revolves around the :class:`~tdt.algorithms.zhao.Zhao` algorithm.
	The algorithm examines changes in volume using a dynamic time window.

	:ivar store: The nutrition store used to store the volume.
	:vartype store: :class:`~tdt.nutrition.store.Store`
	:ivar scheme: The term-weighting scheme used to create documents.
	:vartype scheme: :class:`~nlp.term_weighting.TermWeighting`
	"""

	def __init__(self, queue, periodicity, timestamp='timestamp', scheme=None):
		"""
		Create the consumer with a queue.
		Simultaneously create a nutrition store and the topic detection algorithm container.
		Initially, the IDF table should be empty.
		It will be populated later when the 'reconaissance' period is finished.

		:param queue: The queue that is consumed.
		:type queue: :class:`~queues.queue.Queue`
		:param periodicity: The time window in seconds of the buffered consumer, or how often it is invoked.
		:type periodicity: int
		:param timestamp: The name of the vector attribute used to get the timestamp value.
						  The time value is expected to be a float or integer.
		:type timestamp: str
		:param scheme: The term-weighting scheme that is used to create dimensions.
					   If `None` is given, the :class:`~nlp.term_weighting.TermWeighting.TF` term-weighting scheme is used.
		:type scheme: None or :class:`~nlp.term_weighting.TermWeighting`
		"""

		super(ZhaoConsumer, self).__init__(queue, periodicity, timestamp=timestamp)
		self.store = MemoryNutritionStore()
		self.scheme = scheme

	def _tokenize(self, tweets):
		"""
		Tokenize the given list of tweets.

		:param tweets: A list of tweets.
		:type tweets: list of dictionaries

		:return: A list of filtered tweets.
		:rtype: list of :class:`~vector.nlp.document.Document` instances
		"""

		documents = []
		tokenizer = Tokenizer(stopwords=stopwords.words("english"), normalize_words=True, character_normalization_count=3, remove_unicode_entities=True)
		for tweet in tweets:
			timestamp_ms = int(tweet["timestamp_ms"])
			timestamp = int(timestamp_ms / 1000)

			"""
			Retain the comment of a quoted status.
			However, if the tweet is a plain retweet, get the full text.
			"""
			if "retweeted_status" in tweet and "quoted_status" not in tweet:
				text = tweet["retweeted_status"].get("extended_tweet", {}).get("full_text", tweet.get("text", ""))
			elif "extended_tweet" in tweet:
				text = tweet["extended_tweet"].get("full_text", tweet.get("text", ""))
			else:
				text = tweet.get("text", "")

			tokens = tokenizer.tokenize(text)
			document = Document(text, tokens, scheme=self.scheme)
			document.set_attribute("tokens", tokens)
			document.set_attribute("timestamp", timestamp)
			document.set_attribute("tweet", tweet)

			document.normalize()
			documents.append(document)

		return documents

	async def _create_checkpoint(self, timestamp, document_set):
		"""
		After every time window has elapsed, create a checkpoint from the documents.
		These documents are used to create a nutrition set for the nutrition store.
		This nutrition set represents a snapshot of the time window.

		:param timestamp: The timestamp of the new checkpoint.
		:type timestamp: int
		:param document_set: The list of documents that form the checkpoint.
		:type document_set: list
		"""

		if len(document_set) > 0:
			"""
			Concatenate all the documents in the buffer and normalize the dimensions
			The goal is to get a list of dimensions in the range 0 to 1
			"""

			"""
			Count the volume at each second.
			"""
			timestamp_counts = {}
			for document in document_set:
				timestamp = document.get_attribute("timestamp")
				timestamp_counts[timestamp] = timestamp_counts.get(timestamp, 0) + 1

			"""
			Retrieve the volume counts, if there are any, for the given timestamps.
			Only the volume at a given second is saved.
			"""
			for timestamp, count in timestamp_counts.items():
				volume = self.store.get_nutrition_set(timestamp)
				volume = 0 if volume is None else volume
				self.store.add_nutrition_set(timestamp, volume + count)

	def _detect_topics(self, timestamp):
		"""
		Perform topic detection.

		:param timestamp: The current timestamp, used to isolate recent documents.
		:type timestamp: int

		:return: A list of emerging terms from the cluster.
		:rtype: list
		"""

		(breaking, time_window) = zhao.detect_topics(self.store, # use the nutrition store's checkpoints as historical data
			timestamp=timestamp, # do not consider checkpoints in this sliding time window, but only those that preceed it
			post_rate=1.7
		)
		return (breaking, time_window)

	async def _process(self):
		"""
		Find breaking develpoments based on volume.

		:return: A list of topics, represented with tweets that represent breaking topics.
		:rtype: list of tweets
		"""

		raw_timeline = {}
		timeline = []
		document_set = {}
		last_timestamp = 0

		while not self._stopped:
			if self._buffer.length() > 0:
				"""
				The first step is to filter out non-English tweets and tokenize the rest
				"""
				tweets = self._buffer.dequeue_all()
				documents = self._tokenize(tweets)
				documents = sorted(documents, key=lambda document: document.get_attribute("timestamp"))
				last_timestamp = documents[-1].get_attribute("timestamp")

				"""
				Save the documents just in case they need to be used for summarization.
				"""
				for document in documents:
					timestamp = document.get_attribute("timestamp")
					document_set[timestamp] = document_set.get(timestamp, [])
					document_set[timestamp].append(document)

				"""
				Remove old documents.
				Zhao et al. limit the dynamic window to 60 seconds.
				If this window is used, then the past 30 seconds are relevant.
				"""
				document_set = { timestamp: historical_documents for timestamp, historical_documents in document_set.items() if last_timestamp - timestamp <= 30 }

				await self._create_checkpoint(last_timestamp, documents)

			breaking, time_window = self._detect_topics(last_timestamp)
			if breaking:
				timestamp = -1
				collection = [ document for timestamp in document_set.keys() for document in document_set.get(timestamp) if last_timestamp - timestamp <= time_window / 2. ]
				raw_timeline[last_timestamp] = collection

			await self._sleep()

		for timestamp, collection in sorted(raw_timeline.items(), key=lambda x: x[0]):
			summary = MMR(collection, timestamp=timestamp)
			logger.info("%s: %s" % (datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'), summary.generate_summary(tweet_cleaner.TweetCleaner)))
			timeline.append(summary)

		return timeline
