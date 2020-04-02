"""
Finding Important News REports (FIRE) is a periodic TDT consumer.
It takes in tweets every time window, clusters them and finds the most important terms in each cluster.
In this implementation, the tracking happens through the timeline.

.. note::

	Implementation based on the algorithm presented in `FIRE: Finding Important News REports by Mamo and Azzopardi (2017) <https://link.springer.com/chapter/10.1007/978-3-319-74497-1_3>`_.
"""

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

from tdt.algorithms import Cataldi
from tdt.nutrition import MemoryNutritionStore

from nlp.document import Document
from nlp.term_weighting import TFIDF
from nlp.tokenizer import Tokenizer

import twitter

class FIREConsumer(SimulatedBufferedConsumer):
	"""
	The FIRE consumer is based on the implementation of the same name.
	The algorithm clusters all tweets received in the same period and uses the Cataldi et al. algorithm to identify which ones are breaking.

	:ivar store: The nutrition store used to store the volume changes of individual terms.
	:vartype store: :class:`~tdt.nutrition.store.NutritionStore`
	:ivar scheme: The term-weighting scheme used to create documents.
	:vartype scheme: :class:`~nlp.term_weighting.scheme.TermWeightingScheme`
	"""

	def __init__(self, queue, periodicity, scheme=None):
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
		"""

		super(FIREConsumer, self).__init__(queue, periodicity)
		self.store = MemoryNutritionStore()
		self.scheme = scheme

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
		tokenizer = Tokenizer(stopwords=stopwords.words("english"), normalize_words=True,
							  character_normalization_count=3, remove_unicode_entities=True)
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
		tokenizer = Tokenizer(stopwords=stopwords.words("english"), normalize_words=True,
							  character_normalization_count=3, remove_unicode_entities=True)

		for document in documents:
			tokens = tokenizer.tokenize(document.text)
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
			self.store.add_nutrition_set(timestamp, single_document.get_dimensions())
		elif timestamp is not None:
			self.store.add_nutrition_set(timestamp, {})
			logger.info("Checkpoint passed internally with 0 documents")

		if timestamp is not None:
			self.store.remove_old_nutrition_sets(timestamp - self._periodicity * (sets + 1)) # keep an extra one, just in case

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

		terms = cataldi.detect_topics(self.store, # use the nutrition store's checkpoints as historical data
			timestamp=timestamp, # do not consider checkpoints in this sliding time window, but only those that preceed it
			sets=sets, # consider the past few sets
		)
		return terms
