"""
General functions available to all ATE functions.
"""

import json

def vocabulary(corpora):
	"""
	Extract the vocabulary from the given corpora.

	:param corpora: A corpus, or corpora, of documents.
					If a string is given, it is assumed to be one corpus.
					If a list is given, it is assumed to be a list of corpora.

					.. note::

						It is assumed that the corpora were extracted using the tokenizer tool.
						Therefore each line should be a JSON string representing a document.
						Each document should have a `tokens` attribute.
	:type corpora: str or list of str

	:return: A list of tokens in the corpora.
	:rtype: list of str
	"""

	vocabulary = [ ]

	"""
	Convert the corpora into a list if they aren't already.
	"""
	corpora = [ corpora ] if type(corpora) is str else corpora

	for corpus in corpora:
		with open(corpus, 'r') as f:
			for line in f:
				document = json.loads(line)
				vocabulary.extend(document['tokens'])

		vocabulary = list(set(vocabulary))

	return vocabulary
