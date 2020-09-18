#!/usr/bin/env python3

"""
A tool to evaluate the ATE algorithms' output as a ranking.

To run the tool, use:

.. code-block:: bash

    ./tools/evaluation/ate.py \\
    -- file evaluation/ate/results/terms.json

Accepted arguments:

	- ``-f --file``					*<Required>* The terms output to evaluate, which may be the output of the :mod:`~tools.terms` or :mod:`~tools.bootstrap` tools.
"""

import argparse

def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

    	- ``-f --file``				*<Required>* The terms output to evaluate, which may be the output of the :mod:`~tools.terms` or :mod:`~tools.bootstrap` tools.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Evaluate the quality of an ATE algorithm's ranking.")
    parser.add_argument('-f', '--file', type=str, required=True,
						help='<Required> The file to use to construct the tokenized corpus.')

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
