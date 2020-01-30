"""
An extrapolator that uses Wikipedia's links as the basis for semantic similarity.
"""

import asyncio
import math
import os
import re
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '../../../')
if path not in sys.path:
	sys.path.append(path)

import networkx as nx
from networkx import edge_betweenness_centrality
from networkx.algorithms import centrality, community

from nltk.corpus import stopwords
from nltk.corpus import words

from graph.graph import Graph, Node

from logger import logger

from vector import vector_math

from vector.nlp.document import Document
from vector.nlp.tokenizer import Tokenizer

from wikinterface.info_collector import InfoCollector, PageType
from wikinterface.linkcollector import LinkCollector
from wikinterface.searchcollector import SearchCollector
from wikinterface.textcollector import TextCollector

from ..extrapolator import Extrapolator

class LinkExtrapolator(Extrapolator):
	"""
	The link extrapolator creates a graph and uses the graph to find participants.
	"""

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

	def _heaviest_edge(self, G):
		"""
		Find the heaviest edge in the given graph.
		The algorithm uses the base weight and removes the heaviest - or most strenuous - one

		:param G: The graph on which the algorithm operates.
		:type G: :class:`networkx.Graph`

		:return: The heaviest edge, made up of the source and edge nodes.
		:rtype: tuple
		"""

		weight = { (source, target): weight for source, target, weight in G.edges(data="weight", default=1) }
		edge = max(weight, key=weight.get)
		return edge

	def extrapolate(self, candidates, corpus, extrapolator_scheme, extrapolator_participants=10, extrapolator_threshold=0, token_attribute="tokens", *args, **kwargs):
		"""
		Extrapolate the given candidates.

		:param candidates: The candidates to extrapolate.
			It is assumed that all of the given candidates were resolved using :class:`apd.resolvers.external.wikipedia_resolver.WikipediaResolver`.
			This means that all candidates share their name with a Wikipedia page.
		:type candidates: list
		:param corpus: The corpus of documents, which helps to isolate relevant candidates.
		:type corpus: list
		:param extrapolator_scheme: The term weighting scheme used to create the local and external contexts.
		:type extrapolator_scheme: :class:`vector.nlp.term_weighting.TermWeighting`
		:param extrapolator_participants: The number of extrapolated participants to retrieve.
		:type extrapolator_participants: int
		:param extrapolator_threshold: The minimum score of the extrapolated participant to be considered.
		:type extrapolator_threshold: float
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: The new candidates.
			These candidates are stored as a dictionary.
			The keys are the resolved candidates, and the values are their scores.
		:rtype: dict
		"""

		extrapolated_candidates = { }

		info_collector = InfoCollector()
		link_collector = LinkCollector()
		tokenizer = Tokenizer(stopwords=stopwords.words("english"))
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

		# IDEA: Choose links based on similarity to corpus; the problem is that pages like `Arsenal TV` would have a high similarity with `Arsenal`, and the communities would be flooded like this
		# all_links = [ link for page in first_links for link in first_links[page] ]
		# candidate_pages.update(self.get_candidate_pages(list(first_links.keys()) + all_links, extrapolator_scheme))
		# page_similarities = { page: vector_math.cosine(candidate_pages[page], corpus_document) for page in all_links if page in candidate_pages }
		# next_pages = sorted(page_similarities.items(), key=lambda x:x[1])[-51:]
		# next_pages = [ page for page, _ in next_pages ]

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
		# logger.info("%d nodes in the graph" % graph.size())
		# communities = community.girvan_newman(nx_graph)
		logger.info("Graph converted with %d nodes" % graph.size())
		communities = community.girvan_newman(nx_graph, most_valuable_edge=self._most_central_edge)
		top_level_partitions = list(next(communities))
		logger.info("Communities found")
		# i = 0
		# while ((len(top_level_partitions) <= math.sqrt(graph.size()) # if there are too few partitions
		# 		or max([ len(partition) for partition in top_level_partitions ]) >= math.sqrt(graph.size())) # if the largest partition is very large
		# 	and i < 10):
		# 	top_level_partitions = list(next(communities))
		# 	if len(top_level_partitions) > 0:
		# 		logger.info("%d: %d partitions (largest: %d nodes)" % (i + 1, len(top_level_partitions), max([ len(partition) for partition in top_level_partitions ])))
		# 	i += 1

		"""
		Get the nodes from the biggest partitions.
		"""
		new_candidates = []
		for i, partition in enumerate(top_level_partitions):
			subgraph = nx_graph.subgraph(partition)
			if len(partition) > 3:
				nodes = [ nx_graph.node[node]["name"] for node in partition ]
				new_candidates.extend(nodes)
				logger.info("Partition %d: %d nodes" % (i + 1, len(partition)))


		"""
		Retain the candidates having a minimum score.
		Moreover, exclude candidates that were provided in the seed set - they're already known to exist.
		From these candidates, return only the top ones.
		"""
		extrapolated_candidates = { candidate: vector_math.cosine(corpus_document, candidate_pages[candidate]) for candidate in new_candidates if candidate in candidate_pages }
		extrapolated_candidates = { bracket_pattern.sub(' ', candidate): score for candidate, score in extrapolated_candidates.items() if candidate not in candidates }
		extrapolated_candidates = { candidate: score for candidate, score in extrapolated_candidates.items() if score >= extrapolator_threshold }
		extrapolated_candidates = { candidate: score for candidate, score in extrapolated_candidates.items() if candidate.strip().lower() not in words.words() }
		extrapolated_candidates = { candidate.strip(): score for candidate, score in extrapolated_candidates.items() if len(year_pattern.findall(candidate)) == 0 } # exclude candidates that have a year in the title
		extrapolated_candidates = sorted(extrapolated_candidates.items(), key=lambda x:x[1])[:-1 * (extrapolator_participants + 1):-1]
		# for i, (candidate, score) in enumerate(extrapolated_candidates):
		# 	print("%d: %s (%f)" % (i + 1, candidate, score))
		return [ candidate for candidate, _ in extrapolated_candidates ]

	def get_candidate_pages(self, candidates, extrapolator_scheme):
		"""
		Get the representation of the candidate pages.
		This representation is based on the first sentence of the page.

		:param candidates: The list of candidates whose representation will be returned.
			It is assumed that the candidate refers to a unique Wikipedia page.
		:type candidates: list
		:param extrapolator_scheme: The term weighting scheme used to create the local and external contexts.
		:type extrapolator_scheme: :class:`vector.nlp.term_weighting.TermWeighting`

		:return: A dictionary matching the candidates with the :class:`vector.nlp.document.Document` representation.
		:rtype: dict
		"""

		candidate_pages = { }

		text_collector = TextCollector()
		tokenizer = Tokenizer()

		delimiter_pattern = re.compile("^(.+?)\.[\s\n][A-Z0-9]")
		bracket_pattern = re.compile("\(.*?\)")

		text_content = text_collector.get_plain_text(candidates, introduction_only=True)
		for candidate, text in text_content.items():
			text = bracket_pattern.sub(' ', text)
			matches = delimiter_pattern.findall(text)
			text = text if len(matches) == 0 else matches[0]
			tokens = tokenizer.tokenize(text)
			document = Document(text, tokens, scheme=extrapolator_scheme)
			document.normalize()
			candidate_pages[candidate] = document

		return candidate_pages

