#!/usr/bin/env python3

"""
A tool to formally model events extracted by the :mod:`~tools.consume` tool.
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

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Formally model timelines of events.")

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    args = setup_args()

    # get the meta arguments
    cmd, pcmd = tools.meta(args), tools.meta(args)

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

def model(timelines, *args, **kwargs):
	"""
	Formally model the given timelines.

	:param timelines: A timeline, or a list of timelines.
	:type timelines: :class:`~summarization.timeline.Timeline` or list of  :class:`~summarization.timeline.Timeline`
	
	:return: A list of event models, one for each timeline.
    :rtype: list of :class:`~modeling.EventModel`
	"""

	return [ ]

if __name__ == "__main__":
    main()
