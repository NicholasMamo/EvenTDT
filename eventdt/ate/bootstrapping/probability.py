"""
Methods that evaluate unithood or termhood based on probability.
"""

import json
import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

import ate
from ate import linguistic

def CHI(corpora, x, y, cache=None):
	"""
	Calculate the chi-square statistic on the given corpora for the two given tokens.
	The statistic is based on how many documents tokens co-occur in.
	The order of the two tokens does not matter since the chi-square statistic is symmetric.

	All the tokens in `x` are matched with all tokens in `y` in a cross-product fashion.
	The chi-square statistic is computed for each such pair (one token in `x`, one token in `y`).

	The chi-square statistic is 0 if the two variables are independent.
	The higher the statistic, the more dependent the two variables are.

	:param corpora: A corpus, or corpora, of documents.
					If a string is given, it is assumed to be one corpus.
					If a list is given, it is assumed to be a list of corpora.

					.. note::

						It is assumed that the corpora were extracted using the tokenizer tool.
						Therefore each line should be a JSON string representing a document.
						Each document should have a `tokens` attribute.
	:type corpora: str or list of str
	:param x: The first token or list of tokens in the comparison.
			  Alternatively, a list of tokens can be provided.
			  This is more efficient because it can allow caching.
	:type x: str or list of str
	:param y: The second token or list of tokens in the comparison.
			  Alternatively, a list of tokens can be provided.
			  This is more efficient because it can allow caching.
	:type y: str or list of str
	:param cache: A list of terms that are re-used often and which should be cached.
				  If an empty list is given, no cache is used.

				  .. note::

					  Cache should be used when there is a lot of repetition.
					  For example, `x` can be used as cache when `x` is small and `y` is large.
					  If the data is small, using cache can be detrimental.
	:type cache: list of str

	:return: The chi-square statistic for all pairs of x and y as a dictionary.
			 The keys are the pairs, and the values the chi-square statistic.
	:rtype: dict
	"""

	chi = { }

	"""
	Convert the corpora and tokens into a list if they aren't already.
	The list of tokens is always made into a list, even if it's a list of one string.
	"""
	corpora = [ corpora ] if type(corpora) is str else corpora
	x = [ x ] if type(x) is str else x
	y = [ y ] if type(y) is str else y

	"""
	Create the contingency tables and calculate the chi statistic for each pair.
	"""
	tables = _contingency_table(corpora, x, y, cache=cache)
	chi = { pair: _chi(table) for pair, table in tables.items() }

	return chi

def _contingency_table(corpora, x, y, cache=None):
	"""
	Create the contingency tables for all the pairs of tokens in `x` and `y`.
	All the tokens in `x` are matched with all tokens in `y` in a cross-product fashion.

	:param corpora: The list of corpora to use to create the contingency table.
					.. note::

						It is assumed that the corpora were extracted using the tokenizer tool.
						Therefore each line should be a JSON string representing a document.
						Each document should have a `tokens` attribute.
	:type corpora: list of str
	:param x: The first list of tokens to use to create the contingency tables.
	:type x: list of str
	:param y: The second list of tokens to use to create the contingency tables.
	:type y: list of str
	:param cache: A list of terms that are re-used often and which should be cached.
				  If an empty list is given, no cache is used.

				  .. note::

					  Cache should be used when there is a lot of repetition.
					  For example, `x` can be used as cache when `x` is small and `y` is large.
					  If the data is small, using cache can be detrimental.
	:type cache: list of str

	:return: A dictionary of contingency tables.
			 The keys are the pairs of the tokens.
			 The values are four-tuples representing the values of cells in the order:

			 	1. Top-left,
				2. Top-right,
				3. Bottom-left, and
				4. Bottom-right.
	:rtype: dict
	"""

	tables = { }

	"""
	Convert the corpora and tokens into a list if they aren't already.
	"""
	corpora = [ corpora ] if type(corpora) is str else corpora
	x = [ x ] if type(x) is str else x
	y = [ y ] if type(y) is str else y
	cache = cache or [ ]
	cache = [ cache ] if type(cache) is str else cache

	"""
	Get the total number of documents in the corpora.
	Initially, the token counts will be calculated only for tokens that are not cached.
	The token counts for tokens that are cached can be calculated in the cache routine.
	"""
	total = ate.total_documents(corpora)
	counts = ate.total_documents(corpora, focus=list(set(x + y)))

	"""
	Generate the pairs for which the chi-square statistic will be computed.
	Then, initialize the contingency table for each pair.
	"""
	pairs = joint_vocabulary(x, y)
	tables = { pair: (0, 0, 0, 0) for pair in pairs }

	"""
	If cache is defined, generate a list of documents for each cached token.
	This reduces the number of documents to go over.
	"""
	if cache:
		for token in cache:
			"""
			Look for pairs that mention the cached token.
			"""
			cached_pairs = [ pair for pair in pairs if token in pair ]

			"""
			Create the cache.
			Update the A in the tables for the cached token.
			This value represents the number of documents in which both the cached token and the other token appear.
			"""
			documents = _cache(corpora, token)
			for document in documents:
				for a, b in cached_pairs:
					if a in document['tokens'] and b in document['tokens']:
						A, B, C, D = tables[(a, b)]
						A += 1
						tables[(a, b)] = (A, B, C, D)

			"""
			Complete the contingency tables.
			"""
			for (a, b) in cached_pairs:
				 A, B, C, D = tables[(a, b)]
				 B = counts[a] - A # documents in which the first token appears without the second token
				 C = counts[b] - A # documents in which the second token appears without the first token
				 D = total - (A + B + C) # documents in which neither the first nor the second token appears
				 tables[(a, b)] = (A, B, C, D)

			"""
			Remove the already-created contingency tables from the pairs.
			"""
			pairs = [ pair for pair in pairs if token not in pair ]

	"""
	Create any remaining contingency tables.
	"""
	if pairs:
		for corpus in corpora:
			with open(corpus, 'r') as f:
				for line in f:
					document = json.loads(line)
					for a, b in pairs:
						if a in document['tokens'] and b in document['tokens']:
							A, B, C, D = tables[(a, b)]
							A += 1
							tables[(a, b)] = (A, B, C, D)

		"""
		Complete the contingency tables.
		"""
		for (a, b) in pairs:
			 A, B, C, D = tables[(a, b)]
			 B = counts[a] - A # documents in which the first token appears without the second token
			 C = counts[b] - A # documents in which the second token appears without the first token
			 D = total - (A + B + C) # documents in which neither the first nor the second token appears
			 tables[(a, b)] = (A, B, C, D)

	return tables

def _chi(table):
	"""
	Calculate the chi-square statistic from the given table.
	The chi-square statistic is 0 if the two variables are independent.
	The higher the statistic, the more dependent the two variables are.

	:param table: The contingency table as a four-tuple.
				  The values are four-tuples representing the values of cells in the order:

	 			 	1. Top-left,
	 				2. Top-right,
	 				3. Bottom-left, and
	 				4. Bottom-right.
	:type table: tuple of int

	:return: The chi-square statistic.
	:rtype: float
	"""

	N = sum(table)
	A, B, C, D = table

	"""
	If any value in the denominator is 0, return 0.
	This is an unspecified case that results in division by 0.
	"""
	if not all([ A + C, B + D, A + B, C + D ]):
		return 0

	return ((N * (A * D - C * B) ** 2) /
		    ( (A + C) * (B + D) * (A + B) * (C + D) ))
