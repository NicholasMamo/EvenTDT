#!/usr/bin/env python3

"""
A tool to automatically extract terms from the given corpora.

To run the script, use:

.. code-block:: bash

    ./tools/terms.py \\
	-f data/tokenized_corpus.json \\
	-m tfidf \\
	--tfidf data/idf.json

Accepted arguments:

	- ``-f --files``		*<Required>* The input corpora from where to extract domain-specific terms.
	- ``-m --method``		*<Required>* The method to use to look for similar keywords; supported: `TFIDF`.
	- ``--tfidf``			*<Required>* The TF-IDF scheme to use to extract terms (used only with the `TF-IDF` method).
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
from ate.stat.tfidf import TFIDFExtractor

parser = argparse.ArgumentParser(description="Extract terms from domain-specific corpora.")
def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --files``		*<Required>* The input corpora from where to extract domain-specific terms.
		- ``-m --method``		*<Required>* The method to use to look for similar keywords; supported: `TFIDF`.
		- ``--tfidf``			*<Required>* The TF-IDF scheme to use to extract terms (used only with the `TF-IDF` method).

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser.add_argument('-f', '--files',
						nargs='+', required=True,
						help='<Required> The input corpora from where to extract domain-specific terms.')
	parser.add_argument('-m', '--method',
						type=method, required=True,
						help='<Required> The method to use to look for similar keywords; supported: `TFIDF`.')
	parser.add_argument('--tfidf', required=False,
						help='<Required> The TF-IDF scheme to use to extract terms (used only with the `TF-IDF` method).')

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

	extractor = instantiate(args)
	
	print(cmd)

def instantiate(args):
	"""
	Instantiate the method based on the arguments that it accepts.

	:param args: The command-line arguments.
	:type args: :class:`argparse.Namespace`

	:return: The created extractor.
	:rtype: :class:`~ate.extractor.Extractor`
	"""

	if args.method == TFIDFExtractor:
		if not args.tfidf:
			parser.error("The TF-IDF scheme is required with the TF-IDF method.")

		return args.method(tools.load(args.tfidf))

def method(method):
	"""
	Convert the given string into an ATE class.
	The accepted classes are:

		#. :func:`~ate.stat.tfidf.TFIDFExtractor`,

	:param method: The method string.
	:type method: str

	:return: The class type that corresponds to the given method.
	:rtype: class

	:raises argparse.ArgumentTypeError: When the given method string is invalid.
	"""

	methods = {
		'tfidf': TFIDFExtractor,
	}

	if method.lower() in methods:
		return methods[method.lower()]

	raise argparse.ArgumentTypeError(f"Invalid method value: {method}")

if __name__ == "__main__":
	main()
