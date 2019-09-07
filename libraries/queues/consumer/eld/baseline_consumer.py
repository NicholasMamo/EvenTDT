"""
A simple consumer that takes in tweets every time window.
It clusters these documents and finds the most important terms in each cluster.
"""

import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '../../../../')
if path not in sys.path:
	sys.path.insert(1, path)

from ..buffered_consumer import BufferedConsumer
from ..buffered_consumer import PseudoBufferedConsumer

from ..filter import filter
from ..filter.filter import Filter

from libraries.vector.cluster.algorithms.nokmeans import NoKMeans, ClusterType
from libraries.vector.nlp.document import Document
from libraries.vector.nlp.tokenizer import Tokenizer

from libraries.logger import logger

from datetime import datetime

import asyncio

logger.set_logging_level(logger.LogLevel.INFO)

class BaselineConsumer(PseudoBufferedConsumer):
	"""
	The BaselineConsumer class is the simlest implementation in ELD, with the bare necessities.
	It was developed as the Minimum Viable Product (MVP) for ELD.
	"""

	def _filter(self, tweets):
		"""
		Filter the given tweets based on a simple rule - only retain English tweets.

		:param tweets: A list of tweets.
		:type tweets: list of dictionaries

		:return: A list of filtered tweets.
		:type tweets: list of dictionaries
		"""

		rules = [
			("lang", filter.equal, "en"),
		]
		f = Filter(rules)
		return [tweet for tweet in tweets if f.filter(tweet)]

	def _tokenize(self, tweets):
		"""
		Tokenize the given list of tweets.

		:param tweets: A list of tweets.
		:type tweets: list of dictionaries

		:return: A list of filtered tweets.
		:rtype: list of :class:`vector.nlp.document.Document` instances
		"""

		t = Tokenizer()
		documents = []
		for tweet in tweets:
			document = Document(t.tokenize(tweet.get("text", "")))
			document.set_attribute("text", tweet.get("text", ""))
			document.set_attribute("original", tweet)
			document.normalize()
			documents.append(document)

		return documents

	def _cluster(self, documents):
		"""
		Cluster the given documents.

		:param documents: A list of documents.
		:rtype documents: list of :class:`vector.nlp.document.Document`

		:return: A list of all the clusters from the clustering approach.
			This includes those that are frozen.
		:rtype: list of :class:`vector.cluster.cluster.Cluster` instances
		"""

		clustering = NoKMeans()
		clustering.cluster(documents, threshold=0.5, freeze_period=50)
		return clustering.get_clusters(ClusterType.ALL)

	async def _process(self):
		"""
		Find breaking terms - as a baseline - from the stream of tweets.

		:return: A list of topics, represented with tweets that represent breaking topics.
		:rtype: list of tweets
		"""

		topics = []
		total_documents, total_tweets = 0, 0

		while not self._stopped:
			if self._buffer.length() > 0:
				"""
				The first step is to filter out non-English tweets and tokenize the rest
				"""
				tweets = self._buffer.dequeue_all()
				total_tweets += len(tweets)
				tweets = self._filter(tweets)
				documents = self._tokenize(tweets)
				total_documents += len(documents)

				logger.info("%d tweets in %d seconds" % (len(documents), self._periodicity))

				"""
				Then, cluster the documents
				"""
				clusters = self._cluster(documents)
				for i, cluster in enumerate(clusters):
					if (cluster.size() > 10):
						topics.append(cluster.get_vectors()[0].get_attribute("text"))
						# print("\t", cluster.get_vectors()[0].get_attribute("text"))


			await self._sleep()

		if self._buffer.length() > 0:
			tweets = self._buffer.dequeue_all()
			total_tweets += len(tweets)
			tweets = self._filter(tweets)
			documents = self._tokenize(tweets)
			total_documents += len(documents)

			logger.info("%d tweets flushed" % (self._buffer.length()))

		logger.info("%d tweets viewed and %d documents processed" % (total_tweets, total_documents))
		return topics
