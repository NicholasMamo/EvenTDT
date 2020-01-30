"""
The general concept of an update summarization algorithm.
This idea is also described as incremental summarization.
"""

from datetime import datetime

from abc import ABC, abstractmethod
import math
import os
import re
import sys
import time

path = os.path.dirname(__file__)
path = os.path.join(path, '../../../')
if path not in sys.path:
	sys.path.insert(1, path)

from .. import mmr
from ...scorers import scorer
from ...summary import Summary

from logger import logger

from vector import vector_math
from vector.nlp.cleaners import tweet_cleaner
from vector.cluster.cluster import Cluster
from vector.nlp.document import Document

class FragmentedUpdateSummarization(ABC):
	"""
	A summarizer that generates summaries that are mindful of what the reader has seen before.
	It assumes that the user is only interested in updates that they have not encountered yet.

	The update summarizer that takes in emerging terms and clusters to create summaries.
	The summarization module is a class because it is state-full.
	It remembers recent emerging terms to churn out incremental updates.

	Central to the update summarization is the assumption that temporally-close emerging terms are related.
	Incoming clusters are added to the most recent summary if one is available.
	Otherwise, if there have been no recent developments, a new summary is created.
	Once a summary has not been updated in the past time window, it is retired and no longer updated.

	:ivar _clusters: A list of clusters that make up the current summary.
		This is a tuple, made up of the emerging terms and the associated clusters.
	:vartype _clusters: list
	:ivar _summary: The last generated summary.
		This summary is still a work in progress.
		Once it is complete, it is added to the finished summaries.
	:vartype _summary: :class:`summarization.summary.Summary`
	:ivar _current_development: A cluster representing the current development.
	:vartype _current_development: :class:`vector.cluster.cluster.Cluster`
	:ivar _frozen_summaries: A list containing frozen triples representing old summaries.
		These tuples are made up of the clusters used to create the summaries, the summaries themselves, and a development representation.
		The clusters are actually a list of tuples, similarly to the `_clusters` variable.
	:vartype _frozen_summaries: list
	:ivar _time_window: The length of the time window (in seconds).
		This time window is used to determine how long a summary may go without update for the topic to be deemed over.
	:vartype _time_window: int
	"""

	def __init__(self, time_window=60, scorer=scorer.Scorer):
		"""
		Create the containers for the current summary and finished summaries.
		The current summary contains containers for the clusters and the timestamp when it was last updated.

		:param time_window: The time window (in seconds) to consider breaking topics to be semantically-related.
		:type time_window: int
		:param scorer: The type of scorer used to rank documents.
			By default, no scoring is employed.
		:type scorer: :class:`summarization.scorers.scorer.Scorer`
		"""

		self._time_window = time_window

		self._clusters = []
		self._summary = Summary()
		self._frozen_summaries = []
		self._scorer = scorer()

	@abstractmethod
	def add_cluster(self, cluster, breaking_terms, timestamp, summarization_min_score=0, *args, **kwargs):
		"""
		Add a cluster to the summary.

		The cluster is accompanied with tuples representing breaking terms.
		These tuples contain not only the breaking term, but its emergence.

		The generated summary gives more importance to terms that are emerging powerfully.

		:param breaking_terms: Tuples that represent the breaking terms.
			The tuples are made up of the actual terms, and their emergence score.
		:type breaking_terms: list
		:param cluster: The cluster within which the breaking terms were found.
			Its documents will be used to create the summaries.
		:type cluster: :class:`vector.cluster.cluster.Cluster`
		:param timestamp: The timestamp when the cluster is being added.
		:type timestamp: int
		:param min_score: The minimmum score that is required to add a document to a summary.
			Since cosine similarity is used, this threshold is bounded between -1 and 1.
		:type min_score: float
		"""

		pass

	@abstractmethod
	def create_summary(self):
		"""
		Generate a summary from the documents comprising the development.

		:return: A summary.
		:rtype: :class:`summarization.summary.Summary`
		"""

		pass

	def _initialize(self, timestamp=0, *args, **kwargs):
		"""
		Initialize the summary.

		:param timestamp: The timestamp when the summary was created.
		:type timestamp: int
		"""

		"""
		If the current summary is old and not empty, retire it and create a new one.
		The summary is only saved if it is incremental.
		"""
		if len(self._clusters) > 0:
			self.create_summary(*args, **kwargs)
			incremental_summary = self._is_incremental(self._summary, *args, **kwargs)
			summary_score = sum([ self._scorer.score(document) for document in incremental_summary.get_documents() ])
			"""
			Only save a summary if it is non-empty and not a near-duplicate of a previous summary.
			"""
			if len(incremental_summary.get_documents()) > 0 and summary_score > 0.5:
				self._frozen_summaries.append((self._clusters, self._summary, self._current_development ))
				logger.info("%s %d: %s" % (datetime.fromtimestamp(self._summary.created_at()).strftime('%Y-%m-%d %H:%M:%S'),
					len(self._frozen_summaries),
					self._summary.generate_summary(*args, **kwargs)))
			else:
				pass
				# logger.warning("EXCLUDED AT %s: %s" % (datetime.fromtimestamp(self._summary.created_at()).strftime('%Y-%m-%d %H:%M:%S'),
				# 	self._summary.generate_summary(*args, **kwargs)))

		"""
		The first summary needs a date. Therefore it should always be created.
		"""
		self._summary = Summary([], timestamp)
		self._clusters = []
		self._current_development = Cluster()

	def _check_novelty(self, cluster, consider=-1):
		"""
		Check whether the given cluster represents a new development or a continuation of an older one.
		This serves as the tracking step to ensure tht the summarization is an actual update.

		:param cluster: The cluster within which the breaking terms were found.
		:type cluster: :class:`vector.cluster.cluster.Cluster`
		:param consider: The number of previous developments to consider.
			If it is negative, all developments are considered.
		:type consider: int

		:return: A tuple containing the list of clusters from the most similar development and the corresponding similarity.
		:rtype: tuple
		"""

		if len(self._frozen_summaries) > 0:
			similarities = []
			consider = consider if consider > 0 else len(self._frozen_summaries)

			"""
			Compute the similarity between the given cluster and each development.
			"""
			for i, (clusters, summary, development) in enumerate(self._frozen_summaries[:-(consider + 1):-1]):
				similarity = vector_math.cosine(development.get_centroid(), cluster.get_centroid())
				similarities.append((clusters, similarity))

			return max(similarities, key=lambda x:x[1])
		else:
			return ([], 0)

	def _is_incremental(self, proposed_summary, threshold=0.7, consider=-1, *args, **kwargs):
		"""
		Check whether the given summary provides novel information based only on lexical information.
		The comparisons are based on cosine similarity.

		:param proposed_summary: The summary to check
		:type proposed_summary: :class:`summarization.summary.Summary`
		:param threshold: The maximum similarity threshold to consider a summary to be novel.
			If the similarity with any previous development is higher than the threshold, it is not novel.
		:type threshold: float
		:param consider: The number of previous developments to consider.
			If it is negative, all developments are considered.
		:type consider: int

		:return: A new summary without documents that are repeated.
		:rtype: :class:`summarization.summary.Summary`
		"""

		retained_documents = []

		consider = consider if consider > 0 else len(self._frozen_summaries)
		for document in proposed_summary.get_documents():
			max_similarity = 0
			for i, (_, summary, _) in enumerate(self._frozen_summaries[:-(consider + 1):-1]):
				for summary_document in summary.get_documents():
					similarity = vector_math.cosine(document, summary_document)
					max_similarity = max(similarity, max_similarity)

			if max_similarity < threshold:
				retained_documents.append(document)
			else:
				pass
				# logger.warning("Filtered out document from summary (%f): %s" % (max_similarity, document.get_text()))

		proposed_summary.set_documents(retained_documents)
		return proposed_summary

	def _is_inactive(self, timestamp):
		"""
		Check if the current summary has been inactive far too long.

		:param timestamp: The current timestamp, which is compared with the
		:type timestamp: int
		"""

		return timestamp - self._summary.last_updated() > self._time_window

	def ping(self, timestamp):
		"""
		Retire a summary if it has expired.

		:param timestamp: The current timestamp.
		:type timestamp: int
		"""

		if self._is_inactive(timestamp):
			"""
			If the current summary is old, retire it and create a new one.
			"""
			self._initialize(timestamp, cleaner=tweet_cleaner.TweetCleaner)

	def get_summary(self):
		"""
		Get the currently-active summary.

		:return: The currently-active summary.
		:rtype _summary: :class:`summarization.summary.Summary`
		"""

		return self._summary

	def is_active_summary(self):
		"""
		Check whether there is a currently-active summary.
		A summary is active if it has clusters in it.

		:return: A boolean indicating whether there is a currently-active summary.
		:rtype: bool
		"""

		return len(self._clusters) > 0

	@abstractmethod
	def _create_query(self, clusters):
		"""
		Create a query from the given clusters.
		The query is used to summarize the documents, identifying the most important aspects in them.

		:param clusters: The list of cluster from which to create the query.
		:type cluster: list

		:return: The summarization query.
		:rtype: :class:`vector.nlp.document.Document`
		"""

		pass

	def export_timeline(self):
		"""
		Export the timeline that was generated by the summarizer.
		The timeline is only made up of summaries.

		:return: A list of :class:`summarization.summary.Summary` instances.
		:rtype: list
		"""

		return [ summary for _, summary, _ in self._frozen_summaries ]

	def export_raw_timeline(self):
		"""
		Export the timeline's clusters.
		These clusters are the raw ingredients to clusters, and can be used to generate new summaries.

		Note that adding each individual cluster sequentially might produce different results from the original timeline.
		Clusters remain active, and therefore the summaries generated in this way consider the new documents as well.
		Old nodes could even attract new clusters.
		This change in summary make-up could cancel out summaries that come after, possibly changing the number of nodes.

		:return: A list of lists of :class:`vector.cluster.cluster.Cluster` instances.
			The top-most levels represent each node on the timeline.
		:rtype: list
		"""

		return [ (clusters, summary.created_at()) for clusters, summary, _ in self._frozen_summaries ]
