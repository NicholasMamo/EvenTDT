#!/usr/bin/env python3

"""
A tool to evaluate the ATE algorithms' output as a ranking.

To run the tool, use:

.. code-block:: bash

    ./tools/evaluation/ate.py \\
    --file evaluation/ate/results/terms.json \\
    --gold evaluation/ate/results/gold.txt \\
    --output evaluation/ate/results/results.json \\
    --stem --unigrams --verbose

The output is a JSON file with the following structure:

.. code-block:: json

    {
        "cmd": {
            "_cmd": "EvenTDT/tools/evaluation/ate.py  --file evaluation/ate/results/terms.json  --gold evaluation/ate/results/gold.txt  --output evaluation/ate/results/results.json --stem --unigrams --verbose",
            "_date": "2020-10-14T14:08:13.382725",
            "_timestamp": 1602677293.3827367,
            "file": "evaluation/ate/results/terms.json",
            "gold": [ "evaluation/ate/results/gold.txt" ],
            "keep": 5,
            "output": "evaluation/ate/results/results.json",
            "split": false,
            "stem": true,
            "unigrams": true,
            "verbose": true
        },
            "pcmd": {
            "_cmd": "EvenTDT/tools/evaluation/ate.py  --file evaluation/ate/results/terms.json  --gold evaluation/ate/results/gold.txt  --output evaluation/ate/results/results.json --stem --unigrams --verbose",
            "_date": "2020-10-14T14:08:13.382725",
            "_timestamp": 1602677293.3827367,
            "file": "evaluation/ate/results/terms.json",
            "gold": { "offsid": "offside", "keeper": "keeper" },
            "keep": 5,
            "output": "evaluation/ate/results/results.json",
            "terms": [ "offsid", "ff", "keeper", "equalis", "baller" ],
            "split": false,
            "stem": true,
            "unigrams": true,
            "verbose": true
        },
        "results": {
            "summary": {
                "average precision": 0.833333335,
                "precision": 0.5,
                "recall": 0.5,
                "f1": 0.5
            },
            "p@k": {
                "1": 1,
                "2": 0.5,
                "3": 0.33,
                "4": 0.5,
                "5": 0.6
            },
            "precise": {
                "offsid": true,
                "ff": false,
                "keeper": true,
                "equalis": false,
                "baller": false
            },
            "recalled": [ "offside", "keeper" ]
        }
    }

The full list of accepted arguments:

    - ``-f --file``              *<Required>* The file containing the terms to evaluate, which may be the output of the :mod:`~tools.terms` or :mod:`~tools.bootstrap` tools.
    - ``-g --gold``              *<Required>* The files containing the gold standard, with each word on a separate line.
    - ``-o --output``            *<Required>* The file where to save the results.
    - ``-k --keep``              *<Optional>* The number of words in the ranking to keep (defaults to all terms).
    - ``--stem``                 *<Optional>* Stem the gold standard terms.
    - ``--split``                *<Optional>* Split multi-word gold standard terms into unigrams.
    - ``--unigrams``             *<Optional>* Consider only unigrams from the gold standard.
    - ``--verbose``              *<Optional>* Print the results to the shell.
"""

import argparse
from collections import OrderedDict
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
        - ``-g --gold``              *<Required>* The files containing the gold standard, with each word on a separate line.
        - ``-o --output``            *<Required>* The file where to save the results.
        - ``-k --keep``              *<Optional>* The number of words in the ranking to keep (defaults to all terms).
        - ``--stem``                 *<Optional>* Stem the gold standard terms.
        - ``--split``                *<Optional>* Split multi-word gold standard terms into unigrams.
        - ``--unigrams``             *<Optional>* Consider only unigrams from the gold standard.
        - ``--verbose``              *<Optional>* Print the results to the shell.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Evaluate the quality of an ATE algorithm's ranking.")
    parser.add_argument('-f', '--file', type=str, required=True,
                        help='<Required> The file containing the terms to evaluate, which may be the output of the terms or bootstrap tools.')
    parser.add_argument('-g', '--gold', nargs='+', required=True,
                        help='<Required> The file containing the gold standard, with each word on a separate line.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The file where to save the results.')

    parser.add_argument('-k', '--keep', type=int,
                        help='<Optional> The number of words in the ranking to keep (defaults to all terms).')
    parser.add_argument('--stem', action="store_true",
                        help='<Optional> Stem the gold standard terms.')
    parser.add_argument('--split', action="store_true",
                        help='<Optional> Split multi-word gold standard terms into unigrams.')
    parser.add_argument('--unigrams', action="store_true",
                        help='<Optional> Consider only unigrams from the gold standard.')
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
    pcmd = tools.meta(args)
    terms = load_terms(args.file, args.keep)
    gold = load_gold(args.gold, stem=args.stem, split=args.split, unigrams=args.unigrams)
    pcmd['keep'] = pcmd['keep'] or len(terms) # the number of items defaults to all
    pcmd['terms'], pcmd['gold'] = terms, gold

    """
    Get the results.
    """
    precision, recall = evaluation.precision(terms, gold), evaluation.recall(terms, gold)
    results = {
        'summary': {
            'average precision': evaluation.average_precision(terms, gold),
            'precision': precision,
            'recall': recall,
            'f1': evaluation.f1(precision, recall)
        },
        'p@k': evaluation.pk(terms, gold),
        'precise': OrderedDict([ (term, evaluation.is_precise(term, gold)) for term in terms ]),
        'recalled': [ gold[term] for term in evaluation.recalled(terms, gold) ],
    }

    if args.verbose:
        pprint(results)

    """
    Save the results to the output file.
    """
    tools.save(args.output, { 'cmd': cmd, 'pcmd': pcmd, 'results': results })

