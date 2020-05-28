"""
Methods that evaluate unithood or termhood based on probability.
"""

import json

def p(corpora):
	"""
	Calculate the probability of tokens appearing in the corpus.
	The probability is computed in terms of all tokens.

	:param corpora: A corpus, or corpora, of documents.
					If a string is given, it is assumed to be one corpus.
					If a list is given, it is assumed to be a list of corpora.

					It is assumed that the corpora were extracted using the tokenizer tool.
					Therefore each line should be a JSON string representing a document.
					Each document should have a `tokens` attribute.
	:type corpora: str or list of str

	:return: A dictionary with tokens as keys and probabilities as values.
	:rtype dict:
	"""

	"""
	Convert the corpora into a list if they aren't already.
	"""
	corpora = [ corpora ] if type(corpora) is str else corpora

	"""
	Count the total number of tokens encountered and a separate count for each token.
	"""
	tokens = 0
	counts = { }
	for corpus in corpora:
		with open(corpus, 'r') as f:
			for line in f:
				document = json.loads(line)
				tokens += len(document['tokens'])
				for token in document['tokens']:
					counts[token] = counts.get(token, 0) + 1

	"""
	Compute the probability by dividing the count by the number of tokens.
	"""
	if tokens:
		return { token: count / tokens for token, count in counts.items() }

	return { }
