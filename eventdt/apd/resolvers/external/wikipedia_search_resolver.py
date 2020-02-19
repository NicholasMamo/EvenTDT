"""
The Wikipedia search resolver is similar to the :class:`apd.resolvers.external.wikipedia_name_resolver.WikipediaNameResolver`.
In contrast with the name resolver, the search resolver searches for candidates on Wikipedia.
The resolver tries to map candidates to one of the results.

The aim of this resolver is to overcome common problems with the name resolver.
In many cases, colloquial names of candidates are not the same as their formal names.
For example, `FC Barcelona` is referred to simply as `Barcelona`.
"""

import os
import re
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nltk.corpus import stopwords

from vsm import vector_math
from nlp.document import Document
from nlp.tokenizer import Tokenizer
from wikinterface import info, links, search, text

from ..resolver import Resolver

class WikipediaSearchResolver(Resolver):
	"""
	The Wikipedia search resolver looks for pages that include candidate names.
	The Wikipedia API automatically ranks articles by relevance.
	This resolver exploits that to try and match the candidate with any of the top results.
	"""

	def __init__(self, scheme, tokenizer, threshold, corpus):
		"""
		Create the resolver.

		:param scheme: The term-weighting scheme to use to create documents from Wikipedia pages.
					   These documents are used to compare the similarity with the domain of the candidates.
		:type scheme: :class:`nlp.term_weighting.scheme.TermWeightingScheme`
		:param threshold: The threshold below which candidates become unresolved.
		:type threshold: float.
		:param tokenizer: The tokenizer to use to create documents.
		:type tokenizer: :class:`nlp.tokenizer.Tokenizer`
		:param threshold: The similarity threshold beyond which candidate participants are resolved.
		:type threshold: float
		:param corpus: The corpus of documents.
		:type corpus: list of :class:`nlp.document.Document`
		"""

		self.scheme = scheme
		self.tokenizer = tokenizer
		self.threshold = threshold
		self.corpus = corpus

	def resolve(self, candidates, *args, **kwargs):
		"""
		Resolve the given candidates.

		:param candidates: The candidates to resolve.
		:type candidates: list

		:return: A tuple containing the resolved and unresolved candidates respectively.
		:rtype: tuple of lists
		"""

		resolved_candidates, unresolved_candidates = [], []

		delimiter_pattern = re.compile("^(.+?)\.[\s\n][A-Z0-9]")

		candidates = [ candidate.title() for candidate in candidates ]

		"""
		Get the concatenated corpus.
		"""
		tokenized_corpus = []
		for document in corpus:
			tokens = tokenizer.tokenize(document.get_text())
			document = Document(document.get_text(), tokens, scheme=self.scheme)
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
				candidate_document = Document(candidate, tokenizer.tokenize(candidate), scheme=self.scheme)
				page_scores = { }
				for page, text in text_content.items():
					text = text.lower()
					text = bracket_pattern.sub(' ', text)
					matches = delimiter_pattern.findall(text)
					text = text if len(matches) == 0 else matches[0]
					text = text.replace(candidate.lower(), ' ')
					tokens = tokenizer.tokenize(text)
					title_document = Document(page, tokenizer.tokenize(page), scheme=self.scheme)
					document = Document(text, tokens, scheme=self.scheme)
					document.normalize()
					page_scores[page] = vector_math.cosine(document, corpus_document)
					page_scores[page] = page_scores[page] * vector_math.cosine(title_document, candidate_document)

				"""
				Save only the most similar page if it exceeds the threshold.
				"""
				chosen_candidate, score = sorted(page_scores.items(), key=lambda x:x[1])[:-2:-1][0]
				if score >= threshold:
					resolved_candidates.append(chosen_candidate)
				else:
					unresolved_candidates.append(candidate)
			else:
				unresolved_candidates.append(candidate)

		return (resolved_candidates, unresolved_candidates)

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
