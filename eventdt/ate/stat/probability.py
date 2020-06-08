"""
Methods that evaluate unithood or termhood based on probability.
"""

import json
import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

import linguistic

def p(corpora, focus=None, cache=None):
	"""
	Calculate the probability of tokens appearing in the corpus.
	The probability is computed in terms of all tokens.

	Apart from calculating the probability of single tokens, the joint probability can be calculated by providing tuples.

	.. note::

		The joint probability is the minimum count of any token in each document.

	:param corpora: A corpus, or corpora, of documents.
					If a string is given, it is assumed to be one corpus.
					If a list is given, it is assumed to be a list of corpora.

					.. note::

						It is assumed that the corpora were extracted using the tokenizer tool.
						Therefore each line should be a JSON string representing a document.
						Each document should have a `tokens` attribute.
	:type corpora: str or list of str
	:param focus: The tokens for which to compute the probability.
				 If nothing is given, the probability is calculated for all tokens.
				 The tokens can be provided as:

				 - A single word,
				 - A list of tokens,
				 - A tuple, or
				 - A list of tuples.

				 A tuple can be used to compute joint probabilities.
	:type focus: None or str or list of str or tuple or list of tuple
	:param cache: A list of terms that are re-used often and which should be cached.
				  If an empty list is given, no cache is used.

				  .. note::

					  Cache should be used when there is a lot of repetition.
					  For example, `x` can be used as cache when `x` is small and `y` is large.
					  If the data is small, using cache can be detrimental.
	:type cache: list of str

	:return: A dictionary with tokens as keys and probabilities as values.
	:rtype: dict
	"""

	"""
	Convert the corpora and tokens into a list if they aren't already.
	The list of tokens is always made into a list, even if it's a list of one string or tuple.
	"""
	corpora = [ corpora ] if type(corpora) is str else corpora
	focus = focus or [ ]
	focus = [ focus ] if type(focus) is tuple or type(focus) is str else focus
	focus = [ (itemset, ) if type(itemset) is str else itemset for itemset in focus ]

	"""
	Create the initial counts for all tokens and joint probabilities.
	This avoids returning missing probabilities for tokens or joint tokens that never appear.
	"""
	counts = { }
	for itemset in focus:
		counts[itemset if len(itemset) > 1 else itemset[0]] = 0

	"""
	If cache is defined, generate a list of documents for each cached token.
	This reduces the number of documents to go over.
	"""
	if cache:
		for token in cache:
			"""
			If no itemset contains the token, skip the cache.
			"""
			if not any( token in itemset for itemset in focus ):
				continue

			"""
			Create the cache.
			"""
			documents = _cache(corpora, token)

			"""
			Look for item sets that mention the token.
			"""
			itemsets = [ tuple for tuple in focus if token in tuple ]
			for document in documents:
				for itemset in itemsets:
					if not all( item in document['tokens'] for item in itemset ):
						continue

					min_count = min( document['tokens'].count(item) for item in itemset )
					counts[itemset if len(itemset) > 1 else itemset[0]] += min_count

			focus = [ tuple for tuple in focus if token not in tuple ]

	"""
	Count the total number of tokens encountered and a separate count for each token.
	"""
	tokens = 0
	for corpus in corpora:
		with open(corpus, 'r') as f:
			for line in f:
				document = json.loads(line)

				"""
				The number of tokens is always incremented by all the tokens.
				"""
				tokens += len(document['tokens'])

				"""
				If there is no specification for which tokens to compute probability, compute the prior probability for all tokens.
				"""
				if not focus:
					for token in document['tokens']:
						counts[token] = counts.get(token, 0) + 1
				else:
					"""
					Convert each item in the list of tokens for which to compute the probability into a tuple.
					"""
					for itemset in focus:
						if not all( item in document['tokens'] for item in itemset ):
							continue

						min_count = min( document['tokens'].count(item) for item in itemset )
						counts[itemset if len(itemset) > 1 else itemset[0]] += min_count

	"""
	Compute the probability by dividing the count by the number of tokens.
	"""
	if tokens:
		return { token: count / tokens for token, count in counts.items() }

	return { }

