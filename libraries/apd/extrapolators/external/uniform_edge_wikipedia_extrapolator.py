"""
An extrapolator that uses Wikipedia's links as the basis for semantic similarity.
"""

import asyncio
import os
import re
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '../../../')
if path not in sys.path:
	sys.path.append(path)

import networkx as nx
from networkx.algorithms import centrality, community

from nltk.corpus import stopwords
from nltk.corpus import words

from graph.graph import Graph, Node

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
		tokenizer = Tokenizer()

		year_pattern = re.compile("[0-9]{4}") # a pattern that indicates a year in the title
		bracket_pattern = re.compile("\(.*?\)")

		delimiter = '.'

		"""
		Get the concatenated corpus.
		This serves as the local context.
		"""
		tokenized_corpus = []
		for document in corpus:
			tokens = tokenizer.tokenize(document.get_text(), stopwords=stopwords.words("english"))
			document = Document(document.get_text(), tokens, scheme=extrapolator_scheme)
			tokenized_corpus.append(document)
		corpus_document = vector_math.concatenate(tokenized_corpus)
		corpus_document.normalize()

		"""
		Create an empty graph.
		"""
		graph = Graph()
		candidate_nodes = {}

		"""
		Get the first level links.
		Only retain those that appear a minimum of times.
		"""
		first_links = link_collector.get_links(candidates, first_section_only=False, separate=True)
		first_links = { page: links for page, links in first_links.items() if len(year_pattern.findall(page)) == 0 }
		link_popularity = { }
		for link_set in first_links.values():
			for link in link_set:
				link_popularity[link] = link_popularity.get(link, 0) + 1
		link_popularity = sorted(link_popularity.items(), key=lambda x:x[1])[::-1]

		next_pages = [ link for link, _ in link_popularity if link not in first_links.keys() ][:50]

		for candidate, links in first_links.items():
			""""
			Create the nodes and edges, this time using the first-level links.
			"""
			links = [ link for link in links if link in next_pages ]
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
					graph.add_edge(node, candidate_nodes[candidate])

		"""
		Repeat the process a second time.
		"""
		second_links = link_collector.get_links(next_pages, first_section_only=False, separate=True)
		second_links = { page: links for page, links in second_links.items() if len(year_pattern.findall(page)) == 0 }
		link_popularity = { }
		for link_set in second_links.values():
			for link in link_set:
				link_popularity[link] = link_popularity.get(link, 0) + 1
		second_links = { page: [ link for link in second_links[page] if link_popularity[link] > 2 ] for page in second_links }

		for source_page, links in second_links.items():
			""""
			Create the nodes and edges, this time using the second-level links.
			"""
			if source_page not in candidate_nodes:
				"""
				The source page may not always have a node - this could happen because of redirections.
				"""
				node = Node(source_page)
				candidate_nodes[source_page] = node
				graph.add_node(node)

			for page in links:
				if page not in candidate_nodes:
					"""
					If the page does not have a node, create one for it.
					"""
					node = Node(page)
					candidate_nodes[page] = node
					graph.add_node(node)
					graph.add_edge(node, candidate_nodes[source_page])

		"""
		Create a networkx graph and use it to partition the pages.
		"""
		nx_graph = graph.to_networkx()
		i, top_level_partitions = 0, []
		while len(top_level_partitions) <= 4 and i < 5:
			top_level_partitions = next(community.girvan_newman(nx_graph))
			i += 1

		"""
		Get the nodes from the biggest partitions.
		"""
		new_candidates = []
		for i, partition in enumerate(top_level_partitions):
			subgraph = nx_graph.subgraph(partition)
			if len(partition) > 4:
				nodes = [ nx_graph.node[node]["name"] for node in partition ]
				new_candidates.extend(nodes)

		"""
		Filter out nodes that are not similar to the corpus.
		"""
		text_content = text_collector.get_plain_text(new_candidates, introduction_only=True)
		for candidate, text in text_content.items():
			text = bracket_pattern.sub(' ', text)
			text = text[:text.index(delimiter)] if delimiter in text else text
			tokens = tokenizer.tokenize(text, stopwords=stopwords.words("english"))
			document = Document(text, tokens, scheme=extrapolator_scheme)
			document.normalize()
			similarity = vector_math.cosine(corpus_document, document)
			extrapolated_candidates[candidate] = similarity

		"""
		Retain the candidates having a minimum score.
		From these candidates, return only the top ones.
		"""
		extrapolated_candidates = { candidate: score for candidate, score in extrapolated_candidates.items() if score >= extrapolator_threshold }
		extrapolated_candidates = { candidate: score for candidate, score in extrapolated_candidates.items() if candidate.lower() not in words.words() }
		extrapolated_candidates = { candidate: score for candidate, score in extrapolated_candidates.items() if len(year_pattern.findall(candidate)) == 0 } # exclude candidates that have a year in the title
		extrapolated_candidates = sorted(extrapolated_candidates.items(), key=lambda x:x[1])[:-1 * (extrapolator_participants + 1):-1]
		# for i, (candidate, score) in enumerate(extrapolated_candidates):
		# 	print("%d: %s (%f)" % (i + 1, candidate, score))
		return [ candidate for candidate, _ in extrapolated_candidates ]


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
		tokenizer = Tokenizer()
		year_pattern = re.compile("[0-9]{4}")

		"""
		Get the concatenated corpus.
		This serves as the local context.
		"""
		tokenized_corpus = []
		for document in corpus:
			tokens = tokenizer.tokenize(document.get_text(), stopwords=stopwords.words("english"))
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
			tokens = tokenizer.tokenize(text, stopwords=stopwords.words("english"))
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
			tokens = tokenizer.tokenize(text, stopwords=stopwords.words("english"))
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
