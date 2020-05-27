#!/usr/bin/env python3

"""
A tool to tokenize a corpus of tweets.
The tokenizer can be used to pre-process a corpus.

Each line in the tokenizer corresponds to a tweet.
Each line is a JSON object containing, at minimum, the tweet ID and the tokens.

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

	args = setup_args()

def tokenize(tweet, tokenizer):
	"""
	Tokenize the given tweet.
	The text used depends on the type of tweet.
	The full text is always sought.

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

if __name__ == "__main__":
	main()
