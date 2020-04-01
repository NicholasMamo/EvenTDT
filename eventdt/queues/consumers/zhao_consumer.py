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

import twitter

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

	def __init__(self, queue, periodicity=5, timestamp='timestamp', scheme=None):
		"""
		Create the consumer with a queue.
		Simultaneously create a nutrition store and the topic detection algorithm container.
		Initially, the IDF table should be empty.
		It will be populated later when the 'reconaissance' period is finished.

		:param queue: The queue that is consumed.
		:type queue: :class:`~queues.queue.Queue`
		:param periodicity: The time window in seconds of the buffered consumer, or how often it is invoked.
							This defaults to 5 seconds, the same span as half the smallest time window in Zhao et al.'s algorithm.
		:type periodicity: int
		:param timestamp: The name of the vector attribute used to get the timestamp value.
						  The time value is expected to be a float or integer.
		:type timestamp: str
		:param scheme: The term-weighting scheme that is used to create dimensions.
					   If `None` is given, the :class:`~nlp.term_weighting.TermWeighting.TF` term-weighting scheme is used.
		:type scheme: None or :class:`~nlp.term_weighting.TermWeighting`
		"""

		super(ZhaoConsumer, self).__init__(queue, periodicity, timestamp=timestamp)
		self.scheme = scheme
		self.store = MemoryNutritionStore()

	def _to_documents(self, tweets):
		"""
		Convert the given tweets into documents.

		:param tweets: A list of tweets.
		:type tweets: list of dict

		:return: A list of documents created from the tweets in the same order as the given tweets.
				 Documents are normalized and store the original tweet in the `tweet` attribute.
		:rtype: list of :class:`~nlp.document.Document`
		"""

		documents = [ ]

		"""
		The text used for the document depend on what kind of tweet it is.
		If the tweet is too long to fit in the tweet, the full text is used;

		Retain the comment of a quoted status.
		However, if the tweet is a plain retweet, get the full text.
		"""
		tokenizer = Tokenizer(stopwords=stopwords.words("english"), remove_unicode_entities=True)
		for tweet in tweets:
			original = tweet
			while "retweeted_status" in tweet:
				tweet = original["retweeted_status"]

			if "extended_tweet" in tweet:
				text = tweet["extended_tweet"].get("full_text", tweet.get("text", ""))
			else:
				text = tweet.get("text", "")

			"""
			Create the document and save the tweet in it.
			"""
			tokens = tokenizer.tokenize(text)
			document = Document(text, tokens, scheme=self.scheme)
			document.attributes["tweet"] = original
			document.attributes[self.timestamp] = twitter.extract_timestamp(original)
			document.normalize()
			documents.append(document)

		return documents

	async def _create_checkpoint(self, documents):
		"""
		Create checkpoints from the documents in the
		After every time window has elapsed, create a checkpoint from the documents.
		These documents are used to create a nutrition set for the nutrition store.
		This nutrition set represents a snapshot of the time window.

		:param documents: The list of documents that form the checkpoint.
		:type documents: list
		"""

		if len(documents) > 0:
			"""
			Concatenate all the documents in the buffer and normalize the dimensions
			The goal is to get a list of dimensions in the range 0 to 1
			"""

			"""
			Count the volume at each second.
			"""
			volume = { }
			for document in documents:
				timestamp = document.attributes[self.timestamp]
				volume[timestamp] = volume.get(timestamp, 0) + 1

			"""
			Retrieve the volume counts, if there are any, for the given timestamps.
			Only the volume at a given second is saved.
			"""
			for timestamp, count in volume.items():
				self.store.add(timestamp, (self.store.get(timestamp) or 0) + (count or 0))

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
