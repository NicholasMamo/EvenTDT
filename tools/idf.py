#!/usr/bin/env python3

"""
A tool to create a TF-IDF scheme from a corpus of tweets.

To run the script, use:

.. code-block:: bash

    ./implementation/consume.py \\
	-f data/sample.json \\
	-o data/idf.json

Accepted arguments:

	- ``-f --file``							*<Required>* The file to use to construct the TF-IDF scheme.
	- ``-o --output``						*<Required>* The file where to save the TF-IDF scheme.
	- ``--remove-unicode-entities``			*<Optional>* A boolean indicating whether to remove unicode entities.
	- ``--normalize-words``					*<Optional>* A boolean indicating whether to normalize words with repeating characters.
	- ``-character-normalization-count``	*<Optional>* The number of times a character must repeat for it to be normalized. Used only with the ``--normalize-words`` flag.
"""

import argparse
import copy
import json
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', 'eventdt')
if path not in sys.path:
    sys.path.append(path)

from nlp.term_weighting.tfidf import TFIDF
from nlp.tokenizer import Tokenizer
from objects.exportable import Exportable

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``							*<Required>* The file to use to construct the TF-IDF scheme.
		- ``-o --output``						*<Required>* The file where to save the TF-IDF scheme.
		- ``--remove-unicode-entities``			*<Optional>* A boolean indicating whether to remove unicode entities.
		- ``--normalize-words``					*<Optional>* A boolean indicating whether to normalize words with repeating characters.
		- ``-character-normalization-count``	*<Optional>* The number of times a character must repeat for it to be normalized. Used only with the ``--normalize-words`` flag.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Consume a corpus of tweets.")

	"""
	Parameters that define how the corpus should be collected.
	"""

	parser.add_argument('-f', '--file', type=str, required=True,
						help='<Required> The file to use to construct the TF-IDF scheme.')
	parser.add_argument('-o', '--output', type=str, required=True,
						help='<Required> The file where to save the TF-IDF scheme.')
	parser.add_argument('--remove-unicode-entities', action="store_true",
						help='<Optional> A boolean indicating whether to remove unicode entities.')
	parser.add_argument('--normalize-words', action="store_true",
						help='<Optional> A boolean indicating whether to normalize words with repeating characters.')
	parser.add_argument('--character-normalization-count', type=int, required=False, default=3,
						help='<Optional> The number of times a character must repeat for it to be normalized. Used only with the --normalize-words flag.')

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()
	tfidf = construct(file=args.file, normalize_words=args.normalize_words,
					  character_normalization_count=args.character_normalization_count,
					  remove_unicode_entities=args.remove_unicode_entities)
	save(tfidf, args.output)

def construct(file, *args, **kwargs):
	"""
	Construct the TF-IDF scheme from the file.
	The scheme is constructed one line at a time.

	Any additional arguments and keyword arguments are passed on to the :func:`~nlp.tokenizer.Tokenizer.__init__` constructor.

	:param file: The path to the file to use to construct the TF-IDF scheme.
	:type file: str

	:return: The TF-IDF scheme constructed from the file.
	:rtype: :class:`~nlp.term_weighting.tfidf.TFIDF`
	"""

	documents, idf = 0, { }
	tokenizer = Tokenizer(*args, **kwargs)

	"""
	Open the file and iterate over every tweet.
	Tokenize those tweets and use them to update the TF-IDF table.
	"""
	with open(file, 'r') as f:
		for line in f:
			documents = documents + 1
			tweet = json.loads(line)
			tokens = tokenize(tweet, tokenizer)
			idf = update(idf, tokens)

	return TFIDF(documents=documents, idf=idf)

def tokenize(tweet, tokenizer):
	"""
	Convert the given tweet into a document.

	:param tweet: The tweet to tokenize.
	:type tweet: dict
	:param tokenizer: The tokenizer to use to tokenize the tweet.
	:type tokenizer: :class:`~nlp.tokenizer.Tokenizer`

	:return: A list of tokens from the tweet.
	:rtype: list of str
	"""

	"""
	The text used for the document depend on what kind of tweet it is.
	If the tweet is too long to fit in the tweet, the full text is used;

	Retain the comment of a quoted status.
	However, if the tweet is a plain retweet, get the full text.
	"""
	while "retweeted_status" in tweet:
		tweet = tweet["retweeted_status"]

	if "extended_tweet" in tweet:
		text = tweet["extended_tweet"].get("full_text", tweet.get("text", ""))
	else:
		text = tweet.get("text", "")

	return tokenizer.tokenize(text)

def update(idf, tokens):
	"""
	Update the given IDF table with the given tokens.

	:param idf: The IDF table as a dictionary.
				The keys are the tokens and the values are the document frequencies.
	:type idf: dict
	:param tokens: The tokens to add to the IDF.
				   The function automatically gets the set of tokens to remove duplicates.
	:type: list of str
	"""

	idf = copy.deepcopy(idf)
	for token in set(tokens):
		idf[token] = idf.get(token, 0) + 1

	return idf

def save(tfidf, output):
	"""
	Save the given TF-IDF scheme to file.

	:param tfidf: The TF-IDF scheme.
	:type tf-idf: :class:`~nlp.term_weighting.tfidf.TFIDF`
	:param output: The path to the file where to save the TF-IDF scheme.
	:type output: str
	"""

	tfidf = { 'tfidf': tfidf }
	with open(output, 'w') as f:
		f.write(json.dumps(Exportable.encode(tfidf)))

if __name__ == "__main__":
	main()
