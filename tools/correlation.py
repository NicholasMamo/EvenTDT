#!/usr/bin/env python3

"""
The correlation tool receives a list of words and a list of files and computes their correlation.

To run the script, use:

.. code-block:: bash

    ./tools/correlation.py \\
	--terms first half
	--files data/tokenized_corpus.json \\
	--method CHI \\
	--output data/correlation.json

Accepted arguments:

	- ``-t --terms``		*<Required>* The list of words for which to calculate the correlation.
	- ``-f --files``		*<Required>* The input corpora from which to calculate the correlation betwee terms, expected to be already tokenized by the `tokenize` tool.
	- ``-m --method``		*<Required>* The method to use to compute the correlation values; supported: `PMI`, `CHI`.
	- ``-o --output``		*<Required>* The path to the file where to store the correlation values.
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
from ate.bootstrapping.probability import PMIBootstrapper, ChiBootstrapper

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-t --terms``		*<Required>* The list of words for which to calculate the correlation.
		- ``-f --files``		*<Required>* The input corpora from which to calculate the correlation betwee terms, expected to be already tokenized by the `tokenize` tool.
		- ``-m --method``		*<Required>* The method to use to compute the correlation values; supported: `PMI`, `CHI`.
		- ``-o --output``		*<Required>* The path to the file where to store the correlation values.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser = argparse.ArgumentParser(description="Calculate the correlation between the given set of terms.")

	parser.add_argument('-t', '--terms',
						nargs='+', required=True,
						help='<Required> The list of words for which to calculate the correlation.')
	parser.add_argument('-f', '--files',
						nargs='+', required=True,
						help='<Required> The input corpora from which to calculate the correlation betwee terms, expected to be already tokenized by the `tokenize tool.')
	parser.add_argument('-m', '--method',
						type=method, required=True,
						help='<Required> The method to use to compute the correlation values; supported: `PMI`, `CHI`.')
	parser.add_argument('-o', '--output',
						type=str, required=True,
						help='<Required> The path to the file where to store the correlation values.')

	args = parser.parse_args()
	return args

def main():
	"""
	The main program loop.
	"""

	args = setup_args()

	"""
	Get the meta arguments.
	"""
	cmd = tools.meta(args)
	cmd['method'] = str(vars(args)['method'])

	tools.save(args.output, { 'meta': cmd })

def method(method):
	"""
	Convert the given string into a correlation function.
	The accepted methods are:

		#. :func:`~ate.bootstrapping.probability.pmi.PMIBootstrapper`,
		#. :func:`~ate.bootstrapping.probability.chi.ChiBootstrapper`

	:param method: The method string.
	:type method: str

	:return: The function that corresponds to the given method.
	:rtype: function

	:raises argparse.ArgumentTypeError: When the given method string is invalid.
	"""

	methods = {
		'pmi': PMIBootstrapper,
		'chi': ChiBootstrapper,
	}

	if method.lower() in methods:
		return methods[method.lower()]

	raise argparse.ArgumentTypeError(f"Invalid method value: {method}")

if __name__ == "__main__":
	main()
