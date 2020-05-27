#!/usr/bin/env python3

"""
A tool to tokenize a corpus of tweets.
The tokenizer can be used to pre-process a corpus.

Each line in the tokenizer corresponds to a tweet.
Each line is a JSON object containing, at minimum, the tweet ID, the text used for the tokenization and the tokens.

To run the script, use:

.. code-block:: bash

    ./tools/tokenizer.py \\
	-f data/sample.json \\
	-o data/idf.json \\
	--remove-unicode-entities \\
	--normalize-words --stem

Accepted arguments:

	- ``-f --file``							*<Required>* The file to use to construct the tokenized corpus.
	- ``-o --output``						*<Required>* The file where to save the tokenized corpus.
	- ``--remove-unicode-entities``			*<Optional>* Remove unicode entities from the tweets.
	- ``--normalize-words``					*<Optional>* Normalize words with repeating characters in them.
	- ``--character-normalization-count``	*<Optional>* The number of times a character must repeat for it to be normalized. Used only with the ``--normalize-words`` flag.
	- ``-stem``								*<Optional>* Stem the tokens when constructing the tokenized corpus.

"""

import argparse
import json
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', 'eventdt')
if path not in sys.path:
    sys.path.append(path)

from nlp.tokenizer import Tokenizer

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``							*<Required>* The file to use to construct the tokenized corpus.
		- ``-o --output``						*<Required>* The file where to save the tokenized corpus.
		- ``--remove-unicode-entities``			*<Optional>* Remove unicode entities from the tweets.
		- ``--normalize-words``					*<Optional>* Normalize words with repeating characters in them.
		- ``--character-normalization-count``	*<Optional>* The number of times a character must repeat for it to be normalized. Used only with the ``--normalize-words`` flag.
		- ``-stem``								*<Optional>* Stem the tokens when constructing the tokenized corpus.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Tokenize a corpus of tweets.")

	"""
	Parameters that define how the corpus should be collected.
	"""

	parser.add_argument('-f', '--file', type=str, required=True,
						help='<Required> The file to use to construct the tokenized corpus.')
	parser.add_argument('-o', '--output', type=str, required=True,
						help='<Required> The file where to save the tokenized corpus.')
	parser.add_argument('--remove-unicode-entities', action="store_true",
						help='<Optional> Remove unicode entities from the tweets.')
	parser.add_argument('--normalize-words', action="store_true",
						help='<Optional> Normalize words with repeating characters in them.')
	parser.add_argument('--character-normalization-count', type=int, required=False, default=3,
						help='<Optional> The number of times a character must repeat for it to be normalized. Used only with the --normalize-words flag.')
	parser.add_argument('--stem', action="store_true",
						help='<Optional> Stem the tokens when constructing the tokenized corpus.')

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	"""
	Set up the arguments, create the tokenizer and prepare the data directory.
	"""
	args = setup_args()
	tokenizer = Tokenizer(normalize_words=args.normalize_words,
						  character_normalization_count=args.character_normalization_count,
						  remove_unicode_entities=args.remove_unicode_entities, stem=args.stem)
	prepare_output(args.output)

def prepare_output(output):
	"""
	Create the data directory if it does not exist.

	:param output: The output path.
	:type output: str
	"""

	dir = os.path.dirname(output)
	if not os.path.exists(dir):
		os.makedirs(dir)

def tokenize(tweet, tokenizer):
	"""
	Tokenize the given tweet.
def get_text(tweet):
	"""
	Extract the text from the given tweet.
	The text used depends on the type of tweet.
	The full text is always sought.

	:param tweet: The tweet to tokenize.
	:type tweet: dict

	:return: The text to tokenize from the tweet.
	:rtype: str
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
		return tweet["extended_tweet"].get("full_text", tweet.get("text", ""))
	else:
		return tweet.get("text", "")

if __name__ == "__main__":
	main()
