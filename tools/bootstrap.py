#!/usr/bin/env python3

"""
A tool that receives a seed set of terms and looks for similar terms in the given corpora.

To run the script, use:

.. code-block:: bash

    ./tools/bootstrap.py \\
	-s foul yellow \\
	-f data/tokenized_corpus.json

Accepted arguments:

	- ``-s --seed``			*<Required>* The seed set of keywords.
	- ``-f --files``		*<Required>* The input corpora where to look for similar keywords.
	- ``--m --method``		*<Required>* The method to use to look for similar keywords; supported: `PMI`, `CHI`.
	- ``-i --iterations``	*<Optional>* The number of iterations to spend bootstrapping; defaults to 1.
"""

import argparse
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

from ate.bootstrapping.probability import PMI, CHI

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-s --seed``			*<Required>* The seed set of keywords.
		- ``-f --files``		*<Required>* The input corpora where to look for similar keywords.
		- ``-m --method``		*<Required>* The method to use to look for similar keywords; supported: `PMI`, `CHI`.
		- ``-i --iterations``	*<Optional>* The number of iterations to spend bootstrapping; defaults to 1.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser = argparse.ArgumentParser(description="Bootstrap a seed set of terms.")

	parser.add_argument('-s', '--seed',
						nargs='+', required=True,
						help='<Required> The seed set of keywords.')
	parser.add_argument('-f', '--files',
						nargs='+', required=True,
						help='<Required> The input corpora where to look for similar keywords.')
	parser.add_argument('-m', '--method',
						type=method, required=True,
						help='<Required> The method to use to look for similar keywords; supported: `PMI`, `CHI`.')
	parser.add_argument('-i', '--iterations',
						type=int, required=False, default=1,
						help='<Optional> The number of iterations to spend bootstrapping; defaults to 1.')

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()
	print(args)

def method(method):
	"""
	Convert the given string into a bootstrapping function.
	The accepted methods are:

		#. :func:`~ate.bootstrapping.probability.PMI`,
		#. :func:`~ate.bootstrapping.probability.CHI`

	:param method: The method string.
	:type method: str

	:return: The function that corresponds to the given method.
	:rtype: function

	:raises argparse.ArgumentTypeError: When the given method string is invalid.
	"""

	methods = {
		'pmi': PMI,
		'chi': CHI,
	}

	if method.lower() in methods:
		return methods[method.lower()]

	raise argparse.ArgumentTypeError(f"Invalid method value: {method}")

if __name__ == "__main__":
	main()