def load_terms(file, keep=None):
    """
    Load the terms from the given file.

    - If the file is the output of the :mod:`~tools.terms` tool, all terms are loaded from it.
    - If the file is the output of the :mod:`~tools.bootstrap` tool, the seed words and the bootstrapped words are loaded from it.

    :param file: The path to the file containing a list of terms.
    :type file: str
    :param keep: The number of items to keep.
                 This function retains the top items in the ranking.
                 If ``None`` is given, it keeps all items.
    :type keep: int or None

    :return: A list of terms.
    :rtype: list of str
    """

    _terms = [ ]

    with open(file) as f:
        data = json.loads(''.join(f.readlines()))

        """
        Check if this is the output of a tool.
        """
        if 'meta' in data or 'cmd' in data:
            meta = data['meta'] if 'meta' in data else data['pcmd']
            if 'seed' in meta:
                _terms.extend(meta['seed'])
                if data['bootstrapped'] and type(data['bootstrapped'][0]) is str:
                    _terms.extend(data['bootstrapped'])
                else:
                    _terms.extend([ term['term'] for term in data['bootstrapped'] ])
            elif 'terms' in data:
                _terms.extend([ term['term'] for term in data['terms'] ])

    return _terms[:(keep or len(_terms))]

def load_gold(files, stem=False, split=False, unigrams=False):
    """
    Load the gold standard from the given file.
    The function expects one gold term on each line and returns an inverted index.
    The key is the processed term for easy look-up, and the value is the extracted term.

    :param files: The path to the files containing the gold standard.
    :type files: list of str
    :param stem: A boolean indicating whether to stem the gold standard terms.
    :type stem: bool
    :param split: A boolean indicating whether to split multi-word gold standard terms.
    :type split: bool
    :param unigrams: A boolean indicating whether to retain only unigrams.
    :type unigrams: bool

    :return: A dictionary of the gold standard terms.
             The key is the processed term, and the value is the actual, extracted term.
    :rtype: dict
    """

    _terms = { }
    tokenizer = Tokenizer(stem=stem, remove_punctuation=False, min_length=1)

    for file in files:
        with open(file) as f:
            _extracted = [ term.strip() for term in f.readlines() ]
            for term in _extracted:
                tokens = tokenizer.tokenize(term)
                if split:
                    _terms.update({ processed: term for processed in tokens })
                elif unigrams:
                    if len(tokens) == 1:
                        processed = tokens[0]
                        _terms[processed] = term
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

    precision, recall, f1, average_precision = results['summary']['precision'], results['summary']['recall'], results['summary']['f1'], results['summary']['average precision']

    print('Precision        Recall        F1')
    print('---------        ------        --')
    print(f"""{ str(round(precision, 4)).ljust(6, '0') }           { str(round(recall, 4)).ljust(6, '0') }        { str(round(f1, 4)).ljust(6, '0') }""")
    print()
    print('Average Precision')
    print('-----------------')
    print(f"""{ str(round(average_precision, 4)).ljust(6, '0') }""")
    print()

    print('Precision at k (P@k)')
    print('---------------------------------------------------------------------')
    for k in range(10, min(max(results['p@k']), 200) + 1, 10):
        pk = results['p@k'][k]
        print(f"P@{ str(k).ljust(3, ' ') }    { str(round(pk, 4)).ljust(6, '0') }    { (''.join([ '▅' ] * round(pk * 50))).ljust(50, '░') }")

if __name__ == "__main__":
    main()
