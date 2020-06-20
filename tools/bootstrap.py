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
"""

import argparse

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-s --seed``			*<Required>* The seed set of keywords.
		- ``-f --files``		*<Required>* The input corpora where to look for similar keywords.

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

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()

if __name__ == "__main__":
	main()
