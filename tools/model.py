#!/usr/bin/env python3

"""
A tool to formally model events extracted by the :mod:`~tools.consume` tool.

To generate the formal event models, provide the input and output files.
The input file should be a timeline or a list of timelines, one for each stream, generated with the :mod:`~tools.consume` tool.
You can also specify a file where to store the metadata:

.. code-block:: bash

	./tools/concepts.py \\
    --file data/timeline.json \\
    --output data/models.json \\
    --meta data/models.meta.json

The output is a JSON file with one event model on each line:

	{
		"who": [ "Verstappen" ],
		"what": [ "won", "race" ],
		"where": [ "Spain" ],
		"when": [ 1658688327 ]
	}

The full list of accepted arguments:

    - ``-f --file``             *<Required>* A timeline file colleced using the :mod:`~tools.consume` tool.
    - ``-o --output``           *<Required>* The file or directory where to save the event models.
    - ``--meta``                *<Optional>* The file where to save the meta data.
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

        - ``-f --file``             *<Required>* A timeline file colleced using the :mod:`~tools.consume` tool.
        - ``-o --output``           *<Required>* The file or directory where to save the event models.
        - ``--meta``                *<Optional>* The file where to save the meta data.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Formally model timelines of events.")

    parser.add_argument('-f', '--file', type=str, required=True,
                        help='<Required> A timeline file colleced using the `consume` tool.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The file or directory where to save the event models.')
    parser.add_argument('--meta', type=str, required=False,
                        help='<Optional> The file where to save the meta data.')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    args = setup_args()

    # get the meta arguments
    cmd, pcmd = tools.meta(args), tools.meta(args)

    if args.meta:
        tools.save(args.meta, { 'cmd': cmd, 'pcmd': pcmd })

    models = model(args.file)
    tools.save(args.output, models) # to create the directory if it doesn't exist

def is_own(output):
    """
    Check whether this tool produced the given output.

    :param output: A dictionary containing the output of a tool or a path to it.
    :type output: dict or str

    :return: A boolean indicating whether this tool produced the given output.
    :rtype: bool
    """

    pass

def load(output):
    """
    Load the event models from the given file.

    :param output: A dictionary containing this tool's output or a path to it.
    :type output: dict or str

    :return: The event models in the given output.
    :rtype: list of :class:`~modeling.EventModel`
    """

    return [ ]

def model(file, *args, **kwargs):
	"""
	Formally model the given timelines.

	:param file: A path to the timeline file, generated using the :mod:`~tools.consume` tool.
	:type file: str
	
	:return: A list of event models, one for each timeline.
    :rtype: list of :class:`~modeling.EventModel`
	"""

	return [ ]

if __name__ == "__main__":
    main()
