#!/usr/bin/env python3

"""
The summarization tool receives a timeline and creates a summary for each node.
This tool is meant to summarize the ``consume`` tool's output retrospectively, after all tweets have been assigned to the correct cluster.
Moreover, the summarization tool makes it easier to experiment with different parameters on the fly.

To run the script, use:

.. code-block:: bash

    ./tools/summarize.py \\
	--output data/summaries.json

Accepted arguments:

	- ``-o --output``		*<Required>* The path to the file where to store the generated summaries.
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

		- ``-o --output``		*<Required>* The path to the file where to store the generated summaries.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser = argparse.ArgumentParser(description="Summarize a timeline.")

	parser.add_argument('-o', '--output',
						type=str, required=True,
						help='<Required> The path to the file where to store the generated summaries.')

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

	tools.save(args.output, { 'meta': cmd })

if __name__ == "__main__":
	main()
