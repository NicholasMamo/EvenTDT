#!/usr/bin/env python3

"""
A tool to automatically extract participants from the given corpora.
This tool is meant to run on the understanding corpora to extract the event's participants.

To run the script, use:

.. code-block:: bash

    ./tools/apd.py \\
	-f data/understanding.json \\
	-o data/participants.json

Accepted arguments:

	- ``-f --file``		*<Required>* The input corpus from where to extract participants.
	- ``-o --output``	*<Required>* The path to the file where to store the extracted participants.
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

parser = argparse.ArgumentParser(description="Extract terms from domain-specific corpora.")
def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``		*<Required>* The input corpus from where to extract participants.
		- ``-o --output``	*<Required>* The path to the file where to store the extracted participants.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser.add_argument('-f', '--file', nargs=1, required=True,
						help='<Required> The input corpus from where to extract participants.')
	parser.add_argument('-o', '--output',
						type=str, required=True,
						help='<Required> The path to the file where to store the extracted terms.')

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()
	print(args)

	"""
	Get the meta arguments.
	"""
	cmd = tools.meta(args)

	tools.save(args.output, { 'meta': cmd })

if __name__ == "__main__":
	main()
