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

If the terms are stored in a file produced by the ``terms`` or ``bootstrap`` scripts, you can load them as follows:

	./tools/correlation.py \\
	--terms data/terms.json \\
	--files data/tokenized_corpus.json \\
	--method CHI \\
	--output data/correlation.json

Accepted arguments:

	- ``-t --terms``		*<Required>* A list of terms, or the path to the file containing a list of terms for which to calculate the correlation. It can be the output from the ``terms`` and ``bootstrap`` tool.
	- ``-f --files``		*<Required>* The input corpora from which to calculate the correlation betwee terms, expected to be already tokenized by the `tokenize` tool.
	- ``-m --method``		*<Required>* The method to use to compute the correlation values; supported: `PMI`, `CHI`, `Log`.
	- ``-o --output``		*<Required>* The path to the file where to store the correlation values.
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
from ate.bootstrapping.probability import ChiBootstrapper, LogLikelihoodRatioBootstrapper, PMIBootstrapper
from logger import logger

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-t --terms``		*<Required>* A list of terms, or the path to the file containing a list of terms for which to calculate the correlation. It can be the output from the ``terms`` and ``bootstrap`` tool.
		- ``-f --files``		*<Required>* The input corpora from which to calculate the correlation betwee terms, expected to be already tokenized by the `tokenize` tool.
		- ``-m --method``		*<Required>* The method to use to compute the correlation values; supported: `PMI`, `CHI`, `Log`.
		- ``-o --output``		*<Required>* The path to the file where to store the correlation values.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser = argparse.ArgumentParser(description="Calculate the correlation between the given set of terms.")

	parser.add_argument('-t', '--terms',
						nargs='+', required=True,
						help='<Required> A list of terms, or the path to the file containing a list of terms for which to calculate the correlation. It can be the output from the ``terms`` and ``bootstrap`` tool.')
	parser.add_argument('-f', '--files',
						nargs='+', required=True,
						help='<Required> The input corpora from which to calculate the correlation betwee terms, expected to be already tokenized by the `tokenize tool.')
	parser.add_argument('-m', '--method',
						type=method, required=True,
						help='<Required> The method to use to compute the correlation values; supported: `PMI`, `CHI`, `Log`.')
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

	"""
	Load the terms.
	"""
	terms = load_terms(args.terms)
	cmd['terms'] = terms

	"""
	Calculate the correlation.
	"""
	extractor = create_extractor(args.method)
	correlation = extract(extractor, args.files, terms)

	tools.save(args.output, { 'meta': cmd, 'correlation': correlation })

def load_terms(terms):
	"""
	Load the terms from the given list.
	If a list includes files, they are parsed accordingly:

	- If the file is the output of the ``terms`` tool, all terms are loaded from it.
	- If the file is the output of the ``bootstrap`` tool, the seed words and the bootstrapped words are loaded from it.

	:param terms: A list of terms, or the path to the file containing a list of terms for which to calculate the correlation.
				  It can be the output from the ``terms`` and ``bootstrap`` tool.
	:type terms: list of str

	:return: A list of terms.
	:rtype: list of str
	"""

	_terms = [ ]
	
	for term in terms:
		if tools.is_file(term):
			with open(term) as f:
				data = json.loads(''.join(f.readlines()))

				"""
				Check if this is the output of a tool.
				"""
				if 'meta' in data:
					meta = data['meta']
					if 'seed' in meta:
						_terms.extend(meta['seed'])
						_terms.extend(data['bootstrapped'])
					elif 'terms' in data:
						_terms.extend([ term['term'] for term in data['terms'] ])
		else:
			_terms.append(term)

	return _terms

def create_extractor(cls):
	"""
	Instantiate the method based on the arguments that it accepts.

	:param cls: The class type of the method to instantiate.
	:type cls: :class:`~ate.bootstrapping.Bootstrapper`

	:return: The created extractor.
	:rtype: :class:`~ate.bootstrapping.Bootstrapper`
	"""

	return cls()

def extract(extractor, files, terms):
	"""
	Calculate the correlation of the given terms from the given files.

	:param extractor: The created extractor.
	:type extractor: :class:`~ate.bootstrapping.Bootstrapper`
	:param files: A list of paths to files from which to calculate the correlation.
	:type files: list of str
	:param terms: A list of terms for which to compute the correlation.
	:type terms: list of str

	:return: The correlation between all given terms.
			 This is returned as a dictionary of dictionaries.
			 The outer level is each term.
			 The inner level is the outer level term's correlation with the other terms.
	:rtype: dict of dict
	"""

	logger.info(f"Calculating the correlation between { ', '.join(terms) }")

	correlation = extractor.bootstrap(files, terms, terms)
	correlation = { term: { t2: c for (t1, t2), c in correlation.items()
								  if t1 is term }
						  for term in terms }

	logger.info(f"Finished calculating the correlation")
	return correlation

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
		'log': LogLikelihoodRatioBootstrapper,
	}

	if method.lower() in methods:
		return methods[method.lower()]

	raise argparse.ArgumentTypeError(f"Invalid method value: {method}")

if __name__ == "__main__":
	main()
