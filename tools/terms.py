#!/usr/bin/env python3

"""
A tool to automatically extract terms from the given corpora.

To run the script, use:

.. code-block:: bash

    ./tools/terms.py \\
	-f data/tokenized_corpus.json \\
	-m tfidf \\
	--tfidf data/idf.json \\
	-o data/bootstrapped.json

Accepted arguments:

	- ``-f --files``		*<Required>* The input corpora from where to extract domain-specific terms.
	- ``-m --method``		*<Required>* The method to use to look for similar keywords; supported: `TF`, `TFIDF`, `Rank`, `Specificity`, `TFDCF`, `EFIDF`.
	- ``-o --output``		*<Required>* The path to the file where to store the extracted terms.
	- ``--tfidf``			*<Optional>* The TF-IDF scheme to use to extract terms (used only with the `TF-IDF` method).
	- ``--general``			*<Optional>* A path or paths to general corpora used for comparison with the domain-specific corpora (used only with the `Rank`, `Specificity` and `TF-DCF` methods).
	- ``--cutoff``			*<Optional>* The minimum term frequency to consider when ranking terms (used only with the `Specificity` method).
"""

import argparse
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

import tools
from logger import logger
from ate import linguistic
from ate.application import EFIDF
from ate.stat import TFExtractor, TFIDFExtractor
from ate.stat.corpus import RankExtractor, SpecificityExtractor, TFDCFExtractor

parser = argparse.ArgumentParser(description="Extract terms from domain-specific corpora.")
def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --files``		*<Required>* The input corpora from where to extract domain-specific terms.
		- ``-m --method``		*<Required>* The method to use to look for similar keywords; supported: `TF`, `TFIDF`, `Rank`, `Specificity`, `TFDCF`, `EFIDF`.
		- ``-o --output``		*<Required>* The path to the file where to store the extracted terms.
		- ``--tfidf``			*<Optional>* The TF-IDF scheme to use to extract terms (used only with the `TF-IDF` method).
		- ``--general``			*<Optional>* A path or paths to general corpora used for comparison with the domain-specific corpora (used only with the `Rank`, `Specificity` and `TF-DCF` methods).
		- ``--cutoff``			*<Optional>* The minimum term frequency to consider when ranking terms (used only with the `Specificity` method).

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser.add_argument('-f', '--files',
						nargs='+', required=True,
						help='<Required> The input corpora from where to extract domain-specific terms.')
	parser.add_argument('-m', '--method',
						type=method, required=True,
						help='<Required> The method to use to look for similar keywords; supported: `TF`, `TFIDF`, `Rank`, `Specificity`, `TFDCF`, `EFIDF`.')
	parser.add_argument('-o', '--output',
						type=str, required=True,
						help='<Required> The path to the file where to store the extracted terms.')
	parser.add_argument('--tfidf', required=False,
						help='<Optional> The TF-IDF scheme to use to extract terms (used only with the `TF-IDF` method).')
	parser.add_argument('--general',
						nargs='+', required=False,
						help='<Optional> A path or paths to general corpora used for comparison with the domain-specific corpora (used only with the `Rank`, `Specificity` and `TF-DCF` methods).')
	parser.add_argument('--cutoff',
						type=int, default=1, required=False,
						help='<Optional> The minimum term frequency to consider when ranking terms (used only with the `Specificity` method).')

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
	cmd['method'] = str(vars(args)['method'])

	"""
	Create the extractor and extract the terms.
	"""
	args = var(args)
	extractor = instantiate(args['method'],
							tfidf=args['tfidf'], general=args['general'], cutoff=args['cutoff'])
	terms = extractor.extract(args['files'])
	terms = sorted(terms.items(), key=lambda term: term[1], reverse=True)
	terms = [ { 'term': term, 'score': score, 'rank': rank + 1 } for rank, (term, score) in enumerate(terms) ]

	tools.save(args.output, { 'meta': cmd, 'terms': terms })

def instantiate(method, tfidf=None, general=None, cutoff=None):
	"""
	Instantiate the method based on the arguments that it accepts.

	:param method: The class type of the method to instantiate.
	:type method: :class:`~ate.extractor.Extractor`
	:param tfidf: The path to a file containing the TF-IDF scheme.
				  It is required with the :func:`~ate.stat.tfidf.TFIDFExtractor` and :class:`~ate.application.event.EFIDF`.
	:type tfidf: None or str
	:param general: A path, or paths, to files containing general corpora.
					This parameter is required for the :class:`~ate.stat.corpus.tfdcf.TFDCFExtractor`, :class:`~ate.stat.corpus.specificity.SpecificityExtractor` and :class:`~ate.stat.corpus.rank.RankExtractor`.
	:type general: None or str or list of str
	:param cutoff: The cut-off to use with the :class:`~ate.stat.corpus.rank.RankExtractor`.
	:type cutoff: None or int

	:return: The created extractor.
	:rtype: :class:`~ate.extractor.Extractor`
	"""

	if method == TFIDFExtractor:
		if tfidf is None:
			parser.error("The TF-IDF scheme is required with the TF-IDF method.")

		return method(tools.load(tfidf)['tfidf'])
	elif method == TFDCFExtractor:
		if general is None:
			parser.error("One or more paths to general corpora are required with TF-DCF method.")

		return method(general)
	elif method == SpecificityExtractor:
		if general is None:
			parser.error("One or more paths to general corpora are required with domain specificity method.")

		return method(general)
	elif method == RankExtractor:
		if general is None:
			parser.error("One or more paths to general corpora are required with rank difference method.")

		return method(general, cutoff=cutoff)
	elif method == EFIDF:
		if tfidf is None:
			parser.error("The TF-IDF scheme is required with the EF-IDF method.")

	return args.method()

def method(method):
	"""
	Convert the given string into an ATE class.
	The accepted classes are:

		#. :class:`~ate.stat.tfidf.TFExtractor`
		#. :class:`~ate.stat.tfidf.TFIDFExtractor`
		#. :class:`~ate.stat.corpus.rank.RankExtractor`
		#. :class:`~ate.stat.corpus.specificity.SpecificityExtractor`
		#. :class:`~ate.stat.corpus.tfdcf.TFDCFExtractor`
		#. :class:`~ate.application.event.EFIDF`

	:param method: The method string.
	:type method: str

	:return: The class type that corresponds to the given method.
	:rtype: :class:`~ate.extractor.Extractor`

	:raises argparse.ArgumentTypeError: When the given method string is invalid.
	"""

	methods = {
		'tf': TFExtractor,
		'tfidf': TFIDFExtractor,
		'rank': RankExtractor,
		'specificity': SpecificityExtractor,
		'tfdcf': TFDCFExtractor,
		'efidf': EFIDF,
	}

	if method.lower() in methods:
		return methods[method.lower()]

	raise argparse.ArgumentTypeError(f"Invalid method value: { method }")

if __name__ == "__main__":
	main()
