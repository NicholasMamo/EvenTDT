#!/usr/bin/env python3

"""
A tool to automatically extract participants from the given corpora.
This tool is meant to run on the understanding corpora to extract the event's participants.

To run the script, use:

.. code-block:: bash

    ./tools/participants.py \\
	-f data/understanding.json \\
	--extractor EntityExtractor \\
	--scorer TFScorer \\
	-o data/participants.json

Accepted arguments:

	- ``-f --file``			*<Required>* The input corpus from where to extract participants.
	- ``-o --output``		*<Required>* The path to the file where to store the extracted participants.
	- ``--extractor``		*<Optional>* The extractor to use to extract candidate participants; supported: `EntityExtractor` (default), `TokenExtractor`, `TwitterNEREntityExtractor`.
	- ``--scorer``			*<Optional>* The scorer to use to score candidate participants; supported: `TFScorer` (default), `DFScorer`, `LogDFScorer`, `LogTFScorer`.
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
from apd.scorers.local import *
from nlp.document import Document
from nlp.tokenizer import Tokenizer

parser = argparse.ArgumentParser(description="Extract event participants from the understanding corpora.")
def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``			*<Required>* The input corpus from where to extract participants.
		- ``-o --output``		*<Required>* The path to the file where to store the extracted participants.
		- ``--extractor``		*<Optional>* The extractor to use to extract candidate participants; supported: `EntityExtractor` (default), `TokenExtractor`, `TwitterNEREntityExtractor`.
		- ``--scorer``			*<Optional>* The scorer to use to score candidate participants; supported: `TFScorer` (default), `DFScorer`, `LogDFScorer`, `LogTFScorer`.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser.add_argument('-f', '--file', type=str, required=True,
						help='<Required> The input corpus from where to extract participants.')
	parser.add_argument('-o', '--output', type=str, required=True,
						help='<Required> The path to the file where to store the extracted terms.')
	parser.add_argument('--extractor', type=extractor, required=False, default=local.EntityExtractor,
						help='<Required> The extractor to use to extract candidate participants; supported: `EntityExtractor`, `TokenExtractor`, `TwitterNEREntityExtractor`.')
	parser.add_argument('--scorer', type=scorer, required=False, default=TFScorer,
						help='<Required> The scorer to use to score candidate participants; supported: `TFScorer` (default), `DFScorer`, `LogDFScorer`, `LogTFScorer`')

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
	cmd['scorer'] = str(vars(args)['scorer'])

	participants = detect(args.file, args.extractor, args.scorer)
	tools.save(args.output, { 'meta': cmd, 'participants': participants })

def detect(filename, extractor, scorer, *args, **kwargs):
	"""
	Detect participants from the given corpus.

	:param filename: The path to the corpus from where to detect participants.
	:type filename: str
	:param extractor: The class of the extractor with which to extract candidate participants.
	:type extractor: :class:`~apd.extractors.extractor.Extractor`
	:param scorer: The class of the scorer with which to score candidate participants.
	:type scorer: :class:`~apd.scorers.scorer.Scorer`

	:return: A list of participants detected in the corpus.
	:rtype: list of str
	"""

	"""
	Create all the components of the participant detector.
	"""
	extractor = create_extractor(extractor, *args, **kwargs)
	scorer = create_scorer(scorer, *args, **kwargs)
	detector = ParticipantDetector(extractor, scorer)

	"""
	Load the corpus.
	"""
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

def create_extractor(extractor, *args, **kwargs):
	"""
	Create an extractor from the given class.

	:param extractor: The class of the extractor with which to extract candidate participants.
	:type extractor: :class:`~apd.extractors.extractor.Extractor`
	"""

	return extractor()

def create_scorer(scorer, *args, **kwargs):
	"""
	Create a scorer from the given class.

	:param scorer: The class of the scorer with which to score candidate participants.
	:type scorer: :class:`~apd.scorers.scorer.Scorer`
	"""

	return scorer()

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
	:rtype: :class:`~apd.extractors.extractor.Extractor`
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

def scorer(method):
	"""
	Convert the given string into a scorer class.
	The accepted classes are:

		#. :func:`~apd.scorers.local.DFScorer`
		#. :func:`~apd.scorers.local.LogDFScorer`
		#. :func:`~apd.scorers.local.LogTFScorer`
		#. :func:`~apd.scorers.local.TFScorer`

	:param method: The extractor string.
	:type method: str

	:return: The extractor type that corresponds to the given method.
	:rtype: :class:`~apd.scorers.scorer.Scorer`
	"""

	methods = {
		'dfscorer': DFScorer,
		'logdfscorer': LogDFScorer,
		'logtfscorer': LogTFScorer,
		'tfscorer': TFScorer,
	}

	if method.lower() in methods:
		return methods[method.lower()]

	raise argparse.ArgumentTypeError(f"Invalid method value: {method}")

if __name__ == "__main__":
	main()
