"""
General functions available to all ATE functions.
"""

from nltk import sent_tokenize, word_tokenize, pos_tag

import json
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.tokenizer import Tokenizer

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

def nouns(corpora, stem=True):
	"""
	Extract the nouns from the given corpora.

	:param corpora: A corpus, or corpora, of documents.
					If a string is given, it is assumed to be one corpus.
					If a list is given, it is assumed to be a list of corpora.

					.. note::

						It is assumed that the corpora were extracted using the tokenizer tool.
						Therefore each line should be a JSON string representing a document.
						Each document should have a `tokens` attribute.
	:type corpora: str or list of str
	:param stem: A boolean indicating whether the nouns should be stemmed.
	:type stem: bool

	:return: A list of tokens in the corpora.
	:rtype: list of str
	"""

	nouns = [ ]

	"""
	Convert the corpora into a list if they aren't already.
	"""
	corpora = [ corpora ] if type(corpora) is str else corpora

	"""
	Extract the nouns from the corpora.
	"""
	for corpus in corpora:
		with open(corpus, 'r') as f:
			for line in f:
				document = json.loads(line)
				sentences = sent_tokenize(document['text'])
				tags = [ tag for sentence in sentences
				 			 for tag in pos_tag(word_tokenize(sentence)) ]
				nouns.extend([ word.lower() for (word, tag) in tags
									if tag.startswith('N') ])

	"""
	Remove duplicate nouns.
	"""
	nouns = list(set(nouns))

	"""
	Stem the tokens if need be.
	"""
	if stem:
		tokenizer = Tokenizer(stem=stem)
		nouns = [ token for noun in nouns
						for token in tokenizer.tokenize(noun)]

		"""
		Remove duplicate nouns that may have been created by stemming.
		"""
		nouns = list(set(nouns))

	return nouns
