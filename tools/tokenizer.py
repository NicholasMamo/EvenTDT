#!/usr/bin/env python3

"""
A tool to tokenize a corpus of tweets.
The tokenizer can be used to pre-process a corpus.

Each line in the tokenizer corresponds to a tweet.
Each line is a JSON object containing, at minimum, the tweet ID, the text used for the tokenization and the tokens.

Part-of-speech extraction can be specified by using the `--nouns`, `--proper-nouns`, `--verbs` and `--adjectives` arguments.
If none are given, all tokens are collected, including other parts-of-speech, like adverbs.

To run the script, use:

.. code-block:: bash

    ./tools/tokenizer.py \\
	-f data/sample.json \\
	-o data/idf.json \\
	--remove-unicode-entities \\
	--remove-stopwords \\
	--normalize-words --stem

Accepted arguments:

	- ``-f --file``							*<Required>* The file to use to construct the tokenized corpus.
	- ``-o --output``						*<Required>* The file where to save the tokenized corpus.
	- ``-k --keep``							*<Optional>* The tweet attributes to store.
	- ``--remove-retweets``					*<Optional>* Exclude retweets from the corpus.
	- ``--remove-unicode-entities``			*<Optional>* Remove unicode entities from the tweets.
	- ``--normalize-words``					*<Optional>* Normalize words with repeating characters in them.
	- ``--character-normalization-count``	*<Optional>* The number of times a character must repeat for it to be normalized. Used only with the ``--normalize-words`` flag.
	- ``--remove-stopwords``				*<Optional>* Remove stopwords from the tokens.
	- ``-stem``								*<Optional>* Stem the tokens when constructing the tokenized corpus.
	- ``--nouns``							*<Optional>* Extract nouns from the corpus.
	- ``--proper-nouns``					*<Optional>* Extract proper nouns from the corpus.
	- ``--verbs``							*<Optional>* Extract verbs from the corpus.
	- ``--adjectives``						*<Optional>* Extract adjectives from the corpus.

"""

import argparse
import json
import os
import sys

from nltk.corpus import stopwords

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
		- ``-k --keep``							*<Optional>* The tweet attributes to store.
		- ``--remove-retweets``					*<Optional>* Exclude retweets from the corpus.
		- ``--remove-unicode-entities``			*<Optional>* Remove unicode entities from the tweets.
		- ``--normalize-words``					*<Optional>* Normalize words with repeating characters in them.
		- ``--character-normalization-count``	*<Optional>* The number of times a character must repeat for it to be normalized. Used only with the ``--normalize-words`` flag.
		- ``--remove-stopwords``				*<Optional>* Remove stopwords from the tokens.
		- ``-stem``								*<Optional>* Stem the tokens when constructing the tokenized corpus.
		- ``--nouns``							*<Optional>* Extract nouns from the corpus.
		- ``--proper-nouns``					*<Optional>* Extract proper nouns from the corpus.
		- ``--verbs``							*<Optional>* Extract verbs from the corpus.
		- ``--adjectives``						*<Optional>* Extract adjectives from the corpus.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser = argparse.ArgumentParser(description="Tokenize a corpus of tweets.")

	"""
	Parameters that define how the corpus should be collected.
	"""

	parser.add_argument('-f', '--file', type=str, required=True,
						help='<Required> The file to use to construct the tokenized corpus.')
	parser.add_argument('-o', '--output', type=str, required=True,
						help='<Required> The file where to save the tokenized corpus.')
	parser.add_argument('-k', '--keep', type=str, nargs='+', required=False,
						help='<Optional> The tweet attributes to store.')
	parser.add_argument('--remove-retweets', action="store_true",
						help='<Optional> Exclude retweets from the corpus.')
	parser.add_argument('--remove-unicode-entities', action="store_true",
						help='<Optional> Remove unicode entities from the tweets.')
	parser.add_argument('--remove-stopwords', action="store_true",
						help='<Optional> Remove stopwords from the tokens.')
	parser.add_argument('--normalize-words', action="store_true",
						help='<Optional> Normalize words with repeating characters in them.')
	parser.add_argument('--character-normalization-count', type=int, required=False, default=3,
						help='<Optional> The number of times a character must repeat for it to be normalized. Used only with the --normalize-words flag.')
	parser.add_argument('--stem', action="store_true",
						help='<Optional> Stem the tokens when constructing the tokenized corpus.')
	parser.add_argument('--nouns', action="store_true",
						help='<Optional> Extract nouns from the corpus.')
	parser.add_argument('--proper-nouns', action="store_true",
						help='<Optional> Extract proper nouns from the corpus.')
	parser.add_argument('--verbs', action="store_true",
						help='<Optional> Extract verbs from the corpus.')
	parser.add_argument('--adjectives', action="store_true",
						help='<Optional> Extract adjectives from the corpus.')

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
	prepare_output(args.output)
	tags = get_tags(nouns=args.nouns, proper_nouns=args.proper_nouns,
					verbs=args.verbs, adjectives=args.adjectives)
	tokenizer = Tokenizer(normalize_words=args.normalize_words, pos=tags,
						  character_normalization_count=args.character_normalization_count,
						  remove_unicode_entities=args.remove_unicode_entities, stem=args.stem,
						  stopwords=({ } if not args.remove_stopwords else stopwords.words('english')))
	tokenize_corpus(args.file, args.output, tokenizer, args.keep, args.remove_retweets)

