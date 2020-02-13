"""
The Wikipedia Resolver
A resolver that looks for keywords in Wikipedia pages.
These pages are considered to be concepts.
"""

import os
import re
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '../../../')
if path not in sys.path:
	sys.path.append(path)

from nltk.corpus import stopwords

from logger import logger

from vector import vector_math

from vector.nlp.document import Document
from vector.nlp.tokenizer import Tokenizer

from wikinterface.info_collector import InfoCollector, PageType
from wikinterface.linkcollector import LinkCollector
from wikinterface.searchcollector import SearchCollector
from wikinterface.textcollector import TextCollector

from ..resolver import Resolver

class WikipediaResolver(Resolver):
	"""
	The Wikipedia resolver looks for pages that match the candidate's name.
	"""

	def resolve(self, candidates, corpus, resolver_scheme, resolver_threshold=0, token_attribute="tokens", *args, **kwargs):
		"""
		Resolve the given candidates.

		:param candidates: The candidates to resolve.
		:type candidates: list
		:param corpus: The corpus of documents, which helps to resolve the candidates.
		:type corpus: list
		:param resolver_scheme: The term weighting scheme used to create documents that represent ambiguous pages.
		:type resolver_scheme: :class:`vector.nlp.term_weighting.TermWeighting`
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: A tuple containing the resolved candidates, and unresolved ones.
		:rtype: tuple
		"""

		resolved_candidates, unresolved_candidates = [], []
		info_collector = InfoCollector()
		link_collector = LinkCollector()
		search_collector = SearchCollector()
		text_collector = TextCollector()
		tokenizer = Tokenizer(stopwords=stopwords.words("english"))

		candidates = [ candidate.title() for candidate in candidates ]
		text = info_collector.get_type(candidates)
		ambiguous_candidates = []
		for candidate, content in text.items():
			"""
			Some pages resolve directly, though may need to redirect.
			Those pages are retained unchanged to respect domain discourse.
			"""
			if content["type"] is PageType.NORMAL:
				resolved_candidates.append(candidate)
			elif content["type"] is PageType.DISAMBIGUATION:
				ambiguous_candidates.append(candidate)
			else:
				unresolved_candidates.append(candidate)

		"""
		Get the concatenated corpus.
		"""
		tokenized_corpus = []
		for document in corpus:
			tokens = tokenizer.tokenize(document.get_text())
			document = Document(document.get_text(), tokens, scheme=resolver_scheme)
			tokenized_corpus.append(document)
		corpus_document = vector_math.concatenate(tokenized_corpus)
		corpus_document.normalize()

		"""
		Get the links, or potential disambiguations of candidates.
		"""
		ambiguous_candidates = link_collector.get_links(ambiguous_candidates, first_section_only=False)
		for ambiguous_candidate, links in ambiguous_candidates.items():
			"""
			The ambiguous titles are sorted by performing text extraction.
			From this search, only the most similar are retained.
			"""

			if len(links) > 0:
				text_content = text_collector.get_plain_text(links, introduction_only=True)

				"""
				Get the score of each page
				"""
				page_scores = { }
				for page, text in text_content.items():
					tokens = tokenizer.tokenize(text)
					document = Document(text, tokens, scheme=resolver_scheme)
					document.normalize()
					page_scores[page] = vector_math.cosine(document, corpus_document)

				"""
				Save only the most similar page if it exceeds the threshold.
				"""
				chosen_candidate, score = sorted(page_scores.items(), key=lambda x:x[1])[:-2:-1][0]
				if score >= resolver_threshold:
					resolved_candidates.append(chosen_candidate)
				else:
					unresolved_candidates.append(ambiguous_candidate)
			else:
				unresolved_candidates.append(ambiguous_candidate)

		return (resolved_candidates, unresolved_candidates)
