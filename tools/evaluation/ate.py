#!/usr/bin/env python3

"""
A tool to evaluate the ATE algorithms' output as a ranking.

To run the tool, use:

.. code-block:: bash

    ./tools/evaluation/ate.py \\
    --file evaluation/ate/results/terms.json \\
    --gold evaluation/ate/results/gold.txt \\
    --output evaluation/ate/results/results.json \\
    --stem --split --verbose

Accepted arguments:

    - ``-f --file``                  *<Required>* The file containing the terms to evaluate, which may be the output of the :mod:`~tools.terms` or :mod:`~tools.bootstrap` tools.
    - ``-g --gold``                  *<Required>* The file containing the gold standard, with each word on a separate line.
    - ``-o --output``                *<Required>* The file where to save the results.
    - ``--stem``                     *<Optional>* Stem the gold standard terms.
    - ``--split``                    *<Optional>* Split multi-word gold standard terms into unigrams.
    - ``--verbose``                  *<Optional>* Print the results to the shell.

The output is a JSON file with the following structure:

.. code-block:: json

    {
        "meta": {
            "file": "evaluation/ate/results/terms.json",
            "gold": { "offsid": "offside", "keeper": "keeper" },
            "output": "evaluation/ate/results/results.json",
            "terms": [ "offsid", "ff", "keeper", "equalis", "baller" ],
            "stem": true,
            "split": true,
            "verbose": true
        },
        "results": {
            "summary": {
                "precision": 0.5,
                "recall": 0.5,
                "f1": 0.5
            },
            "p@k": {
                "1": 1,
                "2": 0.5,
                "3": 0.33,
                "4": 0.5
                "5": 0.6
            }
            "precise": [ "offsid", "keeper" ],
            "recalled": [ "offside", "keeper" ]
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

from nlp import Tokenizer

def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-f --file``              *<Required>* The file containing the terms to evaluate, which may be the output of the :mod:`~tools.terms` or :mod:`~tools.bootstrap` tools.
        - ``-g --gold``              *<Required>* The file containing the gold standard, with each word on a separate line.
        - ``-o --output``            *<Required>* The file where to save the results.
        - ``--stem``                 *<Optional>* Stem the gold standard terms.
        - ``--split``                *<Optional>* Split multi-word gold standard terms into unigrams.
        - ``--verbose``              *<Optional>* Print the results to the shell.

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
    parser.add_argument('--split', action="store_true",
                        help='<Optional> Split multi-word gold standard terms into unigrams.')
    parser.add_argument('--verbose', action="store_true",
                        help='<Optional> Print the results to the shell.')

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
    terms, gold = load_terms(args.file), load_gold(args.gold, stem=args.stem, split=args.split)
    cmd['terms'], cmd['gold'] = terms, gold

    """
    Get the results.
    """
    precision, recall = evaluation.precision(terms, gold), evaluation.recall(terms, gold)
    f1 = evaluation.f1(precision, recall)
    results = {
        'summary': {
            'precision': precision,
            'recall': recall,
            'f1': f1
        },
        'p@k': evaluation.pk(terms, gold),
        'precise': list(evaluation.precise(terms, gold)),
        'recalled': [ gold[term] for term in evaluation.recalled(terms, gold) ],
    }

    if args.verbose:
        pprint(results)

    """
    Save the results to the output file.
    """
    tools.save(args.output, { 'meta': cmd, 'results': results })

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

def load_gold(file, stem=False, split=False):
    """
    Load the gold standard from the given file.
    The function expects one gold term on each line and returns an inverted index.
    The key is the processed term for easy look-up, and the value is the extracted term.

    :param file: The path to the file containing the gold standard.
    :type file: str
    :param stem: A boolean indicating whether to stem the gold standard terms.
    :type stem: bool
    :param split: A boolean indicating whether to split multi-word gold standard terms.
    :type split: bool

    :return: A dictionary of the gold standard terms.
             The key is the processed term, and the value is the actual, extracted term.
    :rtype: dict
    """

    _terms = { }
    tokenizer = Tokenizer(stem=stem, remove_punctuation=False, min_length=1)

    with open(file) as f:
        _extracted = [ term.strip() for term in f.readlines() ]
        for term in _extracted:
            tokens = tokenizer.tokenize(term)
            if split:
                _terms.update({ processed: term for processed in tokens })
            else:
                processed  = ' '.join(tokens)
                _terms[processed] = term

    return _terms

def pprint(results):
    """
    Pretty-print the given results to the shell.

    :param results: The results to print to the shell.
    :type results: dict
    """

    precision, recall, f1 = results['summary']['precision'], results['summary']['recall'], results['summary']['f1']

    print('Precision        Recall        F1')
    print('---------        ------        --')
    print(f"{ str(round(precision, 4)).ljust(6, '0') }           { str(round(recall, 4)).ljust(6, '0') }        { str(round(f1, 4)).ljust(6, '0') }")
    print()

    print('Precision at k (P@k)')
    print('---------------------------------------------------------------------')
    for k in range(10, min(max(results['p@k']), 200) + 1, 10):
        pk = results['p@k'][k]
        print(f"P@{ str(k).ljust(3, ' ') }    { str(round(pk, 4)).ljust(6, '0') }    { (''.join([ '▅' ] * round(pk * 50))).ljust(50, '░') }")

if __name__ == "__main__":
    main()
