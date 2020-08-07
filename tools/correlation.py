#!/usr/bin/env python3

"""
The correlation tool receives a list of words and a list of files and computes their correlation.

To run the script, use:

.. code-block:: bash

    ./tools/correlation.py \\
	--files data/tokenized_corpus.json \\
	--output data/correlation.json

Accepted arguments:

	- ``-f --files``		*<Required>* The input corpora from which to calculate the correlation betwee terms, expected to be already tokenized by the `tokenize` tool.
	- ``-o --output``		*<Required>* The path to the file where to store the correlation values.
"""

import argparse

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --files``		*<Required>* The input corpora from which to calculate the correlation betwee terms, expected to be already tokenized by the `tokenize` tool.
		- ``-o --output``		*<Required>* The path to the file where to store the correlation values.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser = argparse.ArgumentParser(description="Calculate the correlation between the given set of terms.")

	parser.add_argument('-f', '--files',
						nargs='+', required=True,
						help='<Required> The input corpora from which to calculate the correlation betwee terms, expected to be already tokenized by the `tokenize tool.')
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
	print(args)

if __name__ == "__main__":
	main()
