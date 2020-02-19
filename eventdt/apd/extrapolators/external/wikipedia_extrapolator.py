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

import nltk
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
	:ivar first_level_links: The number of first-level links to retain.
	:vartype first_level_links: int
	:ivar second_level_links: The number of second-level links to retain.
	:vartype second_level_links: int
	"""

	def __init__(self, corpus, tokenizer, scheme, threshold=0, first_level_links=100, second_level_links=1000):
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
		:param first_level_links: The number of first-level links to retain.
		:type first_level_links: int
		:param second_level_links: The index at which the cut-off point of link frequency is taken for the second-level links.
		:type second_level_links: int
		"""

		self.corpus = corpus
		self.tokenizer = tokenizer
		self.scheme = scheme
		self.threshold = threshold
		self.first_level_links = first_level_links
		self.second_level_links = second_level_links

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

		candidates = { }

		"""
		Get the concatenated corpus as a single document, representing the domain.
		This serves as the local context.
		"""
		domain = Document.concatenate(*self.corpus, tokenizer=self.tokenizer, scheme=self.scheme)
		domain.normalize()

		"""
		Create an empty graph.
		This graph will host all resolved participants and candidate participants during extrapolation.
		"""
		graph = nx.Graph()

		"""
		Get the first-level links.
		Then, filter the links to retain only those in the top 100, and those that do not have a year in them.
		Popular links that have already been resolved can be discarded immediately.
		"""
		first_level = links.collect(participants, introduction_only=False, separate=True)
		link_frequency = self._link_frequency(first_level)
		link_frequency = { link: frequency for link, frequency in link_frequency.items() if not self._has_year(self._remove_brackets(link)) }
		link_frequency = sorted(link_frequency.keys(), key=lambda link: link_frequency.get(link), reverse=True)
		frequent_links = [ link for link in link_frequency[:self.first_level_links] if link not in participants ]
		first_level = {
			article: [ link for link in first_level.get(article) if link in frequent_links ]
					   for article in first_level
		}
		self._add_to_graph(graph, first_level, threshold=0)

		"""
		Repeat the process a second time.
		This time, the filter identifies the cut-off at the 1000th most frequent link.
		Once more, articles with a year in the title are excluded.
		Articles that have already been seen are not considered.
		"""
		second_level = links.collect(frequent_links, introduction_only=False, separate=True)
		link_frequency = self._link_frequency(second_level)
		link_frequency = { link: frequency for link, frequency in link_frequency.items() if not self._has_year(self._remove_brackets(link)) }
		cutoff = sorted(link_frequency.values(), reverse=True)[self.second_level_links - 1] if len(link_frequency) >= self.second_level_links else max(link_frequency.values())
		frequent_links = [ link for link in link_frequency if link_frequency.get(link) >= cutoff ]
		frequent_links = [ link for link in frequent_links if link not in list(graph.nodes) ]
		second_level = {
			article: [ link for link in second_level.get(article) if link in frequent_links ]
					   for article in second_level
		}
		self._add_to_graph(graph, second_level, 0.5)

		"""
		Partition the graph into communities.
		The process is repeated until there are fewer than the square root of nodes in the graph.
		Nodes from partitions with at least 3 members are considered to be participants.
		The exceptions are:

			#. nodes that are also normal terms
			#. nodes that have a year in the title
		"""
		communities = community.girvan_newman(graph, most_valuable_edge=self._most_central_edge)
		partitions = list(next(communities))
		while len(partitions) < math.sqrt(len(graph.nodes)):
			partitions = list(next(communities))

		partitions = [ partition for partition in partitions if len(partitions) > 3 ]
		participants = [ node for partition in partitions for node in partition ]
		participants = [ participant for participant in participants if participant.strip().lower() not in words.words() ]
		participants = [ self._remove_brackets(participant) for participant in participants ]
		participants = [ participant for participant in participants if not self._has_year(participant) ]

		"""
		Calculate a score for each candidate participant, retaining those having a score that exceeds the threshold.
		Moreover, exclude candidates that were provided in the resolved participants.
		Return the candidates in descending order of relevance.
		"""
		participants = {
			participant: vector_math.cosine(domain, graph.nodes[participant]['document'])
			for participant in participants
		}
		participants = { participant: score for participant, score in participants.items() if score >= self.threshold }
		participants = sorted(participants.keys(), key=lambda participant: participants.get(participant), reverse=True)
		return participants

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

		if text:
			sentences = nltk.sent_tokenize(text)
			return sentences[0]
		else:
			return text

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
			if source not in documents:
				continue

			if source not in graph.nodes:
				graph.add_node(source, document=documents[source])

			for target in targets:
				if target not in documents:
					continue

				if target not in graph.nodes:
					graph.add_node(target, document=documents[target])

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
