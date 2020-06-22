#!/usr/bin/env python3

"""
A tool to automatically extract terms from the given corpora.

To run the script, use:

.. code-block:: bash

    ./tools/ate.py \\
	-f data/tokenized_corpus.json

Accepted arguments:

	- ``-f --files``		*<Required>* The input corpora from where to extract domain-specific terms.
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

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --files``		*<Required>* The input corpora from where to extract domain-specific terms.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser = argparse.ArgumentParser(description="Extract terms from domain-specific corpora.")
	parser.add_argument('-f', '--files',
						nargs='+', required=True,
						help='<Required> The input corpora from where to extract domain-specific terms.')

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
	print(cmd)

if __name__ == "__main__":
	main()
