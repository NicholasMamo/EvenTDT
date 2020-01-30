"""
Implementation of Mamo et al.'s time-aware document graph summarization method (unpublished).
"""

from datetime import datetime

import json
import math
import os
import re
import sys
import time

path = os.path.dirname(__file__)
path = os.path.join(path, '../../../')
if path not in sys.path:
	sys.path.insert(1, path)

import networkx as nx
from networkx import edge_betweenness_centrality
from networkx.algorithms import centrality, community

from .fragmented_summarizer import FragmentedUpdateSummarization
from .. import mmr
from ...scorers import scorer, tweet_scorer
from ...summary import Summary

from graph.graph import Graph, Node

from logger import logger

from vector import vector_math
from vector.cluster.cluster import Cluster

from vector.nlp.cleaners import tweet_cleaner
from vector.nlp.document import Document
from vector.nlp.term_weighting import TF
from vector.nlp.tokenizer import Tokenizer

class DocumentGraphSummarizer(FragmentedUpdateSummarization):
	"""
	A summarizer that is based on a document graph.
	In the document graph, documents are represented as nodes.
	The edges are weighted according to the cosine similarity between documents.
	An edge exist if the weight is bigger than zero.

	The summarizer does not discriminate betewen documents from different clusters.
	Instead, it adds all documents to the same graph.

	This is based on the assumption that documents in different clusters may still be very similar.
	Therefore graph partitioning methods are used to find the new clusters.
	From these partitions, the most central documents are chosen.

	The advantage of this approach is that there are fewer parameters.

	:ivar _scorer: The scorer that is used to evaluate documents.
	:vartype _scorer: :class:`summarization.scorers.scorer.Scorer`
	:ivar _tokenizer: The tokenizer that is used to re-create sentences.
	:vartype _tokenizer: :class:`vector.nlp.tokenizer.Tokenizer`
	:ivar _scheme: The scheme that is used to convert the tokens into dimensions.
	:vartype _scheme: :class:`vector.nlp.TermWeighting`
	"""

	def __init__(self, time_window=120, scorer=scorer.Scorer, tokenizer=None, scheme=None, output_file=None):
		"""
		Create the containers for the current summary and finished summaries.
		The current summary contains containers for the clusters and the timestamp when it was last updated.

		:param time_window: The time window (in seconds) to consider breaking topics to be semantically-related.
		:type time_window: int
		:param scorer: The type of scorer used to rank documents.
			By default, no scoring is employed.
		:type scorer: :class:`summarization.scorers.scorer.Scorer`
		:param tokenizer: The tokenizer that is used to re-create sentences.
		:type tokenizer: :class:`vector.nlp.tokenizer.Tokenizer`
		:param scheme: The scheme that is used to convert the tokens into dimensions.
		:type scheme: :class:`vector.nlp.TermWeighting`
		:param output_file: A file handle that is used to write information.
		:type output_file: file
		"""

		super().__init__(time_window)

		self._scorer = scorer()
		self._tokenizer = tokenizer if tokenizer is not None else Tokenizer()
		self._scheme = scheme if scheme is not None else TF()
		self._output_file = output_file

	def add_cluster(self, cluster, breaking_terms, timestamp, wait_period=90):
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
		:param wait_period: The period to wait (in seconds) before considering retiring developments.
			It is assumed that this is shorter than the time window.
		:type wait_period: int
		"""

		self.ping(timestamp)

		"""
		Compare the new cluster with old summaries.
		If the cluster is not novel enough in breaking content, do not process it.
		"""
		cluster_set, similarity = self._check_novelty(cluster)
		novel = similarity < 0.6
		if similarity > 0.6:
			cluster_set.append((breaking_terms, cluster))

		# logger.info("%s: %f" % (datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
		# 	similarity))

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
				self._initialize(timestamp, cleaner=tweet_cleaner.TweetCleaner)

		"""
		Only include this cluster if it is novel.
		"""
		if novel:
			"""
			If the summary is empty, re-create it to update the creation timestamp.
			"""
			if len(self._clusters) == 0:
				self._initialize(timestamp, cleaner=tweet_cleaner.TweetCleaner)

			self._clusters.append((breaking_terms, cluster, ))
			self._current_development.add_vectors(cluster.get_vectors())
			self._summary.set_last_updated(timestamp)

	def create_summary(self, *args, **kwargs):
		"""
		Generate a summary from the documents comprising the development.

		:return: A summary.
		:rtype: :class:`summarization.summary.Summary`
		"""

		sentence_split_pattern = re.compile(".+?[.?!\n]")
		graph = Graph()

		if len(self._clusters) > 0:
			"""
			Create a query, based on all clusters. Naturally, this should only happen if there are clusters in the summary.
			One possible explanation why there are no clusters is if the summary is new, but the cluster was judged to be too similar to a previous development.
			"""
			query = self._create_query(self._clusters)

			"""
			Compile the collection of documents that are new.
			Only retain documents if they were added since the last timestamp, or they do not have a node ID associated with them.
			"""
			scorer = tweet_scorer.TweetScorer()
			documents = [ document for _, cluster in self._clusters
				for document in cluster.get_vectors()]
			documents = sorted(documents, key=lambda x: scorer.score(x))[-25:]

			"""
			If there are a few documents and more than a single cluster, create a graph based on sentences, instead of documents.
			"""
			if False and len(documents) > 10 and len(self._clusters) > 1:
				sentences = []

				for document in documents:
					document_sentences = sentence_split_pattern.findall(document.get_attribute("text"))
					document_sentences = [ Document(sentence.strip(), self._tokenizer.tokenize(sentence),
						{ "tokens": self._tokenizer.tokenize(sentence) },
						scheme=self._scheme) for sentence in document_sentences
					]
					document_sentences = [ sentence for sentence in document_sentences if len(sentence.get_dimensions()) > 0 ]
					sentences.extend(document_sentences)

				documents = sentences
				documents = sorted(documents, key=lambda x: scorer.score(x))[:-26:-1]

			"""
			Create a new node for each new document.
			"""
			for document in documents:
				node = Node()
				node.set_attribute("document", document)
				document.set_attribute("node_id", node.get_id())
				graph.add_node(node)

				"""
				Create edges between the new node and any other nodes that are already in the graph.
				Only create an edge if the similarity is not zero.
				"""
				for other in graph.get_nodes():
					if other is not node:
						similarity = vector_math.cosine(document, other.get_attribute("document"))
						if similarity > 0.3:
							graph.add_edge(node, other, 1 - similarity)

			"""
			Generate a summary by partitioning the graph.
			Only reasonably-large subgraphs are retained.
			However, if no sizeable subgraphs are found, get the largest partition anyway.
			"""
			nx_graph = graph.to_networkx()
			i, top_level_partitions = 0, []
			top_level_partitions = next(community.girvan_newman(nx_graph, most_valuable_edge=self._most_central_edge))

			if max([ len(partition) for partition in top_level_partitions ]) > 2:
				top_level_partitions = [ partition for partition in top_level_partitions if len(partition) > 2 ]
			else:
				top_level_partitions = [ max(top_level_partitions, key=lambda x: len(x)) ]

			"""
			Select one representative node from each partition.
			"""
			summary_documents = []
			for i, partition in enumerate(top_level_partitions):
				subgraph = nx_graph.subgraph(partition)
				node_scores = {} # the score of each node
				centrality_scores = centrality.eigenvector_centrality(subgraph) # calculate the centrality of nodes
				for node in partition:
					document = nx_graph.node[node]["document"]
					query_score = vector_math.cosine(query, document)
					quality_score = self._scorer.score(document)
					node_scores[node] = query_score * quality_score * centrality_scores[node]
				summary_documents.append(nx_graph.node[max(node_scores.items(), key=lambda x: x[1])[0]]["document"])

			"""
			Clean up and update the environment.
			"""
			self._summary.set_documents(summary_documents)

		if self._output_file is not None:
			array = graph.to_array()
			for node in array["nodes"]:
				array["nodes"][node]["document"] = array["nodes"][node]["document"].get_text()
			self._output_file.write("%s\n" % json.dumps(array))

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
		for breaking_terms, cluster in clusters:
			document = Document("", { term: weight * cluster.size() for term, weight in breaking_terms })
			query.add_vector(document)
		query = query.get_centroid()
		query.normalize()
		return query

	def _most_central_edge(self, G):
		"""
		Find the most central edge in the given graph.
		The algorithm uses NetworkX's betweenness centrality and is based on weight.
		The lower the weight, the more shortest paths could go through it.

		:param G: The graph on which the algorithm operates.
		:type G: :class:`networkx.Graph`

		:return: The most central edge, made up of the source and edge nodes.
		:rtype: tuple
		"""

		centrality = edge_betweenness_centrality(G, weight='weight')
		edge = max(centrality, key=centrality.get)
		return edge
