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
from summarization.timeline import Timeline
from summarization.timeline.nodes import DocumentNode

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
	:ivar documents: The documents that can still be used for summarization.
					 Older documents are automatically cleared.
	:vartype documents: :class:`~nlp.document.Document`
	:ivar tdt: The TDT algorithm: Zhao et al.'s implementation.
	:vartype tdt: :class:`~tdt.algorithms.zhao.Zhao`
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
		self.documents = { }
		self.tdt = Zhao(self.store)

	async def _process(self):
		"""
		Find breaking develpoments based on changes in volume.

		:return: The constructed timeline.
		:rtype: :class:`~summarization.timeline.Timeline`
		"""

		timeline = Timeline(DocumentNode, 0, 1)

		while not self.stopped:
			"""
			If there are tweets in the buffer, dequeue them and convert them into documents.
			"""
			if self.buffer.length() > 0:
				tweets = self.buffer.dequeue_all()
				documents = self._to_documents(tweets)
				latest_timestamp = self._latest_timestamp(documents)

				"""
				Add the received documents to the document list.
				Then remove old documents that are not needed anymore.
				Zhao et al. limit the dynamic window to 60 seconds.
				Therefore only documents from the past 30 seconds can be relevant.
				"""
				self._add_documents(documents)
				self.documents = self._documents_since(latest_timestamp - 30)

				"""
				Create checkpoints from the received documents.
				"""
				self._create_checkpoint(documents)

				"""
				Detect topics from the stream.
				"""
				window = self._detect_topics(latest_timestamp)
				if window:
					start, end = window
					timeline.add(timestamp, self._documents_since(start))

			await self._sleep()

		return timeline

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

	def _latest_timestamp(self, documents):
		"""
		Get the latest timestamp from the given documents.

		:param documents: The list of documents from where to get the latest timestamp.
		:type documents: list of :class:`~nlp.document.Document`

		:return: The latest timestamp in the given document set.
		:rtype: int

		:raises ValueError: When there are no documents to consider.
		"""

		timestamps = [ document.attributes['timestamp'] for document in documents ]
		return max(timestamps)

	def _add_documents(self, documents):
		"""
		Add the given documents to the list of stored documents.

		:param documents: The list of documents to store in this consumer.
		:type documents: list of :class:`~nlp.document.Document`
		"""

		for document in documents:
			timestamp = document.attributes['timestamp']
			self.documents[timestamp] = self.documents.get(timestamp, [ ])
			self.documents[timestamp].append(document)

	def _documents_since(self, since):
		"""
		Get all the documents since the given timestamp.
		The documents are ordered chronologically.

		:param since: The timestamp since when all documents should be returned.
						  This value is inclusive.
		:type since: float

		:return: The list of documents added since the given timestamp.
		:rtype: list of :class:`~nlp.document.Document`
		"""

		documents = [ ]

		timestamps = [ timestamp for timestamp in self.documents if timestamp >= since ]
		for timestamp in sorted(timestamps):
			documents.extend(self.documents[timestamp])

		return documents

	def _create_checkpoint(self, documents):
		"""
		Create checkpoints from the documents in the
		After every time window has elapsed, create a checkpoint from the documents.
		These documents are used to create a nutrition set for the nutrition store.
		This nutrition set represents a snapshot of the time window.

		:param documents: The list of documents that form the checkpoint.
		:type documents: list of :class:`~nlp.document.Document`
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
		Detect breaking topics using the Zhao et al. algorithm.

		:param timestamp: The timestamp at which point topics are detected.
						  This value is exclusive.
		:type timestamp: float

		:return: A tuple with the start and end timestamp of the time window when there was a burst.
				 Note that this is a half-window, not the entire window.
				 If there was an increase in the second half of the last 60 seconds, the last 30 seconds are returned.
				 If there was no burst, `False` is returned.
		:rtype: tuple or bool
		"""

		return self.tdt.detect(timestamp)
