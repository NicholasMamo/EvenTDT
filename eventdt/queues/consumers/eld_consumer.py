"""
Event TimeLine Detection (ELD) is a consumer based on a publication of the same name.
The approach splits processing into two steps:

 	#. Understand the event, and

	#. Build a timeline for it.

.. note::

	Implementation based on the algorithm presented in `ELD: Event TimeLine Detection -- A Participant-Based Approach to Tracking Events by Mamo et al. (2019) <https://dl.acm.org/doi/10.1145/3342220.3344921>`_.
"""

from nltk.corpus import stopwords

import asyncio
import json
import math
import os
import re
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from .consumer import Consumer

from apd.participant_detector import ParticipantDetector
from apd.extractors.local.entity_extractor import EntityExtractor
from apd.extrapolators.external.wikipedia_extrapolator import WikipediaExtrapolator
from apd.postprocessors.external.wikipedia_postprocessor import WikipediaPostprocessor
from apd.resolvers.external.wikipedia_search_resolver import WikipediaSearchResolver
from apd.scorers.local.log_tf_scorer import LogTFScorer

from logger import logger

from nlp.document import Document
from nlp.term_weighting import TF, TFIDF
from nlp.tokenizer import Tokenizer

from queues import Queue

from summarization.algorithms import DGS

from tdt.algorithms import ELD
from tdt.nutrition import MemoryNutritionStore

from vsm import vector_math
from vsm.clustering.algorithms import TemporalNoKMeans
from vsm.clustering import Cluster

