#!/usr/bin/env python3

"""
A tool to automatically extract participants from the given corpora.
This tool is meant to run on the understanding corpora to extract the event's participants.

To run the script, use:

.. code-block:: bash

    ./tools/participants.py \\
	-f data/understanding.json \\
	--extractor EntityExtractor \\
	-o data/participants.json

Accepted arguments:

	- ``-f --file``			*<Required>* The input corpus from where to extract participants.
	- ``-e --extractor``	*<Required>* The extractor to use to extract candidate participants; supported: `EntityExtractor`, `TokenExtractor`, `TwitterNEREntityExtractor`.
	- ``-o --output``		*<Required>* The path to the file where to store the extracted participants.
"""

import argparse
import json
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

import tools
from apd import ParticipantDetector
from apd.extractors import local
from nlp.document import Document
from nlp.tokenizer import Tokenizer

parser = argparse.ArgumentParser(description="Extract terms from domain-specific corpora.")
def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``			*<Required>* The input corpus from where to extract participants.
		- ``-e --extractor``	*<Required>* The extractor to use to extract candidate participants; supported: `EntityExtractor`, `TokenExtractor`, `TwitterNEREntityExtractor`.
		- ``-o --output``		*<Required>* The path to the file where to store the extracted participants.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser.add_argument('-f', '--file', type=str, required=True,
						help='<Required> The input corpus from where to extract participants.')
	parser.add_argument('-e', '--extractor', type=extractor, required=True,
						help='<Required> he extractor to use to extract candidate participants; supported: `EntityExtractor`, `TokenExtractor`, `TwitterNEREntityExtractor`.')
	parser.add_argument('-o', '--output', type=str, required=True,
						help='<Required> The path to the file where to store the extracted terms.')

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()

	"""
	Get the meta arguments.
	"""
	cmd = tools.meta(args)
	cmd['extractor'] = str(vars(args)['extractor'])

	participants = detect(args.file, args.extractor)
	tools.save(args.output, { 'meta': cmd, 'participants': participants })

def detect(filename, extractor):
	"""
	Detect participants from the given corpus.

	:param filename: The path to the corpus from where to detect participants.
	:type filename: str
	:param extractor: The class of the extractor with which to extract candidate participants.
	:type extractor: :class:`~apd.extractors.extractor.Extractor`

	:return: A list of participants detected in the corpus.
	:rtype: list of str
	"""

	detector = ParticipantDetector(extractor())
	corpus = [ ]
	with open(filename) as f:
		for line in f:
			tweet = json.loads(line)
			while "retweeted_status" in tweet:
				tweet = tweet["retweeted_status"]

			if "extended_tweet" in tweet:
				text = tweet["extended_tweet"].get("full_text", tweet.get("text", ""))
			else:
				text = tweet.get("text", "")

			document = Document(text)
			corpus.append(document)

	participants, _, _, = detector.detect(corpus)
	return participants

def extractor(method):
	"""
	Convert the given string into an extractor class.
	The accepted classes are:

		#. :func:`~apd.extractors.local.EntityExtractor`
		#. :func:`~apd.extractors.local.TokenExtractor`
		#. :func:`~apd.extractors.local.TwitterNEREntityExtractor`

	:param method: The extractor string.
	:type method: str

	:return: The extractor type that corresponds to the given method.
	:rtype: class
	"""

	methods = {
		'entityextractor': local.EntityExtractor,
		'tokenextractor': local.TokenExtractor,
	}

	if method.lower() in methods:
		return methods[method.lower()]
	elif method.lower() == 'twitternerentityextractor':
		from apd.extractors.local.twitterner_entity_extractor import TwitterNEREntityExtractor
		return TwitterNEREntityExtractor

	raise argparse.ArgumentTypeError(f"Invalid method value: {method}")

if __name__ == "__main__":
	main()
