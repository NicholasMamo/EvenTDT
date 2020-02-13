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

class SearchResolver(Resolver):
	"""
	The search resolver looks for pages that are most similar to the corpus.
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
		search_collector = SearchCollector()
		text_collector = TextCollector()
		tokenizer = Tokenizer(stopwords=stopwords.words("english"))

		year_pattern = re.compile("[0-9]{4}")
		bracket_pattern = re.compile("\(.*?\)")
		delimiter_pattern = re.compile("^(.+?)\.[\s\n][A-Z0-9]")

		candidates = [ candidate.title() for candidate in candidates ]

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

		for candidate in candidates:
			"""
			Get the possible pages for each candidate, removing those that have years in them.
			Most often, pages with years in them are not entities.
			Unfortunately, exceptions exist, such as with the name `TSG 1899 Hoffenheim`.

			For each page, fetch its text content and type.
			The type is used to remove pages that are not normal.
			"""
			pages = search_collector.search(candidate, limit=5)
			pages = [ page for page in pages if len(year_pattern.findall(page)) == 0 ]
			pages = [ page for page in pages if not page.lower().startswith("list of") ]
			if len(pages) > 0:
				page_info = info_collector.get_type(pages)
				pages = [ page for page, content in page_info.items() if content["type"] is PageType.NORMAL ]

			if len(pages) > 0:
				text_content = text_collector.get_plain_text(pages, introduction_only=True)

				"""
				Get the score of each page.
				"""
				candidate_document = Document(candidate, tokenizer.tokenize(candidate), scheme=resolver_scheme)
				page_scores = { }
				for page, text in text_content.items():
					text = text.lower()
					text = bracket_pattern.sub(' ', text)
					matches = delimiter_pattern.findall(text)
					text = text if len(matches) == 0 else matches[0]
					text = text.replace(candidate.lower(), ' ')
					tokens = tokenizer.tokenize(text)
					title_document = Document(page, tokenizer.tokenize(page), scheme=resolver_scheme)
					document = Document(text, tokens, scheme=resolver_scheme)
					document.normalize()
					page_scores[page] = vector_math.cosine(document, corpus_document)
					page_scores[page] = page_scores[page] * vector_math.cosine(title_document, candidate_document)

				"""
				Save only the most similar page if it exceeds the threshold.
				"""
				chosen_candidate, score = sorted(page_scores.items(), key=lambda x:x[1])[:-2:-1][0]
				if score >= resolver_threshold:
					resolved_candidates.append(chosen_candidate)
					# logger.info("Resolved %s to %s (%f)" % (candidate, chosen_candidate, score))
				else:
					# logger.info("Could not resolve %s to %s (%f)" % (candidate, chosen_candidate, score))
					unresolved_candidates.append(candidate)
			else:
				unresolved_candidates.append(candidate)

		return (resolved_candidates, unresolved_candidates)