class ELDConsumer(Consumer):
	"""
	The ELD consumer is a real-time consumer with a custom algorithm to detect topics.
	It is siplit into two steps:

		#. Understand the event, and

		#. Build a timeline for it.

	:ivar time_window: The time (in seconds) to spend consuming the queue.
	:vartype time_window: int
	:ivar store: The nutrition store used in conjunction with extractin breaking news.
	:vartype store: :class:`~topic_detection.nutrition_store.nutrition_store.NutritionStore`
	:ivar buffer: A buffer of tweets that have been processed, but which are not part of a checkpoint yet.
	:vartype buffer: :class:`~queues.queue.Queue`
	:ivar tokenizer: The tokenizer used to create documents and create the IDF table, among others.
	:vartype tokenizer: :class:`~vector.nlp.tokenizer.Tokenizer`
	:ivar clustering: The clustering algorithm to use.
	:vartype clustering: :class:`~vector.cluster.algorithms.nokmeans.TemporalNoKMeans`
	:ivar tdt: The TDT algorithm used to detect breaking developments.
	:vartype tdt: :class:`~tdt.algorithms.eld.ELD`
	:ivar summarization: The summarization algorithm used to create the timeline.
	:vartype summarization: :class:`~summarization.algorithms.dgs.DGS`
	"""

	def __init__(self, queue, time_window=60, scheme=None):
		"""
		Create the consumer with a queue.
		Simultaneously create a nutrition store and the topic detection algorithm container.
		Initially, the IDF table should be empty.
		It will be populated later when the 'reconaissance' period is finished.

		The constructor also creates a buffer.
		This buffer is used to store tweets until they are made into a checkpoint.

		:param queue: The queue that is consumed.
		:type queue: :class:`~queues.queue.Queue`
		:param time_window: The size of the window after which checkpoints are created.
		:type time_window: int
		"""

		super(ELDConsumer, self).__init__(queue)

		self.time_window = time_window

		"""
		Create the nutrition store and the buffer.
		The buffer stores tweets that have been processed, but not yet added to a checkpoint.
		"""
		self.store = MemoryNutritionStore()
		self.buffer = Queue()

		"""
		Create the different components of the system.
		"""
		self.tokenizer = Tokenizer(stopwords=stopwords.words('english'),
								   normalize_words=True, character_normalization_count=3,
								   remove_unicode_entities=True)
		self.clustering = TemporalNoKMeans(threshold=0.5, freeze_period=20, store_frozen=False)
		self.tdt = ELD(self.store)
		self.summarization = DGS()

	async def understand(self, max_time, max_inactivity=-1, scheme=None, *args, **kwargs):
		"""
		Understanding is split into two tasks:

			#. Construct the TF-IDF scheme used from the pre-event discussion, and

			#. Identify the event's participants.

		The function returns both in a tuple.

		:param max_time: The time, in seconds, spent understanding the event.
						 It may be interrupted if the queue is inactive for a long time.
		:type max_time: int
		:param max_inactivity: The maximum time (in seconds) to wait idly without input before stopping.
							   If it is negative, it is ignored.
		:type max_inactivity: int
		:param scheme: The term-weighting scheme that is used to create documents in APD.
					   If `None` is given, the :class:`~nlp.term_weighting.tf.TF` term-weighting scheme is used.
		:type scheme: None or :class:`~nlp.term_weighting.scheme.TermWeightingScheme`

		:return: A tuple containing the TF-IDF scheme and the event's participants from the pre-event discussion.
				 The TF-IDF scheme is a :class:`~nlp.term_weighting.tfidf.TFIDF` instance.
				 The participants are a list of strings.
		:rtype: tuple
		"""

		self._started()
		tfidf = await self._construct_idf(max_time=max_time, max_inactivity=max_inactivity)
		participants = await self._detect_participants(scheme)
		self._stopped()
		return (tfidf, participants)

	async def _construct_idf(self, max_time, max_inactivity):
		"""
		Construct the TF-IDF table from the pre-event discussion.
		All of the tweets processed by
		These documents may then be used by the APD task.

		:param max_time: The maximum time (in seconds) to spend understanding the event.
			It may be interrupted if the queue is inactive for a long time.
		:type max_time: int
		:param max_inactivity: The maximum time (in seconds) to wait idly without input before stopping.
			If it is negative, it is ignored.
		:type max_inactivity: int

		:return: The constructed IDF table.
		:rtype: dict
		"""

		real_start = datetime.now().timestamp() # the consumer will run for a limited real time
		total_tweets = 0

		while (True and self.active
			and (datetime.now().timestamp() - real_start < max_time)): # The consumer should keep working until it is stopped or it runs out of time
			"""
			If the queue is idle, stop waiting for input
			"""
			active = await self._wait_for_input(max_inactivity=max_inactivity)
			if not active:
				break

			"""
			Get all the tweets in the queue and add them to the buffer to be used for the checkpoint
			"""
			tweets = self._queue.dequeue_all()
			total_tweets += len(tweets)
			# tweets = self._filter_tweets(tweets)
			documents = self._tokenize(tweets)

			if len(documents) > 0:
				self.buffer.enqueue(documents)

				"""
				Update the IDF.
				"""
				for document in documents:
					for feature in set(document.get_dimensions().keys()):
						self._idf[feature] = self._idf.get(feature, 0) + 1
				self._idf["DOCUMENTS"] = self._idf.get("DOCUMENTS", 0) + len(documents)

		self.stopped = True # set a boolean indicating that the consumer has successfully stopped working

		return self._idf

	async def _detect_participants(self, general_idf, known_participants=None, *args, **kwargs):
		"""
		Detect participants from the received documents.

		:param general_idf: The general IDF table, constructed from a general corpus.
			This corpus represents the general discourse of Twitter.
			It is assumed that one of the keys of the table is the 'DOCUMENTS' field.
		:type general_idf: dict
		:param known_participants: A list of participants that are known in advance.
			These are passed on to be resolved, which means they may not be retained by the resolver.
		:type known_participants: list

		:return: A list of participants.
		:rtype: list
		"""

		documents = self.buffer.dequeue_all()
		cleaner = tweet_cleaner.TweetCleaner()
		scorer = tweet_scorer.TweetScorer()

		rules = [
			("score", filter.gte, 0.9),
			# ("verified", filter.true),
		]

		f = Filter(rules)

		corpus = []
		for document in documents:
			document.set_text(cleaner.clean(document.get_text()))

			tweet = {
				"score": scorer.score(document),
				# "verified": document.get_attribute("tweet")["user"]["verified"]
			}

			if f.filter(tweet):
				corpus.append(document)

		known_participants = [] if type(known_participants) is not list else known_participants
		known_participants = [ keyword for keyword in known_participants if all(c.isalpha() or c.isspace() for c in keyword) ]

		participant_detector = ParticipantDetector(corpus, EntityExtractor, LogSumScorer, WikipediaSearchResolver, WikipediaExtrapolator, WikipediaPostprocessor)
		resolved, unresolved, extrapolated = participant_detector.detect(threshold=0.2, max_candidates=20, known_participants=known_participants,
			resolver_scheme=TFIDF(general_idf), resolver_threshold=0.05,
			extrapolator_scheme=TFIDF(general_idf), extrapolator_participants=30, extrapolator_threshold=0.05,
			postprocessor_surname_only=True)
		logger.info("Found participants: %s" % ', '.join(resolved))
		logger.info("Extrapolated participants: %s" % ', '.join(extrapolated))
		return resolved + extrapolated

	async def _consume(self, max_time, max_inactivity, min_size=3, *args, **kwargs):
		"""
		Consume and process the documents in the queue.
		Processed documents are added to the buffer.

		:param max_time: The maximum time (in seconds) to spend understanding the event.
			It may be interrupted if the queue is inactive for a long time.
		:type max_time: int
		:param max_inactivity: The maximum time (in seconds) to wait idly without input before stopping.
			If it is negative, it is ignored.
		:type max_inactivity: int
		"""

		sets = 10
		threshold = 0.5
		freeze_period = 20
		min_burst = 0.5

		logger.info("Time window: %ds" % self.time_window)
		logger.info("Sets: %d" % sets)
		logger.info("Minimum cluster size: %d" % min_size)
		logger.info("Cluster threshold: %f" % threshold)
		logger.info("Freeze period: %ds" % freeze_period)
		logger.info("Minimum burst: %f" % min_burst)

		self.buffer.dequeue_all()
		real_start = datetime.now().timestamp() # the consumer will run for a limited real time
		start, last_timestamp = None, None # if a file is being used, the timing starts from the first tweet
		total_documents, total_tweets = 0, 0

		while True and self.active and (datetime.now().timestamp() - real_start < max_time): # The consumer should keep working until it is stopped or it runs out of time
			"""
			If the queue is idle, stop waiting for input.
			"""
			active = await self._wait_for_input(max_inactivity=max_inactivity)
			if not active:
				break

			"""
			Get all the tweets in the queue and add them to the buffer to be used for the checkpoint.
			"""
			tweets = self._queue.dequeue_all()
			total_tweets += len(tweets)
			tweets = self._filter_tweets(tweets)
			documents = self._tokenize(tweets)
			# documents = self._filter_documents(documents)
			documents = [ document for document in documents if last_timestamp is None or document.get_attribute("timestamp") >= last_timestamp ]
			documents = sorted(documents, key=lambda document: document.get_attribute("timestamp")) # NOTE: Untested

			self.buffer.enqueue(documents)

			if len(documents) > 0:
				"""
				If this is the first batch of tweets, start timing the procedure.
				If a time window has passed, create a checkpoint.
				The timing is incremented, rather than updated.
				This is aimed at circumventing problems when the consumer spends a lot of time waiting for input.
				In such cases, the time windows could be of unequal length.
				"""
				start = documents[0].get_attribute("timestamp") if start is None else start

				last_timestamp = documents[len(documents) - 1].get_attribute("timestamp")
				checkpoints = 0
				while start is not None and last_timestamp - start >= self.time_window:
					start += self.time_window
					await self._create_checkpoint(start, sets)
					checkpoints += 1

				if checkpoints >= 1:
					self.summarization.ping(last_timestamp)

				"""
				The current implementation resumes from the last time window if there is a backlog.
				That is, it skips all of those that are late.
				This makes sure that the backlog does not snowball.
				To fix this, don't work with all `documents`, but isolate a document set for each time window.
				"""
				if (checkpoints > 1):
					logger.warning("%d checkpoints created at time %s (UTC)" % (
						checkpoints,
						datetime.fromtimestamp(last_timestamp).strftime('%Y-%m-%d %H:%M:%S'))
					)
				documents = [ document for document in documents if document.get_attribute("timestamp") >= start ]

				"""
				If the understanding period has passed, start consuming the stream.

				Scenarios:
					In small events, a threshold of 0.6 and a minimum cluster size of 2 can help with a freeze period of 30 seconds.
					In larger events, a threshold of 0.65 and a minimum cluster size of 3 is preferable with a freeze period of 30 seconds.

					In large events, a threshold of 0.6 and a minimum cluster size of 3 works better with a freeze period of 20 seconds, but with a burst threshold of 0.8.
				"""
				clusters = self._cluster(documents, threshold=threshold, freeze_period=freeze_period) # TEMP: Updated threshold from 0.6 to 0.5 for LIVFUL match, worked well for ARSLIV.
				clusters = self._filter_clusters(clusters, last_timestamp, min_size=min_size, max_intra_similarity=0.9) # TEMP: Updated minimum size from 2 to 3 for LIVFUL match, worked well for ARSLIV.
				for cluster in clusters:
					"""
					Perform topic detection
					"""
					terms = self._detect_topics(cluster, threshold=min_burst, sets=sets, timestamp=last_timestamp, decay_rate=(1./5.))
					if len(terms) > 0:
						term_dict = dict(terms)
						if len(term_dict) > 2 or sum(term_dict.values())/len(terms) > 0.9:
							# summary = self.summarization.add_cluster(cluster, terms, last_timestamp, summarization_min_score=0.5)
							summary = self.summarization.add_cluster(cluster, terms, last_timestamp)

							cluster.set_attribute("checked", True) # once a cluster has been deemed to be breaking, it should not be checked anymore, which guards against repeated clusters in the summary

		await self._create_checkpoint(last_timestamp, sets)
		await asyncio.sleep(1)

		last_summary = self.summarization.create_summary()
		if last_summary is not None:
			logger.info("%s last: %s" % (datetime.fromtimestamp(last_summary.created_at()).strftime('%Y-%m-%d %H:%M:%S'),
				last_summary.generate_summary(cleaner=tweet_cleaner.TweetCleaner)))
		else:
			logger.info("Summarizer empty")

		logger.info("Last document published at time %s (UTC)" % datetime.fromtimestamp(last_timestamp).strftime('%Y-%m-%d %H:%M:%S'))

		self.stopped = True # set a boolean indicating that the consumer has successfully stopped working

		return (self.summarization.export_raw_timeline(), self.summarization.export_timeline(), )

	async def _create_checkpoint(self, timestamp, sets):
		"""
		After every time window has elapsed, get all the buffered documents.
		These documents are used to create a nutrition set for the nutrition store.
		This nutrition set represents a snapshot of the time window.

		:param timestamp: The timestamp of the new checkpoint.
		:type timestamp: int
		:param sets: The number of time windows that are considered.
			Older ones serve no purpose, so they may be removed.
		:type timestamp: int
		"""

		"""
		Concatenate all the documents in the buffer and normalize the dimensions.
		The goal is to get a list of dimensions in the range 0 to 1.
		"""

		document_set = []
		while self.buffer.length() > 0 and self.buffer.head().get_attribute("timestamp") < timestamp:
			document_set.append(self.buffer.dequeue())

		if len(document_set) > 0:
			"""
			Concatenate all the documents in the buffer and normalize the dimensions.
			The goal is to get a list of dimensions in the range 0 to 1.
			"""

			single_document = vector_math.concatenate(document_set)
			single_document = vector_math.augmented_normalize(single_document, a=0)
			self.store.add_nutrition_set(timestamp, single_document.get_dimensions())
			# logger.info("Checkpoint created with %d documents at time %s (UTC)" % (
			#	len(document_set),
			#	datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))
			# )
		elif timestamp is not None:
			self.store.add_nutrition_set(timestamp, {})
			logger.info("Checkpoint passed internally with 0 documents")

		if timestamp is not None:
			self.store.remove_old_nutrition_sets(timestamp - self.time_window * (sets + 1)) # keep an extra one, just in case

	def _filter_tweets(self, tweets):
		"""
		Filter the given tweets, largely based on FIRE's filtering rules.
		Tweets are removed if:

			#. They are not in English - an extra check, just in case;

			#. There are too many hashtags, indicating that the user is desperate for attention;

			#. The user has never favorited a tweet, indicative of bot-like behavior.;

			#. The user has fewer than one follower for every thousand tweets published. \
				These users are usually not only incredibly unpopular, but bots. \
				Their goal is to create trends;

			#. There is more than one URL. Too many URLs are indicative of pre-planned content. \
				For this reason alone, they may be removed. \
				If a development is breaking, many people post immediately, with minimal media; and

			#. The biography is empty. \
				Most users have a biography. Spam accounts do not bother.

		:param tweets: A list of tweets.
		:type tweets: list of dictionaries

		:return: A list of filtered tweets.
		:type tweets: list of dictionaries
		"""

		"""
		Remove objects that are not really tweets
		"""
		retained_tweets = []
		for tweet in tweets:
			if ("entities" in tweet):
				retained_tweets.append(tweet)

		for tweet in retained_tweets:
			"""
			Calculate some scores that are not provided by Twitter's API
			"""
			tweet["num_hashtags"] = len(tweet["entities"]["hashtags"])
			tweet["num_urls"] = len(tweet["entities"]["urls"])
			tweet["follower_per_tweet"] = tweet["user"]["followers_count"] / tweet["user"]["statuses_count"]
			tweet["bio_length"] = len(tweet["user"]["description"]) if tweet["user"]["description"] is not None else 0

		rules = [
			("lang", filter.equal, "en"),
			("num_hashtags", filter.lte, 2),
			("user:favourites_count", filter.gt, 0),
			("follower_per_tweet", filter.gte, 1./1000.)
		]

		# Rules that are new in ELD
		rules.append(("num_urls", filter.lt, 2))
		rules.append(("bio_length", filter.gt, 0))

		f = Filter(rules)
		return [ tweet for tweet in retained_tweets if f.filter(tweet) ]

	def _preprocess(self, tweets):
		"""
		Preprocess the tweets, adding the timestamp to the tweet.

		:param tweets: A list of tweets.
		:type tweets: list of dictionaries

		:return: A list of preprocessed tweets.
		:type tweets: list of dictionaries
		"""
		for tweet in tweets:
			timestamp_ms = int(tweet["timestamp_ms"])
			tweet["timestamp"] = timestamp_ms - timestamp_ms % 1000
		return tweets

	def _filter_documents(self, documents):
		"""
		Filter the given documents based on FIRE's filtering rules. Documents are removed if their score, approximating quality, is low.

		:param documents: The documents to filter.
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

			tokens = self.tokenizer.tokenize(text)
			document = Document(text, tokens, scheme=self.scheme)
			document.set_attribute("tokens", tokens)
			document.set_attribute("timestamp", timestamp)
			document.set_attribute("tweet", tweet)

			document.normalize()
			documents.append(document)

		return documents

	def _cluster(self, documents, threshold=0.7, freeze_period=1):
		"""
		Cluster the given documents.

		:param documents: The documents to cluster.
		:type documents: list of :class:`~vector.nlp.document.Document` instances
		:param threshold: The threshold to use for the incremental clustering approach.
		:type threshold: float
		:param freeze_period: The freeze period (in seconds) of the incremental clustering approach.
		:type freeze_period: float

		:return: The list of clusters that are still active and that have changed.
		:rtype: list of :class:`~vector.cluster.cluster.Cluster` instances
		"""

		clusters = self.clustering.cluster(documents, threshold=threshold, freeze_period=freeze_period, time_attribute="timestamp", store_frozen=False)
		return clusters
		# return self.clustering.get_clusters(ClusterType.ACTIVE)

	def _filter_clusters(self, clusters, timestamp, min_size=10, cooldown=1, max_intra_similarity=0.8):
		"""
		Get a list of clusters that should be checked for emerging topics.
		The filtering looks at various aspects:

			#. A cluster must be slightly large, indicating popularity and importance;

			#. A cluster must not have been checked very recently;

			#. A cluster's documents must not be quasi-identical to each other. \
				This might indicate a slew of retweets. \
				When something happens, people do not wait until someone writes something. \
				Instead, they themselves create conversation;

			#. A cluster may not have been checked previously; and

			#. A cluster must not be inundated with URLs. \
				URLs may be used not only for links, but also media. \
				They indicate premeditation, and possibly spam when all tweets contain them.

		:param clusters: The active clusters, which represent candidate topics.
		:type clusters: list of :class:`~vector.cluster.cluster.Cluster` instances
		:param timestamp: The current timestamp.
			Used to check whether the cluster has been checked recently.
		:type timestamp: int
		:param min_size: The minimum size of a cluster to be considered valid.
		:type min_size: int
		:param cooldown: The minimum time (in seconds) between consecutive checks of a cluster.
		:type cooldown: float
		:param max_intra_similarity: The maximum average similarity, between 0 and 1, of the cluster's documents with the centroid.
			Used to filter out clusters that include only retweets of the same, or almost identical documents.
		:type max_intra_similarity: float

		:return: A list of clusters that should be checked for emerging terms.
		:rtype: list of :class:`~vector.cluster.cluster.Cluster` instances
		"""

		retained_clusters = []

		"""
		Clusters are valid if they are moderately large and they have not been checked recently.
		Moreover, clusters that have more than one URL - either a link to a page, or a media file - are removed.
		This is based on the observation that tweets with many URLs are usually premeditated, or spam.
		"""

		for cluster in clusters:
			cluster.set_attribute("size", cluster.size())
			cluster.set_attribute("cooldown", timestamp - cluster.get_attribute("last_checked", 0))
			cluster.set_attribute("intra_similarity", cluster.get_intra_similarity())
			cluster.initialize_attribute("checked", False) # only set the flag if it does not exist - if the cluster has been checkd, do nothing

			url_pattern = re.compile("https:\\/\\/t.co\\/[a-zA-Z0-9]+\\b")
			urls = [ len(url_pattern.findall(document.get_text())) for document in cluster.get_vectors() ]
			cluster.set_attribute("average_urls", sum(urls)/len(urls))

			replies = [ document.get_text().startswith("@") for document in cluster.get_vectors() ]
			cluster.set_attribute("average_replies", sum(replies)/cluster.size())

		rules = [
			("size", filter.gte, min_size),
			("cooldown", filter.gt, cooldown),
			("intra_similarity", filter.lte, max_intra_similarity),
			("checked", filter.false),
			("average_urls", filter.lte, 1),
			("average_replies", filter.lte, 0.5),
		]

		f = Filter(rules)
		return [cluster for cluster in clusters if f.filter(cluster.get_attributes())]

	def _detect_topics(self, cluster, threshold, sets, timestamp, decay_rate=(1./2)):
		"""
		Perform topic detection.

		:param cluster: The cluster from which to extract the documents.
		:type cluster: :class:`~vector.cluster.cluster.Cluster`
		:param threshold: The minimum emergence of a term to be said to be breaking.
		:type threshold: float
		:param sets: The number of time windows to consider.
		:type sets: int
		:param timestamp: The current timestamp, used to isolate recent documents.
		:type timestamp: int
		:param decay_rate: The decay rate - a smaller decay rate favors recent time windows.
		:type decay_rate: float

		:return: A list of emerging terms from the cluster.
			Each term is actually a tuple, containing the keyword and its emergence.
		:rtype: list
		"""

		cluster.set_attribute("last_checked", timestamp)
		documents = self._get_recent_documents(cluster, timestamp)
		single_document = vector_math.concatenate(documents)
		single_document = vector_math.augmented_normalize(single_document, a=0)

		terms = mamo_eld.detect_topics(self.store, # use the nutrition store's checkpoints as historical data
			single_document.get_dimensions(),  # the current data is the most recent documents from the cluster
			threshold, # use a strict threshold
			sets=sets, # consider the past few sets
			timestamp=timestamp-self.time_window,# do not consider checkpoints in this sliding time window, but only those that preceed it
			decay_rate=decay_rate, # set a decay rate,
			term_only=False
		)
		return terms

class SimulatedELDConsumer(ELDConsumer):
	"""
	The SimulatedELDConsumer is a consumer built on the ELDConsumer.
	It is aimed at being used with files.
	Thus the only changes are made to the consuming functions.
	In this case, the time window is not based on real time, but on the tweets' timestamps.
	"""

	async def _construct_idf(self, understanding_period, max_time, max_inactivity):
		"""
		Construct the IDF table.
		Processed documents are added to the buffer.
		These documents may then be used by the APD task.

		:param max_time: The maximum time (in seconds) to spend understanding the event.
			It may be interrupted if the queue is inactive for a long time.
		:type max_time: int
		:param max_inactivity: The maximum time (in seconds) to wait idly without input before stopping.
			If it is negative, it is ignored.
		:type max_inactivity: int

		:return: The constructed IDF table.
		:rtype: dict
		"""

		real_start = datetime.now().timestamp() # the consumer will run for a limited real time
		start, last_timestamp = None, None # if a file is being used, the timing starts from the first tweet
		total_documents, total_tweets = 0, 0

		while (True and self.active
			and (start is None or datetime.now().timestamp() - real_start < max_time)
			and (start is None or last_timestamp - start < understanding_period)): # The consumer should keep working until it is stopped or it runs out of time
			"""
			If the queue is idle, stop waiting for input
			"""
			active = await self._wait_for_input(max_inactivity=max_inactivity)
			if not active:
				break

			"""
			Get all the tweets in the queue and add them to the buffer to be used for the checkpoint
			"""
			tweets = self._queue.dequeue_all()
			total_tweets += len(tweets)
			# tweets = self._filter_tweets(tweets)
			documents = self._tokenize(tweets)

			if len(documents) > 0:
				"""
				If this is the first batch of tweets, start timing the procedure
				"""
				start = documents[0].get_attribute("timestamp") if start is None else start

				last_timestamp = documents[len(documents) - 1].get_attribute("timestamp")
				# documents = self._filter_documents(documents)
				self.buffer.enqueue(documents)

				"""
				Update the IDF.
				"""
				for document in documents:
					for feature in set(document.get_dimensions().keys()):
						self._idf[feature] = self._idf.get(feature, 0) + 1
				self._idf["DOCUMENTS"] = self._idf.get("DOCUMENTS", 0) + len(documents)

		self.stopped = True # set a boolean indicating that the consumer has successfully stopped working

		return self._idf

	async def _consume(self, max_time, max_inactivity, min_size=3, timeline_filename=None, *args, **kwargs):
		"""
		Consume and process the documents in the queue.
		Processed documents are added to the buffer.

		:param max_time: The maximum time (in seconds) to spend understanding the event.
			It may be interrupted if the queue is inactive for a long time.
		:type max_time: int
		:param max_inactivity: The maximum time (in seconds) to wait idly without input before stopping.
			If it is negative, it is ignored.
		:type max_inactivity: int

		:return: The timeline as a list.
		:rtype: list
		"""

		sets = 10
		threshold = 0.5
		freeze_period = 20
		min_burst = 0.5

		self.buffer.dequeue_all()
		real_start = datetime.now().timestamp() # the consumer will run for a limited real time
		start, last_timestamp, last_written = None, None, None # if a file is being used, the timing starts from the first tweet
		total_documents, total_tweets = 0, 0

		logger.info("Time window: %ds" % self.time_window)
		logger.info("Sets: %d" % sets)
		logger.info("Minimum cluster size: %d" % min_size)
		logger.info("Cluster threshold: %f" % threshold)
		logger.info("Freeze period: %ds" % freeze_period)
		logger.info("Minimum burst: %f" % min_burst)

		while True and self.active and (start is None or datetime.now().timestamp() - real_start < max_time): # The consumer should keep working until it is stopped or it runs out of time
			"""
			If the queue is idle, stop waiting for input.
			"""
			active = await self._wait_for_input(max_inactivity=max_inactivity)
			if not active:
				break

			"""
			Get all the tweets in the queue and add them to the buffer to be used for the checkpoint.
			"""
			tweets = self._queue.dequeue_all()
			total_tweets += len(tweets)
			# for tweet in tweets:
			# 	logger.info(tweet.get("text", ""))
			tweets = self._filter_tweets(tweets)
			documents = self._tokenize(tweets)
			# documents = self._filter_documents(documents)
			documents = [ document for document in documents if last_timestamp is None or document.get_attribute("timestamp") >= last_timestamp ]
			documents = sorted(documents, key=lambda document: document.get_attribute("timestamp")) # NOTE: Untested

			self.buffer.enqueue(documents)

			if len(documents) > 0:
				"""
				If this is the first batch of tweets, start timing the procedure.
				If a time window has passed, create a checkpoint.
				The timing is incremented, rather than updated.
				This is aimed at circumventing problems when the consumer spends a lot of time waiting for input.
				In such cases, the time windows could be of unequal length.
				"""
				start = documents[0].get_attribute("timestamp") if start is None else start

				last_timestamp = documents[len(documents) - 1].get_attribute("timestamp")
				checkpoints = 0
				while start is not None and last_timestamp - start >= self.time_window:
					start += self.time_window
					await self._create_checkpoint(start, sets)
					checkpoints += 1

				if checkpoints >= 1:
					self.summarization.ping(last_timestamp)

				"""
				The current implementation resumes from the last time window if there is a backlog.
				That is, it skips all of those that are late.
				This makes sure that the backlog does not snowball.
				To fix this, don't work with all `documents`, but isolate a document set for each time window.
				"""
				if (checkpoints > 1):
					logger.warning("%d checkpoints created at time %s (UTC)" % (
						checkpoints,
						datetime.fromtimestamp(last_timestamp).strftime('%Y-%m-%d %H:%M:%S'))
					)
				documents = [ document for document in documents if document.get_attribute("timestamp") >= start ]

				"""
				If the understanding period has passed, start consuming the stream.

				Scenarios:
					In small events, a threshold of 0.6 and a minimum cluster size of 2 can help with a freeze period of 30 seconds.
					In larger events, a threshold of 0.65 and a minimum cluster size of 3 is preferable with a freeze period of 30 seconds.

					In large events, a threshold of 0.6 and a minimum cluster size of 3 works better with a freeze period of 20 seconds, but with a burst threshold of 0.8.
				"""
				clusters = self._cluster(documents, threshold=threshold, freeze_period=freeze_period) # TEMP: Updated threshold from 0.6 to 0.5 for LIVFUL match, worked well for ARSLIV.
				clusters = self._filter_clusters(clusters, last_timestamp, min_size=min_size, max_intra_similarity=0.9) # TEMP: Updated minimum size from 2 to 3 for LIVFUL match, worked well for ARSLIV.
				for cluster in clusters:
					"""
					Perform topic detection
					"""
					terms = self._detect_topics(cluster, threshold=min_burst, sets=sets, timestamp=last_timestamp, decay_rate=(1./5.))
					if len(terms) > 0:
						term_dict = dict(terms)
						if len(term_dict) > 2 or sum(term_dict.values())/len(terms) > 0.9:
							# summary = self.summarization.add_cluster(cluster, terms, last_timestamp, summarization_min_score=0.5)
							summary = self.summarization.add_cluster(cluster, terms, last_timestamp)

							cluster.set_attribute("checked", True) # once a cluster has been deemed to be breaking, it should not be checked anymore, which guards against repeated clusters in the summary

				# """
				# Create a digest and write it to file if one is provided.
				# """
				# if timeline_filename is not None:
				# 	last_written = last_timestamp if last_written is None else last_written # set the initial value of the last time the digest was created if need be
				# 	if last_timestamp - last_written > 60: # the file is written to once every minute
				# 		self._create_digest(timeline_filename)
				# 		last_written = last_timestamp

		await self._create_checkpoint(last_timestamp, sets)
		await asyncio.sleep(1)

		"""
		Create a digest and write it to file if one is provided.
		"""
		if timeline_filename is not None:
			self._create_digest(timeline_filename)

		last_summary = self.summarization.create_summary()
		if last_summary is not None:
			logger.info("%s last: %s" % (datetime.fromtimestamp(last_summary.created_at()).strftime('%Y-%m-%d %H:%M:%S'),
				last_summary.generate_summary(cleaner=tweet_cleaner.TweetCleaner)))
		else:
			logger.info("Summarizer empty")

		logger.info("Last document published at time %s (UTC)" % datetime.fromtimestamp(last_timestamp).strftime('%Y-%m-%d %H:%M:%S'))

		self.stopped = True # set a boolean indicating that the consumer has successfully stopped working

		return (self.summarization.export_raw_timeline(), self.summarization.export_timeline(), )