def PMI(corpora, x, y, base=2, cache=None):
	"""
	Calculate the Pointwise Mutual-Information (PMI) between two variables.
	PMI is symmetric and computed as:

	.. math::

		PMI(x,y) = \\log( \\frac{p(x,y)}{p(x)p(y)} )

	The function accepts multiple values for both variables, and returns the PMI separately.
	The return value is a dictionary, where the keys are the cross product between `x` and `y`.

	:param corpora: A corpus, or corpora, of documents.
					If a string is given, it is assumed to be one corpus.
					If a list is given, it is assumed to be a list of corpora.

					.. note::

						It is assumed that the corpora were extracted using the tokenizer tool.
						Therefore each line should be a JSON string representing a document.
						Each document should have a `tokens` attribute.
	:type corpora: str or list of str
	:param x: The tokens for which to compute the probability.
			  These tokens are combined as a cross-product with all tokens in `y`.
			  The tokens can be provided as:

			  - A single word,
			  - A list of tokens,
			  - A tuple, or
			  - A list of tuples.

			  A tuple translates to joint probabilities.
			  If nothing is given, it is replaced with the corpora's vocabulary.
	:type x: str or list of str or tuple or list of tuple
	:param y: The tokens for which to compute the probability.
			  These tokens are combined as a cross-product with all tokens in `x`.
			  The tokens can be provided as:

			  - A single word,
			  - A list of tokens,
			  - A tuple, or
			  - A list of tuples.

			  A tuple translates to joint probabilities.
			  If nothing is given, it is replaced with the corpora's vocabulary.
	:type y: str or list of str or tuple or list of tuple
	:param base: The base of the logarithm, defaults to 2.
	:type base: float
	:param cache: A list of terms that are re-used often and which should be cached.
				  If an empty list is given, no cache is used.

				  .. note::

					  Cache should be used when there is a lot of repetition.
					  For example, `x` can be used as cache when `x` is small and `y` is large.
					  If the data is small, using cache can be detrimental.
	:type cache: list of str

	:return: A dictionary with pairs of `x` and `y` variables as keys, and their PMi as values.
	:rtype: dict
	"""

	pmi = { }

	"""
	The list of tokens in `x` and `y` is always made into a list, even if it's a list of one string or tuple.
	"""
	x, y = x or [ ], y or [ ]
	x = [ x ] if type(x) is tuple or type(x) is str else x
	y = [ y ] if type(y) is tuple or type(y) is str else y

	if not x:
		x = linguistic.vocabulary(corpora)

	if not y:
		y = linguistic.vocabulary(corpora)

	"""
	Get the 'vocabulary' for which to compute probabilities.
	This vocabulary is made up of all the elements in `x` and `y`, as well as the cross-product between them.
	"""
	prior = list(set(x + y))
	prob = p(corpora, focus=prior+joint_vocabulary(x, y), cache=cache)

	"""
	Calculate the PMI from the probabilities.
	"""
	for i in x:
		for j in y:
			pmi[(i, j)] = _pmi(prob, i, j, base)

	return pmi

def _pmi(prob, x, y, base):
	"""
	Calculate the Pointwise Mutual Information (PMI) of `x` and `y` based on the given probabilities.

	:param prob: A probability calculation, possibly calculated using the :func:`ate.stat.probability.p` function.
				 This is used as cache for the probabilities.
				 The keys are the tokens, including the joint probability of `x` and `y`, and the values are their probabilities.
	:type prob: dict
	:param x: The first token or tuple of tokens to use to calculate the PMI.
	:type x: str or tuple of str
	:param y: The second token or tuple of tokens to use to calculate the PMI.
	:type y: str or tuple of str
	:param base: The base of the logarithm, defaults to 2.
	:type base: float

	:return: The PMI of `x` and `y`.
	:rtype: float
	"""

	joint = joint_vocabulary(x, y)[0]
	if not prob[x] or not prob[y] or not prob[joint]:
		return 0

	return math.log(prob[joint]/( prob[x] * prob[y] ), base)

def _cache(corpora, token):
	"""
	Compile all the documents in the given corpora that mention the token.
	These documents can be used as cache.
	In this way, the files do not have to be re-opened and documents without the token do not have to be iterated over.

	:param corpora: A corpus, or corpora, of documents.
					If a string is given, it is assumed to be one corpus.
					If a list is given, it is assumed to be a list of corpora.

					.. note::

						It is assumed that the corpora were extracted using the tokenizer tool.
						Therefore each line should be a JSON string representing a document.
						Each document should have a `tokens` attribute.
	:type corpora: str or list of str
	:param token: The token to look for in the documents.
	:type token: str

	:return: A list of documents, each represented as a dictionary, that contain the given token.
	:rtype: list of dict
	"""

	"""
	Convert the corpora into a list if they aren't already.
	"""
	corpora = [ corpora ] if type(corpora) is str else corpora

	documents = [ ]
	for corpus in corpora:
		with open(corpus, 'r') as f:
			for line in f:
				document = json.loads(line)
				if token in document['tokens']:
					documents.append(document)

	return documents

def joint_vocabulary(x, y):
	"""
	Get the joint vocabulary by creating the cross-product from `x` and `y`.

	:param x: The tokens for which to compute the probability.
			  These tokens are combined as a cross-product with all tokens in `y`.
			  The tokens can be provided as:

			  - A single word,
			  - A list of tokens,
			  - A tuple, or
			  - A list of tuples.

			  A tuple translates to joint probabilities.
	:type x: str or list of str or tuple or list of tuple
	:param y: The tokens for which to compute the probability.
			  These tokens are combined as a cross-product with all tokens in `x`.
			  The tokens can be provided as:

			  - A single word,
			  - A list of tokens,
			  - A tuple, or
			  - A list of tuples.

			  A tuple translates to joint probabilities.
	:type y: str or list of str or tuple or list of tuple

	:return: The joint vocabulary, which is the cross-product of each item in `x` with each item in `y`.
	:rtype: list of tuple
	"""

	vocabulary = [ ]

	"""
	The list of tokens in `x` and `y` is always made into a list, even if it's a list of one string or tuple.
	"""
	x, y = x or [ ], y or [ ]
	x = [ x ] if type(x) is tuple or type(x) is str else x
	y = [ y ] if type(y) is tuple or type(y) is str else y

	"""
	Immediately return if either `x` or `y` are empty.
	"""
	if not x:
		return [ tuple(item) if type(item) is not str else (item, ) for item in y ]

	if not y:
		return [ tuple(item) if type(item) is not str else (item, ) for item in x ]

	"""
	Create the vocabulary.
	"""
	for i in x:
		"""
		Always convert the elements into a list, whether they are a string or a tuple.
		"""
		i = list([ i ] if type(i) is str else i)
		for j in y:
			j = list([ j ] if type(j) is str else j)
			vocabulary.append(tuple(i + j))

	return vocabulary
