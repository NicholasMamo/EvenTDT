"""
Event TimeLine Detection (ELD) is a consumer based on a publication of the same name.
The approach splits processing into two steps:

 	#. Understand the event, and

	#. Build a timeline for it.

.. note::

	Implementation based on the algorithm presented in `ELD: Event TimeLine Detection -- A Participant-Based Approach to Tracking Events by Mamo et al. (2019) <https://dl.acm.org/doi/10.1145/3342220.3344921>`_.
"""

from datetime import datetime
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

from nlp.cleaners import TweetCleaner
from nlp.document import Document
from nlp.term_weighting import TF, TFIDF
from nlp.term_weighting.global_schemes.idf import IDF
from nlp.tokenizer import Tokenizer

from queues import Queue

from summarization.algorithms import DGS
from summarization.timeline import Timeline
from summarization.timeline.nodes import TopicalClusterNode

from tdt.algorithms import ELD
from tdt.nutrition import MemoryNutritionStore

import twitter

from vsm import Vector, vector_math
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
	:ivar scheme: The term-weighting scheme used to create documents.
	:vartype scheme: :class:`~nlp.term_weighting.scheme.TermWeightingScheme`
	:ivar min_size: The minimum size of a cluster to be considered valid.
	:vartype min_size: int
	:ivar cooldown: The minimum time (in seconds) between consecutive checks of a cluster.
	:vartype cooldown: float
	:ivar max_intra_similarity: The maximum average similarity, between 0 and 1, of the cluster's documents with the centroid.
								Used to filter out clusters that include only retweets of the same, or almost identical documents.
	:vartype max_intra_similarity: float
	:ivar sets: The number of time windows that are considered when computing burst.
				The higher this number, the more precise the calculations.
				However, because of the decay in :class:`~tdt.algorithms.cataldi.Cataldi`, old time windows do not affect the result by a big margin.
				Therefore old data can be removed safely.
	:vartype sets: int
	:ivar min_burst: The minimum burst of a term to be considered emerging and returned.
					 This value is exclusive.
	:vartype min_burst: float
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
	:ivar cleaner: The cleaner used to make summaries more presentable.
	:vartype cleaner: :class:`~nlp.cleaners.TweetCleaner`
	"""

	def __init__(self, queue, time_window=30, scheme=None,
				 threshold=0.5, freeze_period=20, min_size=3, cooldown=1, max_intra_similarity=0.8,
				 sets=10, min_burst=0.5):
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
		:param scheme: The term-weighting scheme that is used to create dimensions.
					   If `None` is given, the :class:`~nlp.term_weighting.tf.TF` term-weighting scheme is used.
		:type scheme: None or :class:`~nlp.term_weighting.scheme.TermWeightingScheme`
		:param threshold: The similarity threshold to use for the :class:`~vsm.clustering.algorithms.temporal_no_k_means.TemporalNoKMeans` incremental clustering approach.
						  Documents are added to an existing cluster if their similarity with the centroid is greater than or equal to this threshold.
		:type threshold: float
		:param freeze_period: The freeze period, in seconds, of the incremental clustering approach.
		:type freeze_period: float
		:param min_size: The minimum size of a cluster to be considered valid.
		:type min_size: int
		:param cooldown: The minimum time (in seconds) between consecutive checks of a cluster.
		:type cooldown: float
		:param max_intra_similarity: The maximum average similarity, between 0 and 1, of the cluster's documents with the centroid.
									 Used to filter out clusters that include only retweets of the same, or almost identical documents.
		:type max_intra_similarity: float
		:param sets: The number of time windows that are considered when computing burst.
					 The higher this number, the more precise the calculations.
					 However, because of the decay in :class:`~tdt.algorithms.cataldi.Cataldi`, old time windows do not affect the result by a big margin.
					 Therefore old data can be removed safely.
		:type sets: int
		:param min_burst: The minimum burst of a term to be considered emerging and returned.
						  This value is exclusive.
		:type min_burst: float
		"""

		# NOTE: 1 second cooldown is very low. Maybe this parameter isn't needed.

		super(ELDConsumer, self).__init__(queue)

		self.time_window = time_window
		self.scheme = scheme
		self.sets = sets
		self.min_size = min_size
		self.cooldown = cooldown
		self.max_intra_similarity = max_intra_similarity
		self.min_burst = min_burst

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
		self.clustering = TemporalNoKMeans(threshold=threshold, freeze_period=freeze_period, store_frozen=False)
		self.tdt = ELD(self.store)
		self.cleaner = TweetCleaner(remove_alt_codes=True, complete_sentences=True,
									collapse_new_lines=True, collapse_whitespaces=True,
									remove_unicode_entities=True, remove_urls=True,
									remove_hashtags=True, split_hashtags=True,
									remove_retweet_prefix=True)
		self.summarization = DGS()

	async def understand(self, max_inactivity=-1, *args, **kwargs):
		"""
		Understanding is split into two tasks:

			#. Construct the TF-IDF scheme used from the pre-event discussion, and

			#. Identify the event's participants.

		The function returns both as a dictionary.
		The two keys are `scheme` and `participants`.

		Any additional arguments and keyword arguments are passed on to the :func:`~queues.consumers.eld_consumer.ELDConsumer._construct_idf` and :func:`~queues.consumers.eld_consumer.ELDConsumer._detect_participants` functions.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, it is ignored.
		:type max_inactivity: int

		:return: A dictionary containing the TF-IDF scheme and the event's participants from the pre-event discussion.
				 The TF-IDF scheme is returned in the `scheme` key as a :class:`~nlp.term_weighting.tfidf.TFIDF` instance.
				 The participants are returned in the `participants` key a list of strings.
		:rtype: dict
		"""

		self._started()
		tfidf = await self._construct_idf(max_time=max_time, max_inactivity=max_inactivity)
		participants = await self._detect_participants()
		self._stopped()
		return { 'scheme': tfidf, 'participants': participants }

	async def _construct_idf(self, max_inactivity):
		"""
		Construct the TF-IDF table from the pre-event discussion.
		All of the tweets processed by these documents are added to a buffer so they can be used by the APD task.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, it is ignored.
		:type max_inactivity: int

		:return: The constructed TF-IDF scheme.
		:rtype: :class:`~nlp.term_weighting.tfidf.TFIDF`
		"""

		idf = { }

		"""
		Understanding keeps working until it is stopped.
		"""
		while self.active:
			await asyncio.sleep(1)

		"""
		After it is stopped, construct the IDF.
		Get all the tweets in the queue and convert them to documents.
		Use these documents to build the IDF, but add them to the buffer so they can be used by the APD process.
		"""
		tweets = self.queue.dequeue_all()
		documents = self._to_documents(tweets)
		self.buffer.enqueue(*documents)

		"""
		Update the IDF with the new documents.
		"""
		idf = IDF.from_documents(documents)

		return TFIDF(idf, self.buffer.size())

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

	async def _consume(self, max_inactivity, *args, **kwargs):
		"""
		Consume and process the documents in the queue.
		Processed documents are added to the buffer.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, the consumer keeps waiting for input until the maximum time expires.
		:type max_inactivity: int

		:return: The constructed timeline.
		:rtype: :class:`~summarization.timeline.timeline.Timeline`
		"""

		timeline = Timeline(TopicalClusterNode, expiry=90, min_similarity=0.6)

		"""
		The consumer should keep working until it is stopped.
		Before that, create a placeholder variable to store the time of the last checkpoint.
		"""
		last_checkpoint = None
		while self.active:
			"""
			If the queue is idle, stop waiting for input.
			"""
			active = await self._wait_for_input(max_inactivity=max_inactivity)
			if not active:
				break

			if self.queue.length():
				"""
				Get all the tweets in the queue and convert them to documents.
				These documents are added to the buffer so that they can become part of a checkpoint later.
				"""
				tweets = self.queue.dequeue_all()
				tweets = self._filter_tweets(tweets)
				documents = self._to_documents(tweets)
				if not tweets:
					continue

				latest_timestamp = self._latest_timestamp(documents)
				self.buffer.enqueue(*documents)

				"""
				In the first batch of tweets, the last checkpoint is set to be the first document's timestamp.
				"""
				last_checkpoint = last_checkpoint or documents[0].attributes['timestamp']

				"""
				If a time window has passed, create a checkpoint.
				Multiple checkpoints can be created in every iteration.
				This is because when there are backlogs, an iteration can take longer than a time window.
				In this way, all time windows are of equal length.
				"""
				while latest_timestamp - last_checkpoint >= self.time_window:
					last_checkpoint += self.time_window
					self._create_checkpoint(last_checkpoint)

				"""
				To avoid backlogs from hogging the system, documents published since before the last time window are not used.
				That is, the implementation skips all of those that are late.
				"""
				documents = [ document for document in documents
							  if latest_timestamp - document.attributes['timestamp'] < self.time_window ]

				"""
				Cluster the documents that remain and filter the clusters.
				For each cluster, detect any breaking terms.
				"""
				clusters = self._cluster(documents)
				clusters = self._filter_clusters(clusters, latest_timestamp)
				for cluster in clusters:
					"""
					A cluster is breaking if:

						#. It has at least 3 breaking terms, or

						#. The average burst of its breaking terms is higher than 0.9.

					Clusters that are breaking are marked as such so that they are not checked again.
					"""
					terms = self._detect_topics(cluster, latest_timestamp)
					if len(terms) > 2 or (terms and sum(terms.values())/len(terms) > 0.9):
						cluster.attributes['bursty'] = True
						topic = Vector(terms)
						topic.normalize()
						timeline.add(timestamp=latest_timestamp, cluster=cluster, topic=topic)

						"""
						After adding a cluster to the timeline, generate a summary.
						"""
						summary_documents = self._score_documents(timeline.nodes[-1].get_all_documents())[:50]
						for document in summary_documents:
							document.text = self.cleaner.clean(document.text)

						"""
						Generate a query from the topical keywords and use it to come up with a summary.
						"""
						query = Cluster(vectors=timeline.nodes[-1].topics).centroid
						summary = self.summarization.summarize(summary_documents, 140, query=query)
						logger.info(f"{datetime.fromtimestamp(latest_timestamp).ctime()}: { str(summary) }")

		return timeline

	def _update_idf(self, idf, subset):
		"""
		Update the IDF with the new subset.

		:param idf: The current IDF.
					The function expects a dictionary with the keys being terms and the values their document frequency.
		:type idf: dict
		:param subset: The IDF constructed from a subset of documents.
					   The function expects a dictionary with the keys being terms and the values their document frequency.
		:type subset: dict

		:return: The updated IDF with the terms being the keys and the values their document frequency.
		:rtype: dict
		"""

		return { term: idf.get(term, 0) + subset.get(term, 0) for term in idf.keys() | subset.keys() }

	def _filter_tweets(self, tweets):
		"""
		Filter the given tweets based on :class:`~.queues.consumers.fire_consumer.FIREConsumer`'s filtering rules and new rules.
		FIRE's rules are:

			#. The tweet has to be in English,

			#. The tweet must contain no more than 2 hashtags,

			#. The tweet's author must have favorited at least one tweet, and

			#. The tweet's author must have at least one follower for every thousand tweets they've published.

		The new rules are:

			#. The tweet cannot have more than one URL because too many URLs are indicative of pre-planned content, and

			#. The biography of the tweet's author cannot be empty because that is indicative of bots.

		:param tweets: A list of tweets to filter.
		:type tweets: list of dict

		:return: A list of filtered tweets.
		:type tweets: list of dict
		"""

		"""
		Apply FIRE's filtering rules.
		"""
		tweets = filter(lambda tweet: tweet['lang'] == 'en', tweets)
		tweets = filter(lambda tweet: len(tweet['entities']['hashtags']) <= 2, tweets)
		tweets = filter(lambda tweet: tweet['user']['favourites_count'] > 0, tweets)
		tweets = filter(lambda tweet: tweet['user']['followers_count'] / tweet['user']['statuses_count'] >= 1e-3, tweets)

		"""
		Apply ELD's filtering rules.
		"""

		tweets = filter(lambda tweet: len(tweet['entities']['urls']) <= 1, tweets)
		tweets = filter(lambda tweet: tweet['user']['description'], tweets)

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

	def _create_checkpoint(self, timestamp):
		"""
		After every time window has elapsed, use all the buffered documents to create a new checkpoint.
		The checkpoint creates a new nutrition set stored in the nutrition store.
		This nutrition set represents a snapshot of the time window.

		.. note::

			The ELD consumer follows a real-time process.
			Since there could be a backlog, the function ensures that documents published after the given timestamp are not added to the checkpoint.

		:param timestamp: The timestamp of the new checkpoint.
						  The nutrition data is from documents published in the time window that ends at this timestamp.
						  Newer documents are left in the buffer.
						  This timestamp is inclusive.
		:type timestamp: int
		"""

		"""
		At times, tweets do not arrive in order of their timestamp.
		Therefore before creating the checkpoint, re-organize the buffer.
		The buffer is created with only the documents published before or at the given timestamp.
		The rest of the documents are re-added to the buffer.
		"""
		documents = self.buffer.dequeue_all()
		documents = sorted(documents, key=lambda document: document.attributes['timestamp'])
		self.buffer.enqueue(*[ document for document in documents if document.attributes['timestamp'] > timestamp ])
		documents = [ document for document in documents if document.attributes['timestamp'] <= timestamp ]

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
		The checkpoints that are removed depend on:

			#. The number of sets that should be retained, and

			#. The length of the time window of the consumer.

		:param timestamp: The timestamp of the new checkpoint.
		:type timestamp: int
		"""

		until = timestamp - self.time_window * self.sets
		if until > 0:
			self.store.remove(*self.store.until(until))

	def _cluster(self, documents):
		"""
		Cluster the given documents.

		:param documents: The documents to cluster.
		:type documents: list of :class:`~nlp.document.Document`

		:return: The list of clusters that are still active and that have changed.
		:rtype: list of :class:`~vector.cluster.cluster.Cluster`
		"""

		return self.clustering.cluster(documents, time='timestamp')

	def _filter_clusters(self, clusters, timestamp):
		"""
		Get a list of clusters that should be checked for emerging topics.
		The filtering rules are:

			#. A cluster must have a minimum number of tweets, indicating popularity.

			#. A cluster must not have been checked very recently. \
			   This keeps from checking clusters for breaking topics too often. \
			   Instead, clusters are checked only after some time has passed to save some time.

			#. A cluster's documents must not be quasi-identical to each other. \
			   This might indicate a slew of retweets. \
			   When something happens, people do not wait until someone writes something. \
			   Instead, they themselves create conversation;

			#. A cluster may not have been deemed to be bursty already. \
			   Clusters that are bursty may keep collecting tweets for the summary. \
			   However, they may not be added twice to the same timeline node.

			#. A cluster must not have more than one URL per tweet on average. \
			   URLs include both links and media. \
			   They indicate premeditation, usually spam, when all tweets contain them.

			#. No more than half of a cluster's tweets may be replies.

		:param clusters: The active clusters, which represent candidate topics.
		:type clusters: list of :class:`~vector.clustering.cluster.Cluster`
		:param timestamp: The current timestamp, used to check how long ago the cluster was last checked.
		:type timestamp: int

		:return: A list of clusters that should be checked for emerging terms.
		:rtype: list of :class:`~vsm.clustering.cluster.Cluster`
		"""

		filtered = list(clusters)

		"""
		Filter clusters based on readily-available attributes.
		"""
		filtered = filter(lambda cluster: cluster.size() >= self.min_size, filtered)
		filtered = filter(lambda cluster: timestamp - cluster.attributes.get('last_checked', 0) > self.cooldown, filtered)
		filtered = filter(lambda cluster: cluster.get_intra_similarity() <= self.max_intra_similarity, filtered)
		filtered = filter(lambda cluster: not cluster.attributes.get('bursty', False), filtered)
		filtered = list(filtered)

		"""
		Filter clusters that have more than 1 url per tweet on average.
		"""
		for cluster in filtered:
			urls = [ len(document.attributes['tweet']['entities']['urls'])
					 for document in cluster.vectors ]
			if sum(urls)/cluster.size() > 1:
				filtered.remove(cluster)

		"""
		Filter clusters that have more than half of tweets being replies.
		"""
		for cluster in filtered:
			replies = [ document.text.startswith('@') for document in cluster.vectors ]
			if sum(replies)/cluster.size() > 0.5:
				filtered.remove(cluster)

		return list(filtered)

	def _detect_topics(self, cluster, timestamp):
		"""
		Detect topics using historical data from the given nutrition store.

		:param cluster: The cluster for which to identify breaking topics.
		:type cluster: :class:`~vsm.clustering.cluster.Cluster`
		:param timestamp: The current timestamp.
						  Sets older than this timestamp are used to calculate the burst.
		:type timestamp: int

		:return: The breaking terms and their burst as a dictionary.
				 The keys are the terms and the values are the respective burst values.
		:rtype: dict
		"""

		"""
		Mark the cluster as having been checked.
		"""
		cluster.attributes['last_checked'] = timestamp

		"""
		Create a pseudo-checkpoint from the cluster's documents.
		"""
		document = Document.concatenate(*cluster.vectors, tokenizer=self.tokenizer, scheme=self.scheme)
		max_magnitude = max(document.dimensions.values())
		document.dimensions = { dimension: magnitude / max_magnitude
								for dimension, magnitude in document.dimensions.items() }

		"""
		Calculate the burst for all the terms in the cluster's pseudo-checkpoint.
		The last sets are used.
		"""
		since = timestamp - self.time_window * self.sets
		until = timestamp - self.time_window
		return self.tdt.detect(document.dimensions, min_burst=self.min_burst,
							   since=since, until=until)

	def _score_documents(self, documents, *args, **kwargs):
		"""
		Score the given documents.
		The score is the product of two scores:

			#. A brevity score, based on `BLEU: a Method for Automatic Evaluation of Machine Translation by Papineni et al. (2002) <https://dl.acm.org/doi/10.3115/1073083.1073135>`; and

			#. An emotion score, which is the complement of the fraction of tokens that are capitalized.

		Any additional arguments and keyword arguments are passed on to the functions that calculate the scores.

		:param documents: The list of documents to score.
		:type documents: list of :class:`~nlp.document.Document`

		:return: A list of documents ranked in descending order of their score.
		:rtype: list of :class:`~nlp.document.Document`
		"""

		"""
		Score each document.
		"""
		scores = { }
		for document in documents:
			brevity = self._brevity_score(document.text, *args, **kwargs)
			emotion = self._emotion_score(document.text)
			scores[document] = brevity * emotion

		return sorted(scores, key=scores.get, reverse=True)

	def _brevity_score(self, text, r=10, *args, **kwargs):
		"""
		Calculate the brevity score, bounded between 0 and 1.
		This score is based on `BLEU: a Method for Automatic Evaluation of Machine Translation by Papineni et al. (2002) <https://dl.acm.org/doi/10.3115/1073083.1073135>`:

		.. math::

			score = max(1, e^{1 - \\frac{r}{c}})

		where :math:`c` is the number of tokens in the text, and :math:`r` is the ideal number of tokens.

		The score is 1 even when the tweet is longer than the desired length.
		In this way, the brevity score is more akin to a brevity penalty.

		:param text: The text to score.
					 The text is tokanized by the function.
		:type text: str
		:param r: The ideal number of tokens in the text.
		:type r: str

		:return: The brevity score, bounded between 0 and 1.
		:rtype: float
		"""

		"""
		The tokens are extracted using the same method as in the consumer.
		"""
		tokens = self.tokenizer.tokenize(text)

		"""
		If the text has no tokens, then the score is 0.
		"""
		if not len(tokens):
			return 0

		"""
		If there are tokens in the text, the score is calculated using the formula.
		If there are more tokens than the desired length, the score is capped at 1.
		"""
		return min(math.exp(1 - r/len(tokens)), 1)

	def _emotion_score(self, text, *args, **kwargs):
		"""
		Calculate the emotion in the text.
		This is based on the number of capitalized characters.
		The higher the score, the less emotional the tweet.

		.. note::

			It is not always desirable for the score to be 1.
			That would mean that there is absolutely no capitalization at all.

		:param text: The text to score.
					 The text is tokanized by the function.
		:type text: str

		:return: The emotion score, bounded between 0 and 1.
		:rtype: float
		"""

		upper_pattern = re.compile("[A-Z]")
		lower_pattern = re.compile("[a-z]")
		upper = len(upper_pattern.findall(text))
		lower = len(lower_pattern.findall(text))

		return 1 - upper/(upper + lower) if (upper + lower) else 0
