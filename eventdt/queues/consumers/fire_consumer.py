"""
A simple consumer that takes in tweets every time window, clusters them and finds the most important terms in each cluster.
"""

import os
import sys

from nltk.corpus import stopwords

path = os.path.dirname(__file__)
path = os.path.join(path, '../../../../')
if path not in sys.path:
	sys.path.insert(1, path)

from ..buffered_consumer import BufferedConsumer
from ..buffered_consumer import PseudoBufferedConsumer

from ..filter import filter
from ..filter.filter import Filter

from libraries.vector.cluster.algorithms.nokmeans import TemporalNoKMeans, ClusterType
from libraries.vector.nlp.document import Document
from libraries.vector.nlp.tokenizer import Tokenizer

from libraries.logger import logger

from libraries.topic_detection.algorithms import cataldi
from libraries.topic_detection.nutrition_store.memory_nutrition_store import MemoryNutritionStore

from libraries.vector.nlp.term_weighting import TF, TFIDF
from libraries.vector import vector_math

from datetime import datetime

import asyncio
import math

logger.set_logging_level(logger.LogLevel.INFO)

class FIREConsumer(PseudoBufferedConsumer):
	"""
	The FireConsumer class is based on FIRE: Finding Important News REports (Mamo et al., 2018).
	"""

	def __init__(self, queue, periodicity, idf=None):
		"""
		Create the consumer with a queue.
		Simultaneously create a nutrition store and the topic detection algorithm container.
		Initially, the IDF table should be empty.
		It will be populated later when the 'reconaissance' period is finished.

		:param queue: The queue that is consumed.
		:type queue: :class:`~queues.queue.Queue`
		:param periodicity: The time (in seconds) to spend consuming the queue.
		:type periodicity: int
		:param filter_words: The words to filter out of documents.
		:type filter_words: list
		:param idf: The IDF table to use in the term-weighting scheme.
		:type idf: dict
		"""
		super(FIREConsumer, self).__init__(queue, periodicity)
		self._nutrition_store = MemoryNutritionStore()
		self._term_weighting = TFIDF(idf)

	def _filter_tweets(self, tweets):
		"""
		Filter the given tweets based on FIRE's filtering rules.

		:param tweets: A list of tweets.
		:type tweets: list of dictionaries

		:return: A list of filtered tweets.
		:type tweets: list of dictionaries
		"""

		for tweet in tweets:
			"""
			Calculate some scores that are not provided by Twitter's API
			"""
			tweet["num_hashtags"] = len(tweet["entities"]["hashtags"])
			tweet["follower_per_thousand_tweets"] = tweet["user"]["followers_count"] / tweet["user"]["statuses_count"]

		rules = [
			("lang", filter.equal, "en"),
			("num_hashtags", filter.lte, 2),
			("user:favourites_count", filter.gt, 0),
			("follower_per_thousand_tweets", filter.gte, 1./1000.)
		]
		f = Filter(rules)
		return [tweet for tweet in tweets if f.filter(tweet)]

	def _filter_documents(self, documents):
		"""
		Filter the given documents based on FIRE's filtering rules.

		:param documets: The documents to filter.
		:type documents: list of :class:`~vector.nlp.document.Document` instances

		:return: The approved documents.
		:type documents: list of :class:`~vector.nlp.document.Document` instances
		"""

		for document in documents:
			tokens = document.get_attribute("tokens")
			token_count, unique_token_count = len(tokens), len(set(tokens))
			document.set_attribute("score", math.log(token_count) * unique_token_count / token_count if token_count > 0 else 0)

		rules = [
			("score", filter.gte, 1.37)
		]
		f = Filter(rules)
		return [document for document in documents if f.filter(document.get_attributes())]

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
			tokens = tokenizer.tokenize(tweet.get("text", ""))

			document = Document(tweet.get("text", ""), tokens, scheme=self._term_weighting)
			document.set_attribute("tokens", tokens)
			document.set_attribute("timestamp", timestamp)
			document.set_attribute("tweet", tweet)

			document.set_attribute("text", tweet.get("text", ""))
			if "retweeted_status" in tweet and "quoted_status" not in tweet:
				document.set_attribute("text", tweet["retweeted_status"].get("extended_tweet", {}).get("full_text", tweet.get("text")))

			document.normalize()
			documents.append(document)

		return documents

	def _cluster(self, documents, threshold=0.7, freeze_period=20):
		"""
		Cluster the given documents.

		:param documets: The documents to cluster.
		:type documents: list of :class:`~vector.nlp.document.Document` instances
		:param threshold: The threshold to use for the incremental clustering approach.
		:type threshold: float
		:param freeze_period: The freeze period (in seconds) of the incremental clustering approach.
		:type freeze_period: float

		:return: The list of clusters that are still active and that have changed.
		:rtype: list of :class:`~vector.cluster.cluster.Cluster` instances
		"""

		clustering = TemporalNoKMeans()
		clusters = clustering.cluster(documents, threshold=threshold, freeze_period=freeze_period, time_attribute="timestamp", store_frozen=False)
		return clusters

	async def _create_checkpoint(self, timestamp, sets, document_set):
		"""
		After every time window has elapsed, create a checkpoint from the documents.
		These documents are used to create a nutrition set for the nutrition store.
		This nutrition set represents a snapshot of the time window.

		:param timestamp: The timestamp of the new checkpoint.
		:type timestamp: int
		:param sets: The number of time windows that are considered.
			Older ones serve no purpose, so they may be removed.
		:type timestamp: int
		:param document_set: The list of documents that form the checkpoint.
		:type document_set: list
		"""

		"""
		Concatenate all the documents in the buffer and normalize the dimensions
		The goal is to get a list of dimensions in the range 0 to 1
		"""

		if len(document_set) > 0:
			"""
			Concatenate all the documents in the buffer and normalize the dimensions
			The goal is to get a list of dimensions in the range 0 to 1
			"""

			single_document = vector_math.concatenate(document_set)
			self._nutrition_store.add_nutrition_set(timestamp, single_document.get_dimensions())
		elif timestamp is not None:
			self._nutrition_store.add_nutrition_set(timestamp, {})
			logger.info("Checkpoint passed internally with 0 documents")

		if timestamp is not None:
			self._nutrition_store.remove_old_nutrition_sets(timestamp - self._periodicity * (sets + 1)) # keep an extra one, just in case

	def _detect_topics(self, cluster, sets, timestamp):
		"""
		Perform topic detection.

		:param cluster: The cluster from which to extract the documents.
		:type cluster: :class:`~vector.cluster.cluster.Cluster`
		:param sets: The number of time windows to consider.
		:type sets: int
		:param timestamp: The current timestamp, used to isolate recent documents.
		:type timestamp: int

		:return: A list of emerging terms from the cluster.
		:rtype: list
		"""

		terms = cataldi.detect_topics(self._nutrition_store, # use the nutrition store's checkpoints as historical data
			timestamp=timestamp, # do not consider checkpoints in this sliding time window, but only those that preceed it
			sets=sets, # consider the past few sets
		)
		return terms

	async def _process(self):
		"""
		Find breaking terms from the stream of tweets.

		:return: A list of topics, represented with tweets that represent breaking topics.
		:rtype: list of tweets
		"""

		sets = 10
		topics = []
		total_documents, total_tweets = 0, 0

		while not self._stopped:
			if self._buffer.length() > 0:
				"""
				The first step is to filter out non-English tweets and tokenize the rest
				"""
				tweets = self._buffer.dequeue_all()
				total_tweets += len(tweets)
				tweets = self._filter_tweets(tweets)
				documents = self._tokenize(tweets)
				# documents = self._filter_documents(documents)
				total_documents += len(documents)
				last_timestamp = documents[-1].get_attribute("timestamp")

				await self._create_checkpoint(last_timestamp, sets, documents)

				"""
				Then, cluster the documents
				"""
				clusters = self._cluster(documents)
				# clusters = self._filter_clusters(clusters, last_timestamp, min_size=2, max_intra_similarity=0.9)
				for cluster in clusters:
					"""
					Perform topic detection
					"""
					if cluster.size() > 3:
						terms = self._detect_topics(cluster, sets=sets, timestamp=last_timestamp)
						if len(terms) > 0:
							logger.info("%s: %s" % (datetime.fromtimestamp(last_timestamp).strftime('%Y-%m-%d %H:%M:%S'), ', '.join(terms)))

			await self._sleep()

		logger.info("%d tweets viewed and %d documents processed" % (total_tweets, total_documents))
		return topics
