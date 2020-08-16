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
	- ``-m --method``		*<Required>* The method to use to generate summaries; supported: `DGS`, `MMR`.
	- ``-o --output``		*<Required>* The path to the file where to store the generated summaries.
	- ``--lambda``			*<Optional>* The lambda parameter to balance between relevance and non-redundancy (used only with the :class:`~summarization.algorithms.mmr.MMR` algorithm; defaults to 0.5).
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
		- ``-m --method``		*<Required>* The method to use to generate summaries; supported: `DGS`, `MMR`.
		- ``-o --output``		*<Required>* The path to the file where to store the generated summaries.
		- ``--lambda``			*<Optional>* The lambda parameter to balance between relevance and non-redundancy (used only with the :class:`~summarization.algorithms.mmr.MMR` algorithm; defaults to 0.5).

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
	parser.add_argument('--lambda',
						type=float, metavar='[0-1]', required=False, default=0.5,
						help='<Optional> The lambda parameter to balance between relevance and non-redundancy (used only with the `MMR` algorithm; defaults to 0.5).')

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
	summarizer = create_summarizer(args.method, l=vars(args)['lambda'])

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

def create_summarizer(method, l):
	"""
	Instantiate the summarization algorithm based on the arguments that it accepts.

	:param method: The class type of the method to instantiate.
	:type method: :class:`~summarization.algorithms.summarization.SummarizationAlgorithm`
	:param l: The lambda parameter to balance between relevance and non-redundancy (used only with the :class:`~summarization.algorithms.mmr.MMR` algorithm).
	:type l: float

	:return: The created summarization algorithm.
	:rtype: :class:`~summarization.algorithms.summarization.SummarizationAlgorithm`
	"""

	if method == MMR:
		return method(l=l)

	return method()

if __name__ == "__main__":
	main()
