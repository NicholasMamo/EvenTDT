#!/usr/bin/env python3

"""
A tool to create a TF-IDF scheme from a corpus of tweets.

To run the script, use:

.. code-block:: bash

    ./tools/idf.py \\
	-f data/sample.json \\
	-o data/idf.json \\
	--remove-unicode-entities \\
	--normalize-words --stem

Accepted arguments:

	- ``-f --file``							*<Required>* The file to use to construct the TF-IDF scheme.
	- ``-o --output``						*<Required>* The file where to save the TF-IDF scheme.
	- ``--remove-retweets``					*<Optional>* Exclude retweets from the corpus.
	- ``--remove-unicode-entities``			*<Optional>* Remove unicode entities from the TF-IDF scheme.
	- ``--normalize-words``					*<Optional>* Normalize words with repeating characters in them.
	- ``--character-normalization-count``	*<Optional>* The number of times a character must repeat for it to be normalized. Used only with the ``--normalize-words`` flag.
	- ``-stem``								*<Optional>* Stem the tokens when constructing the TF-IDF scheme.

"""

import argparse
import json
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', 'eventdt')
if path not in sys.path:
    sys.path.append(path)

from nlp.weighting.tfidf import TFIDF
from nlp.tokenizer import Tokenizer
from objects.exportable import Exportable
import twitter

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``							*<Required>* The file to use to construct the TF-IDF scheme.
		- ``-o --output``						*<Required>* The file where to save the TF-IDF scheme.
		- ``--remove-retweets``					*<Optional>* Exclude retweets from the corpus.
		- ``--remove-unicode-entities``			*<Optional>* Remove unicode entities from the TF-IDF scheme.
		- ``--normalize-words``					*<Optional>* Normalize words with repeating characters in them.
		- ``--character-normalization-count``	*<Optional>* The number of times a character must repeat for it to be normalized. Used only with the ``--normalize-words`` flag.
		- ``--stem``							*<Optional>* Stem the tokens when constructing the TF-IDF scheme.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser = argparse.ArgumentParser(description="Create a TF-IDF scheme from a corpus of tweets.")

	"""
	Parameters that define how the corpus should be collected.
	"""

	parser.add_argument('-f', '--file', type=str, required=True,
						help='<Required> The file to use to construct the TF-IDF scheme.')
	parser.add_argument('-o', '--output', type=str, required=True,
						help='<Required> The file where to save the TF-IDF scheme.')
	parser.add_argument('--remove-retweets', action="store_true",
						help='<Optional> Exclude retweets from the corpus.')
	parser.add_argument('--remove-unicode-entities', action="store_true",
						help='<Optional> Remove unicode entities from the TF-IDF scheme.')
	parser.add_argument('--normalize-words', action="store_true",
						help='<Optional> Normalize words with repeating characters in them.')
	parser.add_argument('--character-normalization-count', type=int, required=False, default=3,
						help='<Optional> The number of times a character must repeat for it to be normalized. Used only with the --normalize-words flag.')
	parser.add_argument('--stem', action="store_true",
						help='<Optional> Stem the tokens when constructing the TF-IDF scheme.')

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()
	tfidf = construct(file=args.file, remove_retweets=args.remove_retweets, normalize_words=args.normalize_words,
					  character_normalization_count=args.character_normalization_count,
					  remove_unicode_entities=args.remove_unicode_entities, stem=args.stem)
	save(tfidf, args.output)

def construct(file, remove_retweets, *args, **kwargs):
	"""
	Construct the TF-IDF scheme from the file.
	The scheme is constructed one line at a time.

	Any additional arguments and keyword arguments are passed on to the :func:`~nlp.tokenizer.Tokenizer.__init__` constructor.

	:param file: The path to the file to use to construct the TF-IDF scheme.
	:type file: str
	:param remove_retweets: A boolean indicating whether to xclude retweets from the corpus.
	:type remove_retweets: bool

	:return: The TF-IDF scheme constructed from the file.
	:rtype: :class:`~nlp.weighting.tfidf.TFIDF`
	"""

	documents, idf = 0, { }
	tokenizer = Tokenizer(*args, **kwargs)

	"""
	Open the file and iterate over every tweet.
	Tokenize those tweets and use them to update the TF-IDF table.
	"""
	with open(file, 'r') as f:
		for line in f:
			tweet = json.loads(line)

			"""
			Skip the tweet if retweets should be excluded.
			"""
			if remove_retweets and 'retweeted_status' in tweet:
				continue

			documents = documents + 1
			tokens = tokenize(tweet, tokenizer)
			idf = update(idf, tokens)

	return TFIDF(documents=documents, idf=idf)

def tokenize(tweet, tokenizer):
	"""
	Convert the given tweet into a document.
	The text used depends on the type of tweet.
	The full text is always sought.

	:param tweet: The tweet to tokenize.
	:type tweet: dict
	:param tokenizer: The tokenizer to use to tokenize the tweet.
	:type tokenizer: :class:`~nlp.tokenizer.Tokenizer`

	:return: A list of tokens from the tweet.
	:rtype: list of str
	"""

	text = twitter.full_text(tweet)
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

	:return: The updated IDF table.
	:rtype: dict
	"""

	for token in set(tokens):
		idf[token] = idf.get(token, 0) + 1

	return idf

def save(tfidf, output):
	"""
	Save the given TF-IDF scheme to file.

	:param tfidf: The TF-IDF scheme.
	:type tf-idf: :class:`~nlp.weighting.tfidf.TFIDF`
	:param output: The path to the file where to save the TF-IDF scheme.
	:type output: str
	"""

	"""
	Create the data directory if it does not exist.
	"""
	dir = os.path.dirname(output)
	if not os.path.exists(dir):
		os.makedirs(dir)

	tfidf = { 'tfidf': tfidf }
	with open(output, 'w') as f:
		f.write(json.dumps(Exportable.encode(tfidf)))

if __name__ == "__main__":
	main()
