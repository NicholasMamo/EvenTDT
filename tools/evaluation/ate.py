#!/usr/bin/env python3

"""
A tool to evaluate the ATE algorithms' output as a ranking.

To run the tool, use:

.. code-block:: bash

    ./tools/evaluation/ate.py \\
    --file evaluation/ate/results/terms.json \\
    --output evaluation/ate/results/results.json

Accepted arguments:

    - ``-f --file``                  *<Required>* The terms output to evaluate, which may be the output of the :mod:`~tools.terms` or :mod:`~tools.bootstrap` tools.
    - ``-o --output``                *<Required>* The file where to save the results.

The output is a JSON file with the following structure:

.. code-block:: json

    {
        "meta": {
            "file": "evaluation/ate/results/terms.json",
            "output": "evaluation/ate/results/results.json"
        }
    }
"""

import argparse
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '../..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

import tools
from tools import evaluation

def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-f --file``              *<Required>* The terms output to evaluate, which may be the output of the :mod:`~tools.terms` or :mod:`~tools.bootstrap` tools.
        - ``-o --output``            *<Required>* The file where to save the results.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Evaluate the quality of an ATE algorithm's ranking.")
    parser.add_argument('-f', '--file', type=str, required=True,
                        help='<Required> The terms output to evaluate, which may be the output of the terms or bootstrap tools.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The file where to save the results.')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    args = setup_args()
    cmd = tools.meta(args)
    tools.save(args.output, { 'meta': cmd })

if __name__ == "__main__":
    main()
