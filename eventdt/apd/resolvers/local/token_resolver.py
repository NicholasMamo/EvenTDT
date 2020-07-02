"""
The token resolver can be thought of as a lemmatizer.
It takes candidate participants and tries to map them to the terms that generated them in the event corpus.
This resolver is mainly aimed at resolving candidate participants generated by the :class:`~apd.extractors.local.token_extractor.TokenExtractor`.
For example, if the extracted candidate participants are stemmed tokens, this resolver maps them to the word that is most likely to have generated them.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ..resolver import Resolver

from nlp.document import Document
from nlp.tokenizer import Tokenizer

class TokenResolver(Resolver):
	"""
	The token resolver tries to map tokens to actual terms.
	To resolve tokens, it requires the same tokenizer that generated the candidate participants.
	This algorithm uses the tokenizer to construct a reverse index: what terms could have generated a token?
	It also requires the original corpus to use to look for the lemmas.
	These parameters are accepted as instance variables in the constructor.

	:ivar ~.tokenizer: The tokenizer used to extract the tokens anew.
	:vartype ~.tokenizer: None or :class:`~nlp.tokenizer.Tokenizer`
	:ivar corpus: The corpus of documents.
				  This corpus is used to look for the terms that map to the tokens given as candidates.
	:vartype corpus: list of :class:`~nlp.document.Document`
	:ivar case_fold: A boolean indicating whether terms should be case-folded.
	:vartype case_fold: bool
	"""

	def __init__(self, tokenizer, corpus, case_fold=True):
		"""
		Create the resolver.

		:param tokenizer: The tokenizer used to extract the tokens anew.
		:type tokenizer: None or :class:`~nlp.tokenizer.Tokenizer`
		:param corpus: The corpus of documents.
					   This corpus is used to look for the terms that map to the tokens given as candidates.
		:type corpus: list of :class:`~nlp.document.Document`
		:param case_fold: A boolean indicating whether terms should be case-folded.
		:type case_fold: bool
		"""

		self.tokenizer = tokenizer
		self.corpus = corpus
		self.case_fold = case_fold

	def resolve(self, candidates, *args, **kwargs):
		"""
		Resolve the given candidates by looking for the original words.
		They are sorted according to their score.

		:param candidates: The candidates to resolve.
						   The candidates should be in the form of a dictionary.
						   The keys should be the candidates, and the values the scores.
		:type candidates: dict

		:return: A tuple containing the resolved and unresolved candidates respectively.
		:rtype: tuple of lists
		"""

		unresolved_candidates, resolved_candidates = [], []

		"""
		Generate the inverted index.
		Then keep only the most common term that generates each token.
		"""
		inverted_index = self._construct_inverted_index()
		inverted_index = self._minimize_inverted_index(inverted_index)

		"""
		Try to resolve each candidate.
		If a candidate has no token, it is not resolved.
		"""
		candidates = sorted(candidates.keys(), key=lambda candidate: candidates.get(candidate), reverse=True)
		for candidate in candidates:
			if candidate in inverted_index:
				resolved_candidates.append(inverted_index.get(candidate))
			else:
				unresolved_candidates.append(candidate)

		return (resolved_candidates, unresolved_candidates)

	def _construct_inverted_index(self):
		"""
		Construct an inverted index from the given corpus using the tokenizer.
		The inverted index is a nested dictionary.
		The topmost level is a list of tokens.
		Each token is associated with another dictionary.
		This inner dictionary is a list of terms that generate that token.
		The values of this inner dictionary is the number of times that the term is tokenized into the token.

		:return: An inverted index as a dictionary.
				 The tokens are the keys, and the values are dictionaries.
				 The keys of these inner dictionaries are the terms that generate the tokens.
				 The values are the frequencies of the terms.
		:rtype: dict
		"""

		inverted_index = {}

		"""
		Go through each document and split it into the individual terms.
		Then, tokenize that term and use it to build the inverted index.
		"""
		for document in self.corpus:
			terms = document.text.split()
			for term in terms:
				term = term.lower() if self.case_fold else term
				tokens = self.tokenizer.tokenize(term)

				"""
				Each term can result in multiple tokens.
				Hashtags, for example, may be split by the tokenizer.
				So can terms with dashes in them.
				"""

				for token in tokens:
					inverted_index[token] = inverted_index.get(token, {})
					inverted_index[token][term] = inverted_index[token].get(term, 0) + 1

		return inverted_index

	def _minimize_inverted_index(self, inverted_index):
		"""
		Minimize the inverted index.
		This operation retains only the most common term for each token.

		:param inverted_index: The inverted index, with tokens as keys.
							   Each token is associated with another dictionary.
							   This dictionary has terms that generate the token.
							   The values are the number of times that they generate the token.
		:type inverted_index: dict

		:return: The minimized inverted index as a dictionary.
				 The tokens remain as the keys.
				 The values are the terms that most-commonly generate the token.
		:rtype: dict
		"""

		"""
		The inverted index first retains a tuple of the most common term.
		Then, the term itself is retained.
		"""
		inverted_index = {
			token: max(inverted_index[token].items(), key=lambda x: x[1]) for token in inverted_index
		}

		inverted_index = { token: term[0] for token, term in inverted_index.items() }

		return inverted_index