def prepare_output(output):
	"""
	Create the data directory if it does not exist.

	:param output: The output path.
	:type output: str
	"""

	dir = os.path.dirname(output)
	if not os.path.exists(dir):
		os.makedirs(dir)

def get_tags(nouns, proper_nouns, verbs, adjectives):
	"""
	Get the parts-of-speech tags based on the command-line arguments.
	If neither of the tags are given, `None` is returned.

	:param nouns: A boolean indicating whether to extract nouns.
	:type nouns: bool
	:param proper_nouns: A boolean indicating whether to extract proper nouns.
	:type proper_nouns: bool
	:param verbs: A boolean indicating whether to extract verbs.
	:type verbs: bool
	:param adjectives: A boolean indicating whether to extract adjectives.
	:type adjectives: bool

	:return: A list of parts-of-speech tags corresponding to the given flags, or `None` if all tags should be collected.
	:rtype: None or list of str
	"""

	"""
	If no command-line arguments for parts-of-speech tags are given, collect all tags.
	This happens by returning `None`.
	"""
	if not any([ nouns, proper_nouns, verbs, adjectives ]):
		return None

	map = {
		'nouns': [ 'NN', 'NNS' ],
		'proper_nouns': [ 'NNP', 'NNPS' ],
		'verbs': [ 'VB', 'VBG', 'VBD', 'VBN', 'VBP', 'VBZ' ],
		'adjectives': [ 'JJ', 'JJR', 'JJS' ]
	}

	tags = [ ]
	if nouns:
		tags.extend(map['nouns'])

	if proper_nouns:
		tags.extend(map['proper_nouns'])

	if verbs:
		tags.extend(map['verbs'])

	if adjectives:
		tags.extend(map['adjectives'])

	return tags

def tokenize_corpus(file, output, tokenizer, keep=None, remove_retweets=False):
	"""
	Tokenize the corpus represented by the given file.
	The function iterates over each tweet, tokenizes it and saves it to the file.

	:param file: The path to the corpus file.
	:type file: str
	:param output: The output path.
				   This function assumes that the directory path exists.
	:type output: str
	:param tokenizer: The tokenizer to use to create the tokenized corpus.
	:type tokenizer: :class:`~nlp.tokenizer.Tokenizer`
	:param keep: The list of tweet attributes to store for each tweet.
				 By default, the tweet ID is always kept.
	:type keep: list or None
	:param remove_retweets: A boolean indicating whether to xclude retweets from the corpus.
	:type remove_retweets: bool
	"""

	keep = keep or [ ]

	with open(file, 'r') as infile, \
		  open(output, 'w') as outfile:
		for line in infile:
			tweet = json.loads(line)

			"""
			Skip the tweet if retweets should be excluded.
			"""
			if remove_retweets and 'retweeted_status' in tweet:
				continue

			text = get_text(tweet)
			tokens = tokenizer.tokenize(text)

			"""
			By default, each tweet object stores:

			- The tweet ID,
			- The text used to extract tokens, and
			- The tokens themselves.
			"""
			object = { 'id': tweet['id'], 'text': tweet['text'],
					   'tokens': tokens }

			"""
			Other attributes can be specified as arguments.
			"""
			for attribute in keep:
				object[attribute] = tweet.get(attribute)

			outfile.write(f"{ json.dumps(object) }\n")

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
