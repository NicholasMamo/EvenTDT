"""
Finding Important News REports (FIRE) is a periodic TDT consumer.
It takes in tweets every time window, clusters them and finds the most important terms in each cluster.
In this implementation, the tracking happens through the timeline.

.. note::

	Implementation based on the algorithm presented in `FIRE: Finding Important News REports by Mamo and Azzopardi (2017) <https://link.springer.com/chapter/10.1007/978-3-319-74497-1_3>`_.
"""

from datetime import datetime

import asyncio
import math
import os
import sys

from nltk.corpus import stopwords

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from .buffered_consumer import SimulatedBufferedConsumer

from vsm.clustering.algorithms import TemporalNoKMeans
from vsm import vector_math

from logger import logger

from nlp.document import Document
from nlp.term_weighting import TFIDF
from nlp.tokenizer import Tokenizer

from summarization.algorithms import MMR
from summarization.timeline import Timeline
from summarization.timeline.nodes import ClusterNode

from tdt.algorithms import Cataldi
from tdt.nutrition import MemoryNutritionStore

import twitter

class FIREConsumer(SimulatedBufferedConsumer):
	"""
	The FIRE consumer is based on the implementation of the same name.
	The algorithm clusters all tweets received in the same period and uses the Cataldi et al. algorithm to identify which ones are breaking.

	:ivar store: The nutrition store used to store the volume changes of individual terms.
	:vartype store: :class:`~tdt.nutrition.store.NutritionStore`
	:ivar scheme: The term-weighting scheme used to create documents.
	:vartype scheme: :class:`~nlp.term_weighting.scheme.TermWeightingScheme`
	:ivar sets: The number of time windows that are considered when computing burst.
				The higher this number, the more precise the calculations.
				However, because of the decay in :class:`~tdt.algorithms.cataldi.Cataldi`, old time windows do not affect the result by a big margin.
				Therefore old data can be removed safely.
	:vartype sets: int
	:ivar min_size: The minimum size for a cluster to be considered to be a candidate breaking topic.
					This value is inclusive.
	:vartype min_size: int
	:ivar tokenizer: The tokenizer used to create documents.
	:vartype tokenizer: :class:`~nlp.tokenizer.Tokenizer`
	:ivar clustering: The clustering algorithm to use.
	:vartype clustering: :class:`~vsm.clustering.algorithms.temporal_no_k_means.TemporalNoKMeans`
	:ivar summarization: The summarization algorithm to use.
	:vartype summarization: :class:`~summarization.algorithms.mmr.MMR`
	"""

	def __init__(self, queue, periodicity=60, scheme=None, sets=10, threshold=0.7, freeze_period=20, min_size=4):
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
		:param scheme: The term-weighting scheme that is used to create dimensions.
					   If `None` is given, the :class:`~nlp.term_weighting.tf.TF` term-weighting scheme is used.
		:type scheme: None or :class:`~nlp.term_weighting.scheme.TermWeightingScheme`
		:param sets: The number of time windows that are considered when computing burst.
					 The higher this number, the more precise the calculations.
					 However, because of the decay in :class:`~tdt.algorithms.cataldi.Cataldi`, old time windows do not affect the result by a big margin.
					 Therefore old data can be removed safely.
		:type sets: int
		:param threshold: The similarity threshold to use for the :class:`~vsm.clustering.algorithms.temporal_no_k_means.TemporalNoKMeans` incremental clustering approach.
						  Documents are added to an existing cluster if their similarity with the centroid is greater than or equal to this threshold.
		:type threshold: float
		:param freeze_period: The freeze period, in seconds, of the incremental clustering approach.
		:type freeze_period: float
		:param min_size: The minimum size for a cluster to be considered to be a candidate breaking topic.
						 This value is inclusive.
		:type min_size: int
		"""

		super(FIREConsumer, self).__init__(queue, periodicity)
		self.store = MemoryNutritionStore()
		self.scheme = scheme
		self.sets = sets
		self.min_size = min_size

		self.tokenizer = Tokenizer(stopwords=stopwords.words("english"), normalize_words=True,
								   character_normalization_count=3, remove_unicode_entities=True)
		self.clustering = TemporalNoKMeans(threshold, freeze_period, store_frozen=False)
		self.summarization = MMR()

	async def _process(self):
		"""
		Find breaking develpoments based on how people are talking.

		:return: The constructed timeline.
		:rtype: :class:`~summarization.timeline.timeline.Timeline`
		"""

		timeline = Timeline(ClusterNode, 0, 1)

		while not self.stopped:
			if self.buffer.length() > 0:
				"""
				If there are any tweets in the buffer, dequeue and filter them, and convert them into documents.
				"""
				tweets = self.buffer.dequeue_all()
				tweets = self._filter_tweets(tweets)
				documents = self._to_documents(tweets)
				latest_timestamp = self._latest_timestamp(documents)
				documents = self._filter_documents(documents)

				"""
				Create a checkpoint from the received documents.
				Then, remove old checkpoints and cluster the received documents.
				"""
				self._create_checkpoint(latest_timestamp, documents)
				self._remove_old_checkpoints(latest_timestamp)
				clusters = self._cluster(documents)

				"""
				Clusters are candidates if they have a minimum number of documents in them.
				For each such cluster, check if it has any bursty terms.
				If it does, the cluster is breaking.
				"""
				clusters = self._filter_clusters(clusters)
				for cluster in clusters:
					terms = self._detect_topics(cluster, timestamp=latest_timestamp)
					if terms:
						timeline.add(latest_timestamp, cluster)
						summary = self.summarization.summarize(timeline.nodes[-1].get_all_documents(), 140)
						logger.info(f"{datetime.fromtimestamp(latest_timestamp).ctime()}: { str(summary) }")

			await self._sleep()

		return timeline

	def _filter_tweets(self, tweets):
		"""
		Filter the given tweets based on FIRE's filtering rules.
		The rules are:

			#. The tweet has to be in English,

			#. The tweet must contain no more than 2 hashtags,

			#. The tweet's author must have favorited at least one tweet, and

			#. The tweet's author must have at least one follower for every thousand tweets they've published.

		:param tweets: A list of tweets to filter.
		:type tweets: list of dict

		:return: A list of filtered tweets.
		:type tweets: list of dict
		"""

		tweets = filter(lambda tweet: tweet['lang'] == 'en', tweets)
		tweets = filter(lambda tweet: len(tweet['entities']['hashtags']) <= 2, tweets)
		tweets = filter(lambda tweet: tweet['user']['favourites_count'] > 0, tweets)
		tweets = filter(lambda tweet: tweet['user']['followers_count'] / tweet['user']['statuses_count'] >= 1e-3, tweets)
		return list(tweets)

	def _to_documents(self, tweets):
		"""
		Convert the given tweets into documents.

		:param tweets: A list of tweets.
		:type tweets: list of dict

		:return: A list of documents created from the tweets in the same order as the given tweets.
				 Documents are normalized and store the original tweet in the `tweet` attribute.
		:rtype: list of :class:`~nlp.document.Document`
		"""

		documents = []

		"""
		The text used for the document depend on what kind of tweet it is.
		If the tweet is too long to fit in the tweet, the full text is used;

		Retain the comment of a quoted status.
		However, if the tweet is a plain retweet, get the full text.
		"""
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
			tokens = self.tokenizer.tokenize(text)
			document = Document(text, tokens, scheme=self.scheme)
			document.attributes['tweet'] = original
			document.attributes['timestamp'] = twitter.extract_timestamp(original)
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

	def _filter_documents(self, documents):
		"""
		Filter the given documents based on FIRE's scoring.
		The score is based on the fraction of unique tokens:

		.. math::

			s_d = \\ln(|d|) * \\frac{|d_u|}{|d|}

		where :math:`s_d` is the computed score.
		:math:`|d|` and :math:`|d_u|` are the number of tokens, and the number of unique tokens in the document respectively.
		Documents that have no tokens are immediately discarded.

		:param documets: A list of documents.
		:type documents: list of :class:`~nlp.document.Document`

		:return: A list of filtered documents.
		:type documents: list of :class:`~nlp.document.Document`
		"""

		filtered = [ ]

		for document in documents:
			tokens = self.tokenizer.tokenize(document.text)
			count, unique = len(tokens), len(set(tokens))

			"""
			If the document has no tokens, the score cannot be computed.
			Since it is low-quality, it is removed immediately.
			"""
			if not count:
				continue

			"""
			If the document does have tokens, compute the score.
			Low-quality documents are removed.
			"""
			score = math.log(count) * unique / count
			if score >= 1.37:
				filtered.append(document)

		return filtered

	def _create_checkpoint(self, timestamp, documents):
		"""
		After every time window has elapsed, create a checkpoint from the documents.
		These checkpoints store a snapshot of how much each different term was used at the time.

		:param timestamp: The timestamp of the new checkpoint.
		:type timestamp: int
		:param documents: The list of documents that form the checkpoint.
		:type documents: list of :class:`~nlp.document.Document`
		"""

		"""
		To create the checkpoint, concatenate all documents without normalizing.
		This simply sums up all of the dimensions.
		Then, the dimensions are rescaled to be between 0 and 1.

		.. note::

			The document is not normalized, but rescaled.
		"""

		"""
		If there are documents, concatenate them and rescale the dimensions between 0 and 1.
		Otherwise, create an empty nutrition set.
		"""
		if documents:
			document = Document.concatenate(*documents, tokenizer=self.tokenizer, scheme=self.scheme)
			max_magnitude = max(document.dimensions.values())
			document.dimensions = { dimension: magnitude / max_magnitude
									for dimension, magnitude in document.dimensions.items() }
			self.store.add(timestamp, document.dimensions)
		else:
			self.store.add(timestamp, { })

	def _remove_old_checkpoints(self, timestamp):
		"""
		Remove old checkpoints.
		The checkpoints that are removed depend on the number of sets that should be retained and the periodicity of the consumer.

		:param timestamp: The timestamp of the new checkpoint.
		:type timestamp: int
		"""

		until = timestamp - self.periodicity * self.sets
		if until > 0:
			self.store.remove(*self.store.until(until))

	def _cluster(self, documents):
		"""
		Cluster the given documents.

		:param documets: The documents to cluster.
		:type documents: list of :class:`~nlp.document.Document`

		:return: The list of clusters that have changed.
		:rtype: list of :class:`~vector.cluster.cluster.Cluster`
		"""

		return self.clustering.cluster(documents, time='timestamp')

	def _filter_clusters(self, clusters):
		"""
		Filter clusters that are too small.

		:param clusters: A list of clusters to filter.
		:type clusters: list of :class:`~vsm.clustering.cluster.Cluster`

		:return: A list of filtered clusters.
		:rtype: list of :class:`~vsm.clustering.cluster.Cluster`
		"""

		return list(filter(lambda cluster: cluster.size() >= self.min_size, clusters))

	def _detect_topics(self, cluster, timestamp):
		"""
		Detect topics from the given cluster.
		This method makes a copy of the nutrition store.
		It replaces the data at the given timestamp with a pseudo-checkpoint.
		This checkpoint is constructed using only data from the cluster.

		:param cluster: The cluster for which to identify breaking topics.
		:type cluster: :class:`~vsm.clustering.cluster.Cluster`
		:param timestamp: The current timestamp.
						  Sets older than this timestamp are used to calculate the burst.
		:type timestamp: int

		:return: A list of emerging terms from the cluster.
		:rtype: list
		"""

		"""
		Create a copy of the memory nutrition store.
		Replace the value at the current timestamp with a pseudo-checkpoint from the cluster's documents.
		"""
		copy = self.store.copy()
		document = Document.concatenate(*cluster.vectors, tokenizer=self.tokenizer, scheme=self.scheme)
		max_magnitude = max(document.dimensions.values())
		document.dimensions = { dimension: magnitude / max_magnitude
								for dimension, magnitude in document.dimensions.items() }
		copy.add(timestamp, document.dimensions)

		"""
		Run the algorithm.
		"""
		algo = Cataldi(copy)
		since = timestamp - self.periodicity * self.sets
		return algo.detect(timestamp=timestamp, since=since)
