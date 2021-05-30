#!/usr/bin/env python3

"""
A tool to extract lexical concepts from terms.

To extract concepts, specify the output file:

.. code-block:: bash

    ./tools/terms.py \\
    --output data/concepts.json

The output is a JSON file with the following structure:

.. code-block:: json

    {
        "cmd": {
            "output": "data/concepts.json",
            "_date": "2021-05-30T11:32:04.775216",
            "_timestamp": 1622367124.7752266,
            "_cmd": "./tools/concepts.py --output data/concepts.json"
        },
        "pcmd": {
            "output": "data/concepts.json",
            "_date": "2021-05-30T11:32:04.775232",
            "_timestamp": 1622367124.775234,
            "_cmd": "./tools/concepts.py --output data/concepts.json"
        }
    }


The full list of accepted arguments:

    - ``-o --output``           *<Required>* The path to the file where to store the extracted terms.
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
from logger import logger

parser = argparse.ArgumentParser(description="Extract terms from domain-specific corpora.")
def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-o --output``           *<Required>* The path to the file where to store the extracted concepts.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The path to the file where to store the extracted concepts.')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    args = setup_args()

    # get the meta arguments
    cmd, pcmd = tools.meta(args), tools.meta(args)

    # save the meta data and concepts to file
    tools.save(args.output, { 'cmd': cmd, 'pcmd': pcmd })

if __name__ == "__main__":
    main()
