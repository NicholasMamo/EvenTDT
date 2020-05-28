"""
Methods that evaluate unithood or termhood based on probability.
"""

import json

def p(corpora, only=None):
	"""
	Calculate the probability of tokens appearing in the corpus.
	The probability is computed in terms of all tokens.

	Apart from calculating the probability of single tokens, the joint probability can be calculated by providing tuples.

	.. note::

		The joint probability is the minimum count of any token in each document.

	:param corpora: A corpus, or corpora, of documents.
					If a string is given, it is assumed to be one corpus.
					If a list is given, it is assumed to be a list of corpora.

					It is assumed that the corpora were extracted using the tokenizer tool.
					Therefore each line should be a JSON string representing a document.
					Each document should have a `tokens` attribute.
	:type corpora: str or list of str
	:param only: The tokens for which to compute the probability.
				 If nothing is given, the probability is calculated for all tokens.
				 The tokens can be provided as:

				 - A single word,
				 - A list of tokens,
				 - A tuple,
				 - A list of tuples.

				 A tuple can be used to compute joint probabilities.
	:type only: None or str or list of str or tuple or list of tuple

	:return: A dictionary with tokens as keys and probabilities as values.
	:rtype: dict
	"""

	"""
	Convert the corpora and tokens into a list if they aren't already.
	The list of tokens is always made into a list, even if it's a list of one string or tuple.
	"""
	corpora = [ corpora ] if type(corpora) is str else corpora
	only = only or [ ]
	only = [ only ] if type(only) is tuple or type(only) is str else only

	"""
	Count the total number of tokens encountered and a separate count for each token.
	"""
	tokens = 0
	counts = { }
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
				if not only:
					for token in document['tokens']:
						counts[token] = counts.get(token, 0) + 1
				else:
					"""
					Convert each item in the list of tokens for which to compute the probability into a tuple.
					"""
					for item_set in only:
						item_set = (item_set, ) if type(item_set) is str else item_set
						min_count = min(document['tokens'].count(item) for item in item_set )

						if len(item_set) > 1:
							counts[item_set] = counts.get(item_set, 0) + min_count
						else:
							item = item_set[0]
							counts[item] = counts.get(item, 0) + min_count

	"""
	Compute the probability by dividing the count by the number of tokens.
	"""
	if tokens:
		return { token: count / tokens for token, count in counts.items() }

	return { }
