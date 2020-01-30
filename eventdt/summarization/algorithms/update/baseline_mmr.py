"""
Implementation of the baseline MMR (unpublished).
It is based on Carbonell and Goldstein's MMR (1998).
"""

import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '../../../')
if path not in sys.path:
	sys.path.insert(1, path)

from .fragmented_summarizer import FragmentedUpdateSummarization
from .. import mmr
from ...scorers import scorer
from ...summary import Summary

from logger import logger

from vector import vector_math
from vector.nlp.cleaners import tweet_cleaner
from vector.cluster.cluster import Cluster
from vector.nlp.document import Document

class BaselineMMR(FragmentedUpdateSummarization):
	"""
	A summarizer that takes in emerging terms and clusters to create summaries.
	The summarization module is a class because it is state-full.
	It remembers recent emerging terms to churn out incremental updates.

	Central to the FragmentedMMR is the assumption that temporally-close emerging terms are related.
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
	:ivar _frozen_summaries: A list containing frozen tuples representing old summaries.
		These tuples are made up of the clusters used to create the summaries, and the summaries themselves.
		The clusters are actually a list of tuples, similarly to the `_clusters` variable.
	:vartype _frozen_summaries: list
	:ivar time_window: The length of the time window (in seconds).
		This time window is used to determine how long a summary may go without update for the topic to be deemed over.
		:vartype _scorer: :class:`summarization.scorers.scorer.Scorer`
	:vartype time_window: int
	"""

	def __init__(self, time_window=120, scorer=scorer.Scorer, *args, **kwargs):
		"""
		Create the containers for the current summary and finished summaries.
		The current summary contains containers for the clusters and the timestamp when it was last updated.

		:param time_window: The time window (in seconds) to consider breaking topics to be semantically-related.
		:type time_window: int
		:param scorer: The type of scorer used to rank documents.
			By default, no scoring is employed.
		:type scorer: :class:`summarization.scorers.scorer.Scorer`
		"""

		super().__init__(time_window)

		self._scorer = scorer()

	def add_cluster(self, cluster, breaking_terms, timestamp, wait_period=90, summarization_min_score=0, *args, **kwargs):
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

		if self._is_inactive(timestamp):
			"""
			If the current summary is old, retire it and create a new one.
			"""
			self._initialize(timestamp, cleaner=tweet_cleaner.TweetCleaner, min_score=summarization_min_score)

		"""
		Compare the new cluster with old summaries.
		If the cluster is not novel enough in breaking content, do not process it.
		"""
		cluster_set, similarity = self._check_novelty(cluster)
		novel = similarity < 0.6
		if similarity > 0.6:
			cluster_set.append(cluster)

		if novel and (timestamp - self._summary.created_at() > wait_period):
			"""
			If the new development is vastly different from the current one, create a new summary.
			Create a representation of the current development and compare it with the new update.
			"""
			current_development = self._current_development.get_centroid()

			"""
			Calculate the similarity between the current summary and the new development.
			If the similarity is too low, and the summary is not new, it is an indication that there has been a major shift in focus.
			If this happens, the old summary should be retired.
			"""
			similarity = vector_math.cosine(current_development, cluster.get_centroid())
			if similarity < 0.1:
				self._initialize(timestamp, cleaner=tweet_cleaner.TweetCleaner, min_score=summarization_min_score)

		"""
		Only include this cluster if it is novel.
		"""
		if novel:
			"""
			If the summary is empty, re-create it to update the creation timestamp.
			"""
			if len(self._clusters) == 0:
				self._initialize(timestamp, cleaner=tweet_cleaner.TweetCleaner, min_score=summarization_min_score)

			self._clusters.append((breaking_terms, cluster, ))
			self._current_development.add_vectors(cluster.get_vectors())
			self._summary.set_last_updated(timestamp)

	def create_summary(self, *args, **kwargs):
		"""
		Generate a summary from the documents comprising the development.

		:return: A summary.
		:rtype: :class:`summarization.summary.Summary`
		"""

		if len(self._clusters) > 0:
			"""
			Create a query, based on all clusters. Naturally, this should only happen if there are clusters in the summary.
			One possible explanation why there are no clusters is if the summary is new, but the cluster was judged to be too similar to a previous development.
			"""
			query = self._create_query(self._clusters)

			"""
			Compile the collection of documents, but retain only the top documents.
			"""
			collection = [ document for _, cluster in self._clusters
				for document in cluster.get_vectors() ]

			collection = sorted(collection, key=lambda x: self._scorer.score(x))[-25:]

			"""
			Generate a summary using MMR.
			"""
			generated_summary = mmr.MMR(collection, query, document_scorer=self._scorer, *args, **kwargs)

			"""
			Clean up and update the summary.
			"""
			self._summary.set_documents(generated_summary.get_documents())
			return self._summary

	def _create_query(self, clusters):
		"""
		Create a query from the given clusters.
		The query is used to summarize the documents, identifying the most important aspects in them.

		The query is made up of all the breaking terms found in the clusters.
		It is later used to score documents; those which are similar to the query are weighted more.
		In the end, the cluster's centroid is used as the query.

		The individual documents making up the cluster are re-created each time.
		This approach is adopted since the cluster may change over time, and so would its size.

		:param clusters: The list of cluster from which to create the query.
		:type cluster: list

		:return: The summarization query.
		:rtype: :class:`vector.nlp.document.Document`
		"""

		query = Cluster()
		for _, cluster in clusters:
			query.add_vectors(cluster.get_vectors())
		query = query.get_centroid()
		query.normalize()
		return query
