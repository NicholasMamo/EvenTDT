#!/usr/bin/env python3

"""
A tool to extract lexical concepts from terms.

To extract concepts, specify two files: a file containing the correlations between files, generated using the :mod:`~tools.correlation` tool, and the output file:

.. code-block:: bash

    ./tools/terms.py \\
    --correlations data/terms.json \\
    --output data/concepts.json

The output is a JSON file with the following structure:

.. code-block:: json

    {
        "cmd": {
            "correlations": "data/correlations.json",
            "method": "<class 'ate.concepts.gnclustering.GNClustering'>",
            "output": "data/concepts.json",
            "concepts": 10,
            "_date": "2021-05-30T11:32:04.775216",
            "_timestamp": 1622367124.7752266,
            "_cmd": "./tools/concepts.py --correlations data/correlations.json --output data/concepts.json --concepts 10"
        },
        "pcmd": {
            "correlations": "data/correlations.json",
            "method": "<class 'ate.concepts.gnclustering.GNClustering'>",
            "output": "data/concepts.json",
            "concepts": 10,
            "_date": "2021-05-30T11:32:04.775232",
            "_timestamp": 1622367124.775234,
            "_cmd": "./tools/concepts.py --correlations data/correlations.json --output data/concepts.json --concepts 10"
        }
    }


The full list of accepted arguments:

    - ``-c --correlations``     *<Required>* The path to the file containing correlations between terms, generated using the :mod:`~tools.correlation` tool.
    - ``-m --method``           *<Required>* The method to use to extract the lexical concepts; supported: `GNClustering`.
    - ``-o --output``           *<Required>* The path to the file where to store the extracted terms.
    - ``--concepts``            *<Required>* The number of concepts to extract.
"""

import argparse
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

from ate.concepts import GNClustering
import tools
from logger import logger

parser = argparse.ArgumentParser(description="Extract terms from domain-specific corpora.")
def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-c --correlations``     *<Required>* The path to the file containing correlations between terms, generated using the :mod:`~tools.correlation` tool.
        - ``-m --method``           *<Required>* The method to use to extract the lexical concepts; supported: `GNClustering`.
        - ``-o --output``           *<Required>* The path to the file where to store the extracted concepts.
        - ``--concepts``            *<Required>* The number of concepts to extract.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser.add_argument('-c', '--correlations', required=True,
                        help='<Required> The path to the file containing correlations between terms, generated using the ``correlation`` tool.')
    parser.add_argument('-m', '--method', type=method, required=True,
                        help='<Required> The method to use to extract the lexical concepts; supported: `GNClustering`.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The path to the file where to store the extracted concepts.')
    parser.add_argument('--concepts', type=nn, required=True,
                        help='<Optional> The number of concepts to extract.')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    args = setup_args()

    # get the meta arguments
    cmd, pcmd = tools.meta(args), tools.meta(args)
    cmd['method'], pcmd['method'] = str(vars(args)['method']), str(vars(args)['method'])

    # save the meta data and concepts to file
    tools.save(args.output, { 'cmd': cmd, 'pcmd': pcmd })

def method(method):
    """
    Convert the given string into a lexical concept algorithm.
    The accepted methods are:

        #. :func:`~ate.concepts.gnclustering.GNClustering`

    :param method: The method string.
    :type method: str

    :return: The function that corresponds to the given method.
    :rtype: function

    :raises argparse.ArgumentTypeError: When the given method string is invalid.
    """

    methods = {
        'gnclustering': GNClustering,
    }

    if method.lower() in methods:
        return methods[method.lower()]

    raise argparse.ArgumentTypeError(f"Invalid method value: {method}")

def nn(n):
    """
    Validate that the given integer is a natural number, or an integer greater than 0.

    :param n: The number of clusters to extract.
    :type n: str

    :return: The same number as an integer, if it is valid.
    :rtype: int

    :raises argparse.ArgumentTypeError: When the given number is not an integer.
    :raises argparse.ArgumentTypeError: When the given number is not greater than 0.
    """

    try:
        if not float(n).is_integer():
            raise argparse.ArgumentTypeError(f"The number of clusters must be an integer, received {n}")
    except:
        raise argparse.ArgumentTypeError(f"The number of clusters must be an integer, received {n}")

    if int(n) > 0:
        return int(n)
    else:
        raise argparse.ArgumentTypeError(f"The number of clusters must be greater than 0, received {n}")

if __name__ == "__main__":
    main()
