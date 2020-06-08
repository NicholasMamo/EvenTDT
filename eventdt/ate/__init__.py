"""
Package-level functions that are likely to be useful to both linguistic and statistical approaches.
"""

def total_documents(corpora):
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

	:return: The number of documents in the given corpora.
	:rtype: float
	"""

	documents = 0

	"""
	Convert the corpora into a list if they aren't already.
	"""
	corpora = [ corpora ] if type(corpora) is str else corpora

	for corpus in corpora:
		with open(corpus, 'r') as f:
			for line in f:
				documents += 1

	return documents
