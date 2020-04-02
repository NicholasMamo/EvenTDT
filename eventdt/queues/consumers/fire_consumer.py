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
	:ivar sets: The number of time windows that are considered when computing burst.
				The higher this number, the more precise the calculations.
				However, because of the decay in :class:`~tdt.algorithms.cataldi.Cataldi`, old time windows do not affect the result by a big margin.
				Therefore old data can be removed safely.
	:vartype sets: int
	:ivar tokenizer: The tokenizer used to create documents.
	:vartype tokenizer: :class:`~nlp.tokenizer.Tokenizer`
	:ivar clustering: The clustering algorithm to use.
	:vartype clustering: :class:`~vsm.clustering.algorithms.temporal_no_k_means.TemporalNoKMeans`
	"""

	def __init__(self, queue, periodicity, scheme=None, sets=10, threshold=0.7, freeze_period=20):
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
		"""

		super(FIREConsumer, self).__init__(queue, periodicity)
		self.store = MemoryNutritionStore()
		self.scheme = scheme
		self.sets = sets

		self.tokenizer = Tokenizer(stopwords=stopwords.words("english"), normalize_words=True,
								   character_normalization_count=3, remove_unicode_entities=True)
		self.clustering = TemporalNoKMeans(threshold, freeze_period, store_frozen=False)

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

	def _cluster(self, documents):
		"""
		Cluster the given documents.

		:param documets: The documents to cluster.
		:type documents: list of :class:`~nlp.document.Document`

		:return: The list of clusters that have changed.
		:rtype: list of :class:`~vector.cluster.cluster.Cluster`
		"""

		return self.clustering.cluster(documents, time='timestamp', store_frozen=False)

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

		"""
		Remove old checkpoints.
		"""
		self.store.remove(*self.store.until(timestamp - self.periodicity * self.sets))

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
