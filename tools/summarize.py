#!/usr/bin/env python3

"""
The summarization tool receives a timeline and creates a summary for each node.
This tool is meant to summarize the ``consume`` tool's output retrospectively, after all tweets have been assigned to the correct cluster.
Moreover, the summarization tool makes it easier to experiment with different parameters on the fly.

To run the script, use:

.. code-block:: bash

    ./tools/summarize.py \\
	--file data/timeline.json \\
	--method MMR \\
	--output data/summaries.json

Accepted arguments:

	- ``-f --file``			*<Required>* The path to the file containing the timeline to summarize.
	- ``-o --output``		*<Required>* The path to the file where to store the generated summaries.
	- ``-m --method``		*<Required>* The method to use to generate summaries; supported: `DGS`, `MMR`.
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
from objects.exportable import Exportable
from summarization.algorithms import DGS, MMR

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``			*<Required>* The path to the file containing the timeline to summarize.
		- ``-o --output``		*<Required>* The path to the file where to store the generated summaries.
		- ``-m --method``		*<Required>* The method to use to generate summaries; supported: `DGS`, `MMR`.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser = argparse.ArgumentParser(description="Summarize a timeline.")

	parser.add_argument('-f', '--file',
						type=str, required=True,
						help='<Required> The path to the file containing the timeline to summarize.')
	parser.add_argument('-m', '--method',
						type=method, required=True,
						help='<Required> The method to use to generate summaries; supported: `DGS`, `MMR`.')
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
	cmd['method'] = str(vars(args)['method'])

	"""
	Summarize the timeline.
	"""
	timeline = load_timeline(args.file)

	tools.save(args.output, { 'meta': cmd })

def method(method):
	"""
	Convert the given string into a summarization class.
	The accepted classes are:

		#. :class:`~summarization.algorithms.mmr.MMR`
		#. :class:`~summarization.algorithms.dgs.DGS`

	:param method: The method string.
	:type method: str

	:return: The class type that corresponds to the given method.
	:rtype: :class:`~summarization.algorithms.summarization.SummarizationAlgorithm`

	:raises argparse.ArgumentTypeError: When the given method string is invalid.
	"""

	methods = {
		'dgs': DGS,
		'mmr': MMR,
	}

	if method.lower() in methods:
		return methods[method.lower()]

	raise argparse.ArgumentTypeError(f"Invalid method value: { method }")

def load_timeline(file):
	"""
	Load the timeline from the given file.

	:param file: The path to the file where the timeline is saved.
				 This function assumes that the timeline was created using the ``consume`` tool.
	:type file: str

	:return: The loaded timeline.
	:rtype: :class:`~summarization.timeline.Timeline`
	"""

	with open(file) as f:
		data = json.loads(''.join(f.readlines()))['timeline']
		return Exportable.decode(data)

if __name__ == "__main__":
	main()
