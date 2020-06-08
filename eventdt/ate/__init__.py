"""
Package-level functions that are likely to be useful to both linguistic and statistical approaches.
"""

import json

def total_documents(corpora, focus=None):
	"""
	Count the total number of documents in the given corpora.

	:param corpora: A corpus, or corpora, of documents.
					If a string is given, it is assumed to be one corpus.
					If a list is given, it is assumed to be a list of corpora.

					.. note::

						It is assumed that the corpora were extracted using the tokenizer tool.
						Therefore each line should be a JSON string representing a document.
						Each document should have a `tokens` attribute.
	:type corpora: str or list of str
	:param focus: The tokens for which to compute the document frequency.
				  If nothing is given, the document frequency is calculated for all tokens.
				  The tokens can be provided as:

				  - A single word,
				  - A list of tokens,
				  - A tuple, or
				  - A list of tuples.

				  A tuple can be used to compute joint frequencies.
	:type focus: None or str or list of str or tuple or list of tuple

	:return: The number of documents in the given corpora.
			 If one token or one tuple is given, the number of documents in which the token or tuple appears are returned.
			 If multiple tokens or tuples are given, a dictionary is given with the separate counts.
	:rtype: int or dict
	"""

	documents = { '*': 0 } if not focus else { }

	"""
	Convert the corpora into a list if they aren't already.
	Also convert the focus items into a list.
	"""
	corpora = [ corpora ] if type(corpora) is str else corpora
	focus = focus or [ ]
	focus = [ focus ] if type(focus) is tuple or type(focus) is str else focus
	focus = [ (itemset, ) if type(itemset) is str else itemset for itemset in focus ]

	"""
	Create the initial counts for all tokens and joint probabilities.
	This avoids returning missing probabilities for tokens or joint tokens that never appear.
	"""
	for itemset in focus:
		documents[itemset if len(itemset) > 1 else itemset[0]] = 0

	for corpus in corpora:
		with open(corpus, 'r') as f:
			for line in f:
				document = json.loads(line)

				"""
				If focus tokens or tuples were given, check which itemsets appear in the given documents.
				"""
				if focus:
					for itemset in focus:
						if all( item in document['tokens'] for item in itemset ):
							documents[itemset if len(itemset) > 1 else itemset[0]] += 1
				else:
					documents['*'] += 1

	if len(documents) == 1:
		return list(documents.values())[0]
	else:
		return documents
