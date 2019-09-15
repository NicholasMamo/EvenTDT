#!/usr/bin/env python3

"""
A tool to collect tweets.

The implemented modes of operation are:

- Collect only the understanding period

To run the script, use:

.. code-block:: bash

    ./tools/collect.py \\
		-t "'#ARSWAT' Arsenal Watford"

Accepted arguments:

	- -t --track		A list of tracking keywords.
"""

import argparse
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import conf

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- -t --track		A list of tracking keywords.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Collect a corpus of tweets.")
	parser.add_argument('-t', '--track', nargs='+', type=str, required=True,
						action='append', help='<Required> The initial tracking keywords.')

	args = parser.parse_args()
	return args


def main():
	"""
	Main program loop.
	"""

	args = setup_args()
	print(args)

if __name__ == "__main__":
	main()
