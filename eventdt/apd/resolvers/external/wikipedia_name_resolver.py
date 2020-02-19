"""
The Wikipedia name resolver looks to map candidates to pages that include their name.
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

from wikinterface import info, links, text

from ..resolver import Resolver

class WikipediaNameResolver(Resolver):
	"""
	The Wikipedia name resolver looks for pages that match the candidate's name.
	It then maps the candidate to that page by returning the page name instead of the candidate.

	:ivar scheme: The term-weighting scheme to use to create documents from Wikipedia pages.
				   These documents are used to compare the similarity with the domain of the candidates.
	:vartype scheme: :class:`nlp.term_weighting.scheme.TermWeightingScheme`
	:ivar tokenizer: The tokenizer to use to create documents.
	:vartype tokenizer: :class:`nlp.tokenizer.Tokenizer`
	:ivar threshold: The threshold below which candidates become unresolved.
	:vartype threshold: float.
	:ivar corpus: The corpus of documents.
	:vartype corpus: list of :class:`nlp.document.Document`
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
						   The candidates should be in the form of a dictionary.
						   The keys should be the candidates, and the values the scores.
		:type candidates: dict

		:return: A tuple containing the resolved and unresolved candidates respectively.
		:rtype: tuple of lists
		"""

		resolved_candidates, unresolved_candidates = [], []

		candidates = [ candidate for candidate in candidates ]
		resolved, unresolved, ambiguous = self._resolve_unambiguous_candidates(candidates)
		resolved_candidates.extend(resolved)
		unresolved_candidates.extend(unresolved)

		"""
		Get the concatenated corpus as a single document, representing the domain.
		"""
		domain = Document.concatenate(*self.corpus, tokenizer=self.tokenizer, scheme=self.scheme)
		domain.normalize()

		"""
		Get the potential disambiguations of the ambiguous candidates.
		Then, find the best page for each candidate.
		If its similarity with the domain is sufficiently high, the candidate is resolved.
		"""
		ambiguous = links.collect(ambiguous, introduction_only=False)
		for candidate, pages in ambiguous.items():
			"""
			If there are candidate pages, get the most similar page.
			If the most similar page exceeds the similarity threshold, resolve the candidate to that page.
			Otherwise, the candidate cannot be resolved.
			"""
			if len(pages) > 0:
				page, score = self._disambiguate(pages, domain)
				if score >= self.threshold:
					resolved_candidates.append(page)
					continue

			unresolved_candidates.append(candidate)

		return (resolved_candidates, unresolved_candidates)

	def _resolve_unambiguous_candidates(self, candidates):
		"""
		Resolve the candidates that are unambiguous.
		The function handles three possiblities:

			#. There are candidates that have a page, and therefore the candidate is resolved to them.
			#. Others have a disambiguation page and are thus ambiguous.
			   These candidates are resolved elsewhere.
			#. Other candidates return an empty result.
			   In this case, they are said to be unresolved.

		:param candidates: The candidates to resolve.
						   The candidates should be in the form of a dictionary.
						   The keys should be the candidates, and the values the scores.
		:type candidates: dict

		:return: A tuple containing the resolved, unresolved and ambiguous candidates respectively.
		:rtype: tuple of lists
		"""

		resolved_candidates, unresolved_candidates, ambiguous_candidates = [], [], []

		for candidate in candidates:
			text = info.types([ candidate ])
			for page, type in text.items():
				"""
				Some pages resolve directly, though may need to redirect.
				Those pages are retained unchanged to respect domain discourse.
				"""
				if type is info.ArticleType.NORMAL:
					resolved_candidates.append(candidate)
					break
				elif type is info.ArticleType.DISAMBIGUATION:
					ambiguous_candidates.append(candidate)
					break

			"""
			If the candidate could not be resolved or if it does not have a disambiguation, the candidate cannot be resolved.
			"""
			if (candidate not in resolved_candidates and
				candidate not in ambiguous_candidates):
				unresolved_candidates.append(candidate)

		return resolved_candidates, unresolved_candidates, ambiguous_candidates

	def _disambiguate(self, pages, domain):
		"""
		Disambiguate a candidate by finding the link that is most similar to the domain.
		The function returns the link's page name and the associated score.
		Only one page is returned: the one with the highest score.

		:param pages: A list
		:type pages: TODO: complete
		:param domain: A document that represents the domain.
		:type domain: :class:`nlp.document.Document`

		:return: A tuple containing the most similar page and its similarity score.
		:rtype: tuple
		"""

		"""
		Get the first section of each page.
		Then, convert them into documents.
		"""
		pages = text.collect(pages, introduction_only=True)
		for page, text in pages.items():
			pages[page] = Document(text, self.tokenizer.tokenize(text),
								   scheme=self.scheme)
			pages[page].normalize()

		"""
		Rank the page scores in descending order.
		Then, choose the best page and return it alongside its score.
		"""
		page_scores = { page: vector_math.cosine(text, domain) for page, text in pages.items() }
		best_page = max(page_scores, key=lambda page: page_scores.get(page))
		return (best_page, page_scores[best_page])
