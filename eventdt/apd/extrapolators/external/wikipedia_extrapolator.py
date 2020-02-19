"""
The Wikipedia extrapolator looks for new participants that are tightly-linked with resolved participants.
The extrapolator looks for outgoing links twice.
First, it looks for outgoing links from the resolved participants.
Secondly, it looks for outgoing links from the first set of links.

All of these articles are added to a graph, subject to certain constraints.
The extrapolator uses the Girvan-Newman algorithm to extract communities.
Large communities of tightly-linked articles are considered to be candidate participants.
The most relevant articles in these communities are scored for relevance by the extrapolator.
"""

import asyncio
import math
import os
import re
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

import networkx as nx
from networkx import edge_betweenness_centrality
from networkx.algorithms import community

from nltk.corpus import stopwords, words

from vsm import vector_math
from nlp.document import Document
from nlp.tokenizer import Tokenizer
from wikinterface import info, links, search, text

from ..extrapolator import Extrapolator

class WikipediaExtrapolator(Extrapolator):
	"""
	The Wikipedia extrapolator looks for new participants that are tightly-linked with resolved participants.
	This definition is based on a graph, and communities are extracted using the Girvan-Newman algorithm.

	:ivar corpus: The corpus of documents.
	:vartype corpus: list of :class:`nlp.document.Document`
	:ivar tokenizer: The tokenizer to use to create documents.
	:vartype tokenizer: :class:`nlp.tokenizer.Tokenizer`
	:ivar scheme: The term-weighting scheme to use to create documents from Wikipedia pages.
				  These documents are used to compare the similarity with the domain of the candidates.
	:vartype scheme: :class:`nlp.term_weighting.scheme.TermWeightingScheme`
	:ivar threshold: The similarity threshold beyond which new participants are are added.
	:vartype threshold: float
	"""

	def __init__(self, corpus, tokenizer, scheme, threshold=0):
		"""
		Create the extrapolator.

		:param corpus: The corpus of documents.
		:type corpus: list of :class:`nlp.document.Document`
		:param tokenizer: The tokenizer to use to create documents.
		:type tokenizer: :class:`nlp.tokenizer.Tokenizer`
		:param scheme: The term-weighting scheme to use to create documents from Wikipedia pages.
					   These documents are used to compare the similarity with the domain of the candidates.
		:type scheme: :class:`nlp.term_weighting.scheme.TermWeightingScheme`
		:param threshold: The similarity threshold beyond which new participants are are added.
		:type threshold: float
		"""

		self.corpus = corpus
		self.tokenizer = tokenizer
		self.scheme = scheme
		self.threshold = threshold

	def extrapolate(self, participants, *args, **kwargs):
		"""
		Extrapolate the given participants.

		:param participants: The participants to extrapolate.
							 It is assumed that all participants were resolved using a Wikipedia resolver.
							 This means that all participants share their name with a Wikipedia page.
		:type participants: list of str

		:return: The new participants.
				 These participants are stored as a dictionary.
				 The keys are the resolved participants, and the values are their scores.
		:rtype: list of str
		"""

		extrapolated_participants = { }

		delimiter_pattern = re.compile("^(.+?)\.[\s\n][A-Z0-9]")

		year_pattern = re.compile("[0-9]{4}") # a pattern that indicates a year in the title
		bracket_pattern = re.compile("\(.*?\)")

		"""
		Get the concatenated corpus.
		This serves as the local context.
		"""
		tokenized_corpus = []
		for document in corpus:
			tokens = tokenizer.tokenize(document.get_text())
			document = Document(document.get_text(), tokens, scheme=extrapolator_scheme)
			tokenized_corpus.append(document)
		corpus_document = vector_math.concatenate(tokenized_corpus)
		corpus_document.normalize()

		"""
		Create an empty graph.
		"""
		graph = Graph()
		candidate_nodes = {}
		candidate_pages = {}

		"""
		Get the first level links.
		Only retain those that appear a minimum of times.
		"""
		first_links = link_collector.get_links(candidates, first_section_only=False, separate=True)
		first_links = { page: links for page, links in first_links.items() if len(year_pattern.findall(page)) == 0 } # TODO: Try removing year pattern
		link_popularity = { }
		for link_set in first_links.values():
			for link in link_set:
				link_popularity[link] = link_popularity.get(link, 0) + 1
		link_popularity = sorted(link_popularity.items(), key=lambda x:x[1])[::-1]
		next_pages = [ link for link, _ in link_popularity if link not in first_links.keys() ][:100]
		candidate_pages.update(self.get_candidate_pages(list(first_links.keys()) + next_pages, extrapolator_scheme))

		"""
		Create the representation for the pages.
		Initially, this is made up of the candidates and popular outgoing links in these candidates.
		"""

		first_links = { page: [ link for link in first_links[page] if link in next_pages ] for page in first_links }
		for candidate, links in first_links.items():
			""""
			Create the nodes and edges, this time using the first-level links.
			"""
			node = Node(candidate)
			candidate_nodes[candidate] = node
			graph.add_node(node)

			for page in links:
				if page not in candidate_nodes:
					"""
					If the page does not have a node, create one for it.
					"""
					node = Node(page)
					candidate_nodes[page] = node
					graph.add_node(node)
					if candidate not in candidate_pages:
						logger.warning("%s has no representation" % candidate)
						continue
					if page not in candidate_pages:
						logger.warning("%s has no representation" % page)
						continue
					similarity = vector_math.cosine(candidate_pages[candidate], candidate_pages[page])
					if similarity > 0:
						graph.add_edge(node, candidate_nodes[candidate], 1 - similarity)

		"""
		Repeat the process a second time.
		"""
		second_links = link_collector.get_links(next_pages, first_section_only=False, separate=True)
		second_links = { page: links for page, links in second_links.items() if len(year_pattern.findall(page)) == 0 }
		link_popularity = { }
		for link_set in second_links.values():
			for link in link_set:
				link_popularity[link] = link_popularity.get(link, 0) + 1

		cutoff = 1
		second_links = { page: [ link for link in second_links[page] if link_popularity[link] >= cutoff ] for page in second_links }
		unique_links = set([ link for links in second_links.values() for link in links ])
		while len(unique_links) > 1000:
			second_links = { page: [ link for link in second_links[page] if link_popularity[link] > cutoff ] for page in second_links }
			unique_links = set([ link for links in second_links.values() for link in links ])
			cutoff += 1
		logger.info("Graph to be created with a popularity cut-off of %d" % (cutoff - 1))

		"""
		Create the representations of the the new pages.
		"""
		new_pages = list(set([ link for page in second_links for link in second_links[page] if link not in candidate_pages ]))
		candidate_pages.update(self.get_candidate_pages(new_pages + list(second_links.keys()), extrapolator_scheme))

		for source, links in second_links.items():
			""""
			Create the nodes and edges, this time using the second-level links.
			"""
			if source not in candidate_nodes:
				"""
				The source page may not always have a node - this could happen because of redirections.
				"""
				node = Node(source)
				candidate_nodes[source] = node
				graph.add_node(node)

			"""
			Visit each target link and create a node for it if need be.
			Then, add an edge from the source page to this page.
			"""
			for target in links:
				if (len(year_pattern.findall(target)) == 0
					and not target.lower().startswith("list of")):

					if target not in candidate_nodes:
						node = Node(target)
						candidate_nodes[target] = node
						graph.add_node(node)
					else:
						node = candidate_nodes[target]

					if source not in candidate_pages:
						# logger.warning("%s has no representation" % source)
						continue
					if target not in candidate_pages:
						# logger.warning("%s has no representation" % target)
						continue
					similarity = vector_math.cosine(candidate_pages[source], candidate_pages[target])
					if similarity > 0.5:
						graph.add_edge(node, candidate_nodes[source], 1 - similarity)

		"""
		Create a networkx graph and use it to partition the pages.
		"""
		nx_graph = graph.to_networkx()
		communities = community.girvan_newman(nx_graph, most_valuable_edge=self._most_central_edge)
		top_level_partitions = list(next(communities))

		"""
		Get the nodes from the biggest partitions.
		"""
		new_candidates = []
		for i, partition in enumerate(top_level_partitions):
			subgraph = nx_graph.subgraph(partition)
			if len(partition) > 3:
				nodes = [ nx_graph.node[node]["name"] for node in partition ]
				new_candidates.extend(nodes)


		"""
		Retain the candidates having a minimum score.
		Moreover, exclude candidates that were provided in the seed set - they're already known to exist.
		From these candidates, return only the top ones.
		"""
		extrapolated_participants = { candidate: vector_math.cosine(corpus_document, candidate_pages[candidate]) for candidate in new_candidates if candidate in candidate_pages }
		extrapolated_participants = { bracket_pattern.sub(' ', candidate): score for candidate, score in extrapolated_participants.items() if candidate not in candidates }
		extrapolated_participants = { candidate: score for candidate, score in extrapolated_participants.items() if score >= extrapolator_threshold }
		extrapolated_participants = { candidate: score for candidate, score in extrapolated_participants.items() if candidate.strip().lower() not in words.words() }
		extrapolated_participants = { candidate.strip(): score for candidate, score in extrapolated_participants.items() if len(year_pattern.findall(candidate)) == 0 } # exclude candidates that have a year in the title
		extrapolated_participants = sorted(extrapolated_participants.items(), key=lambda x:x[1])[:-1 * (extrapolator_participants + 1):-1]
		return [ candidate for candidate, _ in extrapolated_participants ]

	def _has_year(self, title):
		"""
		Check whether the given title has a year in it.

		:param title: The title of the article.
		:type title: str

		:return: A boolean indicating whether the title includes a year in it.
		:rtype: bool
		"""

		year_pattern = re.compile("\\b[0-9]{4}\\b")
		return len(year_pattern.findall(title)) > 0

	def _remove_brackets(self, text):
		"""
		Remove brackets from the given text.

		:param text: The text from which to remove brackets.
		:type text: str

		:return: The text without any components in the brackets.
		:rtype: str
		"""

		bracket_pattern = re.compile("\(.*?\)")
		return bracket_pattern.sub(' ', text)

	def _get_first_sentence(self, text):
		"""
		Get the first sentence from the given text.

		:param text: The text from which to extract the first sentence.
		:type text: str

		:return: The first sentence from the given text.
		:rtype: str
		"""

		sentences = nltk.sent_tokenize(text)
		return sentences[0]

	def _link_frequency(self, articles):
		"""
		Count the link frequency in the given set.

		:param articles: The dictionary of articles with their outgoing links.
						 The keys are the article titles.
						 The values are the outgoing links.
		:type articles: dict

		:return: A dictionary of the outgoing links (the values of the dictionary).
				 The keys are the outgoing links.
				 The values are the frequency across all articles.
		:rtype: dict
		"""

		outgoing_links = [ link for link_set in articles.values() for link in link_set ]
		return { link: outgoing_links.count(link) for link in set(outgoing_links) }

	def _add_to_graph(self, graph, outgoing_links, threshold=0):
		"""
		Add the links to the graph.
		The function fetches the article text and uses it to add to the weighted graph.

		.. note::

			The weight of edges is `1 - similarity`.
			The higher the similarity, the less weight.
			Therefore more paths go through that edge.

		:param graph: The graph to which to add the new nodes and edges.
		:type graph: :class:`nx.Graph`
		:param outgoing_links: The dictionary of links.
							   The keys should be the source articles.
							   The values should be the outgoing links from these articles.
		:type outgoing_links: dict
		:param threshold: The minimum similarity between the source and target articles to add an edge between them.
		:type threshold: float
		"""

		"""
		Get the text from all articles.
		"""
		sources = list(outgoing_links.keys())
		targets = [ link for link_set in outgoing_links.values() for link in link_set ]
		articles = text.collect(sources + targets, introduction_only=True)

		"""
		Convert each article into a document.
		The article is based only on the first sentence.
		"""
		documents = { }
		for title, introduction in articles.items():
			introduction = self._remove_brackets(introduction)
			introduction = self._get_first_sentence(introduction)
			document = Document(introduction, self.tokenizer.tokenize(introduction),
								scheme=self.scheme)
			document.normalize()
			documents[title] = document

		"""
		Add first the nodes, and then the edges to the graph.
		This is done by going through all the outgoing links.
		If they have a page, the similarity between the source article and that link is computed.
		If the similarity exceeds the threshold, add an edge between the two.
		"""
		for source, targets in outgoing_links.items():
			if source not in graph.nodes:
				graph.add_node(source)

			for target in targets:
				if target not in graph.nodes and target in documents:
					graph.add_node(target)

				if source in documents and target in documents:
					similarity = vector_math.cosine(documents[source], documents[target])
					if similarity > threshold:
						graph.add_edge(source, target, weight=(1 - similarity))

	def _most_central_edge(self, G):
		"""
		Find the most central edge in the given graph.
		The algorithm uses NetworkX's betweenness centrality, but it is based on weight.
		The lower the weight, the more shortest paths could go through it.

		:param G: The graph on which the algorithm operates.
		:type G: :class:`networkx.Graph`

		:return: The most central edge, made up of the source and edge nodes.
		:rtype: tuple
		"""

		centrality = edge_betweenness_centrality(G, weight='weight')
		edge = max(centrality, key=centrality.get)
		return edge
