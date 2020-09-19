#!/usr/bin/env python3

"""
A tool to evaluate the ATE algorithms' output as a ranking.

To run the tool, use:

.. code-block:: bash

    ./tools/evaluation/ate.py \\
    --file evaluation/ate/results/terms.json \\
    --gold evaluation/ate/results/gold.txt \\
    --output evaluation/ate/results/results.json \\
    --stem

Accepted arguments:

    - ``-f --file``                  *<Required>* The file containing the terms to evaluate, which may be the output of the :mod:`~tools.terms` or :mod:`~tools.bootstrap` tools.
    - ``-g --gold``                  *<Required>* The file containing the gold standard, with each word on a separate line.
    - ``-o --output``                *<Required>* The file where to save the results.
    - ``--stem``                     *<Optional>* Stem the gold standard terms.

The output is a JSON file with the following structure:

.. code-block:: json

    {
        "meta": {
            "file": "evaluation/ate/results/terms.json",
            "gold": { "offsid": "offsid", "keeper": "keeper" },
            "output": "evaluation/ate/results/results.json",
            "terms": [ "offsid", "ff", "keeper", "equalis", "baller" ],
            "stem": True
        }
    }
"""

import argparse
import json
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

        - ``-f --file``              *<Required>* The file containing the terms to evaluate, which may be the output of the :mod:`~tools.terms` or :mod:`~tools.bootstrap` tools.
        - ``-g --gold``              *<Required>* The file containing the gold standard, with each word on a separate line.
        - ``-o --output``            *<Required>* The file where to save the results.
        - ``--stem``                 *<Optional>* Stem the gold standard terms.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Evaluate the quality of an ATE algorithm's ranking.")
    parser.add_argument('-f', '--file', type=str, required=True,
                        help='<Required> The file containing the terms to evaluate, which may be the output of the terms or bootstrap tools.')
    parser.add_argument('-g', '--gold', type=str, required=True,
                        help='<Required> The file containing the gold standard, with each word on a separate line.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The file where to save the results.')

    parser.add_argument('--stem', action="store_true",
                        help='<Optional> Stem the gold standard terms.')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    """
    Set up the arguments and the data to use.
    """
    args = setup_args()
    cmd = tools.meta(args)
    terms, gold = load_terms(args.file), load_gold(args.gold)
    cmd['terms'], cmd['gold'] = terms, gold

    """
    Save the results to the output file.
    """
    tools.save(args.output, { 'meta': cmd })

def load_terms(file):
    """
    Load the terms from the given file.

    - If the file is the output of the :mod:`~tools.terms` tool, all terms are loaded from it.
    - If the file is the output of the :mod:`~tools.bootstrap` tool, the seed words and the bootstrapped words are loaded from it.

    :param file: The path to the file containing a list of terms.
    :type file: str

    :return: A list of terms.
    :rtype: list of str
    """

    _terms = [ ]

    with open(file) as f:
        data = json.loads(''.join(f.readlines()))

        """
        Check if this is the output of a tool.
        """
        if 'meta' in data:
            meta = data['meta']
            if 'seed' in meta:
                _terms.extend(meta['seed'])
                _terms.extend(data['bootstrapped'])
            elif 'terms' in data:
                _terms.extend([ term['term'] for term in data['terms'] ])

    return _terms

def load_gold(file):
    """
    Load the gold standard from the given file.
    The function expects one gold term on each line.

    :param file: The path to the file containing the gold standard.
    :type file: str

    :return: A dictionary of the gold standard terms.
             The key is the extracted term, and the value is the processed term.
    :rtype: dict
    """

    _terms = { }

    with open(file) as f:
        _terms = { term.strip(): term.strip() for term in f.readlines() }

    return _terms

if __name__ == "__main__":
    main()
