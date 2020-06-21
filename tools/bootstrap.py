#!/usr/bin/env python3

"""
A tool that receives a seed set of terms and looks for similar terms in the given corpora.

To run the script, use:

.. code-block:: bash

    ./tools/bootstrap.py \\
	-s data/seed.txt \\
	-f data/tokenized_corpus.json

Accepted arguments:

	- ``-s --seed``			*<Required>* The path to the file containing seed keywords, expected to contain one keyword on each line.
	- ``-f --files``		*<Required>* The input corpora where to look for similar keywords.
	- ``--m --method``		*<Required>* The method to use to look for similar keywords; supported: `PMI`, `CHI`.
	- ``-i --iterations``	*<Optional>* The number of iterations to spend bootstrapping; defaults to 1.
	- ``-k --keep``			*<Optional>* The number of keywords to keep after each iteration; defaults to 5.
	- ``-c --cutoff``		*<Optional>* The number of candidate keywords to consider, based on probability from the given corpora; defaults to 100.
"""

import argparse
import copy
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

from ate.bootstrapping.probability import p, PMI, CHI

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-s --seed``			*<Required>* The path to the file containing seed keywords, expected to contain one keyword on each line.
		- ``-f --files``		*<Required>* The input corpora where to look for similar keywords.
		- ``-m --method``		*<Required>* The method to use to look for similar keywords; supported: `PMI`, `CHI`.
		- ``-i --iterations``	*<Optional>* The number of iterations to spend bootstrapping; defaults to 1.
		- ``-k --keep``			*<Optional>* The number of keywords to keep after each iteration; defaults to 5.
		- ``-c --cutoff``		*<Optional>* The number of candidate keywords to consider, based on probability from the given corpora; defaults to 100.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser = argparse.ArgumentParser(description="Bootstrap a seed set of terms.")

	parser.add_argument('-s', '--seed',
						required=True,
						help='<Required> The path to the file containing seed keywords, expected to contain one keyword on each line.')
	parser.add_argument('-f', '--files',
						nargs='+', required=True,
						help='<Required> The input corpora where to look for similar keywords.')
	parser.add_argument('-m', '--method',
						type=method, required=True,
						help='<Required> The method to use to look for similar keywords; supported: `PMI`, `CHI`.')
	parser.add_argument('-i', '--iterations',
						type=int, required=False, default=1,
						help='<Optional> The number of iterations to spend bootstrapping; defaults to 1.')
	parser.add_argument('-k', '--keep',
						type=int, required=False, default=5,
						help='<Optional> The number of keywords to keep after each iteration; defaults to 5.')
	parser.add_argument('-c', '--cutoff',
						type=int, required=False, default=100,
						help='<Optional> The number of candidate keywords to consider, based on probability from the given corpora; defaults to 100.')

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
	cmd = meta(args)

	seed = load_seed(args.seed)
	cmd['seed'] = seed
	print(cmd)

def load_seed(seed_file):
	"""
	Load the seed words from the given seed file.
	The function expects a file with one seed word on each line.

	:param seed_file: The path to the seed file.
	:type seed_file: str

	:return: A list of seed words.
	:rtype: list of str
	"""

	seed_list = [ ]

	with open(seed_file, 'r') as f:
		seed_list.extend(f.readlines())

	seed_list = [ word.strip() for word in seed_list ]
	return seed_list

def meta(args):
	"""
	Get the meta arguments.

	:param args: The command-line arguments.
	:type args: :class:`argparse.Namespace`

	:return: The meta arguments as a dictionary.
	:rtype: dict
	"""

	meta = copy.deepcopy(vars(args))
	meta['method'] = str(meta['method'])
	return meta

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
