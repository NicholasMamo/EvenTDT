#!/usr/bin/env python3

"""
The consumer receives an input file and consumes it with one of the given consumers.
This consumer is split into two asynchronous tasks.
The first task reads the file, and the second consumes it.

To run the script, use:

.. code-block:: bash

    ./implementation/consume.py

Accepted arguments:

	- ``-f --file``			*<Required>* The file to consume.

"""

import argparse

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``			*<Required>* The file to consume.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Consume a corpus of tweets.")

	"""
	Parameters that define how the corpus should be collected.
	"""

	parser.add_argument('-f', '--file', nargs=1, type=str, required=True,
						help='<Required> The file to consume.')

	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()
	print(args.f)