class WikipediaExtrapolator(Extrapolator):
	"""
	The Wikipedia extrapolator looks for pages that match the candidate's name.
	"""

	def extrapolate(self, candidates, corpus, extrapolator_scheme, extrapolator_participants=10, extrapolator_threshold=0, token_attribute="tokens", *args, **kwargs):
		"""
		Extrapolate the given candidates.

		:param candidates: The candidates to extrapolate.
			It is assumed that all of the given candidates were resolved using :class:`apd.resolvers.external.wikipedia_resolver.WikipediaResolver`.
			This means that all candidates share their name with a Wikipedia page.
		:type candidates: list
		:param corpus: The corpus of documents, which helps to isolate relevant candidates.
		:type corpus: list
		:param extrapolator_scheme: The term weighting scheme used to create the local and external contexts.
		:type extrapolator_scheme: :class:`vector.nlp.term_weighting.TermWeighting`
		:param extrapolator_participants: The number of extrapolated participants to retrieve.
		:type extrapolator_participants: int
		:param extrapolator_threshold: The minimum score of the extrapolated participant to be considered.
		:type extrapolator_threshold: float
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: The new candidates.
			These candidates are stored as a dictionary.
			The keys are the resolved candidates, and the values are their scores.
		:rtype: dict
		"""

		extrapolated_candidates = { }
		info_collector = InfoCollector()
		link_collector = LinkCollector()
		text_collector = TextCollector()
		tokenizer = Tokenizer(stopwords=stopwords.words("english"))
		year_pattern = re.compile("[0-9]{4}")

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
		Get the text from all the seed set.
		This content is used to build a corpus of external data.
		This serves as the external context.
		"""
		text_content = text_collector.get_plain_text(candidates, introduction_only=True)
		external_corpus = []
		for candidate, text in text_content.items():
			text = text[:text.index("\n")] if "\n" in text else text
			tokens = tokenizer.tokenize(text)
			document = Document(text, tokens, scheme=extrapolator_scheme)
			document.normalize()
			external_corpus.append(document)
		external_corpus_document = vector_math.concatenate(external_corpus)
		external_corpus_document.normalize()

		"""
		Get the links from the whole articles of the candidates.
		Pages with dates in them are excluded.
		"""
		links = link_collector.get_links(candidates, first_section_only=False, separate=False)
		links = [ link for link in links if len(year_pattern.findall(link)) == 0 ]
		links = [ link for link in links if all([ candidate not in link for candidate in candidates ]) ]

		"""
		Collect the text and compare it with the local and external contexts.
		"""
		text_content = text_collector.get_plain_text(links, introduction_only=True)
		for page, text in text_content.items():
			text = text[:text.index(".")] if "." in text else text
			tokens = tokenizer.tokenize(text)
			document = Document(text, tokens, scheme=extrapolator_scheme)
			document.normalize()
			local_similarity = vector_math.cosine(corpus_document, document)
			external_similarity = vector_math.cosine(external_corpus_document, document)
			extrapolated_candidates[page] = external_similarity * local_similarity

		"""
		Retain the candidates having a minimum score.
		From these candidates, return only the top ones.
		"""
		extrapolated_candidates = { candidate: score for candidate, score in extrapolated_candidates.items() if score >= extrapolator_threshold }
		extrapolated_candidates = sorted(extrapolated_candidates.items(), key=lambda x:x[1])[:-1 * (extrapolator_participants + 1):-1]
		# for i, (candidate, score) in enumerate(extrapolated_candidates):
		# 	print("%d: %s (%f)" % (i + 1, candidate, score))
		return [ candidate for candidate, _ in extrapolated_candidates ]
