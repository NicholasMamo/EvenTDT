#!/usr/bin/env python3

"""
A tool that receives a seed set of terms and looks for similar terms in the given corpora.

To run the script, use:

.. code-block:: bash

    ./tools/bootstrap.py \\
    --seed data/seed.txt \\
    --candidates data/candidates.txt \\
    --output data/bootstrapped.json \\
    --files data/tokenized_corpus.json

The seed and candidates files can be either text files or the output from the :class:`~tools.terms` tool.
If a text file is given, this tool expects one word on each line.

The output is a JSON file with the following structure:

The output is a JSON file with the following structure:

.. code-block:: json

    {
        "cmd": {
            "files": [
                "data/tokenized_corpus.json"
            ],
            "method": "<class 'ate.bootstrapping.probability'>",
            "seed": "data/seed.txt",
            "candidates": "data/candidates.txt",
            "output": "data/bootstrapped.json",
            "iterations": 17,
            "keep": null,
            "choose": "<built-in function max>",
            "generate": 100,
            "lambda": 1,
            "max_seed": 30,
            "max_candidates": 200,
            "_date": "2021-04-09T12:12:22.023277",
            "_timestamp": 1609067542.0232878,
            "_cmd": "./tools/terms.py --files data/tokenized_corpus.json --output data/bootstrapped.json --method CHI"
        },
        "pcmd": {
            "files": [
                "data/tokenized_corpus.json"
            ],
            "method": "<class 'ate.bootstrapping.probability'>",
            "seed": [
                "yellow",
                "card",
                "red",
                "goal",
                "gol"
            ],
            "candidates": [
                "foul",
                "var",
                "tackl"
            ],
            "output": "data/bootstrapped.json",
            "iterations": 17,
            "keep": null,
            "choose": "<built-in function max>",
            "generate": 100,
            "lambda": 1,
            "max_seed": 30,
            "max_candidates": 200,
            "_date": "2020-12-27T12:12:22.023302",
            "_timestamp": 1609067542.023305,
            "_cmd": "./tools/terms.py --files data/tokenized_corpus.json --output data/bootstrapped.json --method CHI"
        },
        "bootstrapped": [
            {
             "term": "foul",
             "score": 10.2,
             "rank": 6
            },
            {
             "term": "tackl",
             "score": 9.8,
             "rank": 7
            },
            {
             "term": "var",
             "score": 5.4,
             "rank": 6
            }
        ]
    }

The full list of accepted arguments:

    - ``-s --seed``          *<Required>* The path to the file containing seed keywords, expected to contain one keyword on each line. Alternatively, the output from the :class:`~tools.terms` tool can be provided.
    - ``-f --files``         *<Required>* The input corpora where to look for similar keywords, expected to be already tokenized by the ``tokenize`` tool.
    - ``-m --method``        *<Required>* The method to use to look for similar keywords; supported: ``CHI``, ``Log``, ``PMI``.
    - ``-o --output``        *<Required>* The path to the file where to store the bootstrapped keywords.
    - ``-c --candidates``    *<Optional>* The path to the file containing candidate keywords, expected to contain one keyword on each line. Alternatively, the output from the :class:`~tools.terms` tool can be provided. If no candidates are given, all vocabulary keywords are considered candidates.
    - ``-i --iterations``    *<Optional>* The number of iterations to spend bootstrapping; defaults to 1.
    - ``-k --keep``          *<Optional>* The number of keywords to keep after each iteration; defaults to 5.
    - ``--choose``           *<Optional>* The function to use to choose new seed terms; defaults to choosing candidates that have the highest scores; supported: ``max``, ``mean``, ``median``, ``wmean`` (weighted mean).
    - ``--generate``         *<Optional>* The number of candidate keywords to generate if no candidates are provided; defaults to 100.
    - ``--max-seed``         *<Optional>* The number of seed words to use from the given files; defaults to all words.
    - ``--max-candidates``   *<Optional>* The number of candidate words to use from the given files; defaults to all words.
    - ``--lambda``           *<Optional>* The lambda value used with the ``wmean`` scoring method; defaults to 1.
"""

import argparse
import copy
import json
import math
import os
import statistics
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

import tools
from ate.stat import probability
from ate.bootstrapping.probability import ChiBootstrapper, LogLikelihoodRatioBootstrapper, PMIBootstrapper
from objects.exportable import Exportable
from logger import logger

def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-s --seed``          *<Required>* The path to the file containing seed keywords, expected to contain one keyword on each line. Alternatively, the output from the :class:`~tools.terms` tool can be provided.
        - ``-f --files``         *<Required>* The input corpora where to look for similar keywords, expected to be already tokenized by the ``tokenize`` tool.
        - ``-m --method``        *<Required>* The method to use to look for similar keywords; supported: ``CHI``, ``Log``, ``PMI``.
        - ``-o --output``        *<Required>* The path to the file where to store the bootstrapped keywords.
        - ``-c --candidates``    *<Optional>* The path to the file containing candidate keywords, expected to contain one keyword on each line. Alternatively, the output from the :class:`~tools.terms` tool can be provided. If no candidates are given, all vocabulary keywords are considered candidates.
        - ``-i --iterations``    *<Optional>* The number of iterations to spend bootstrapping; defaults to 1.
        - ``-k --keep``          *<Optional>* The number of keywords to keep after each iteration; defaults to 5.
        - ``--choose``           *<Optional>* The function to use to choose new seed terms; defaults to choosing candidates that have the highest scores; supported: ``max``, ``mean``, ``median``, ``wmean`` (weighted mean).
        - ``--generate``         *<Optional>* The number of candidate keywords to generate if no candidates are provided; defaults to 100.
        - ``--max-seed``         *<Optional>* The number of seed words to use from the given files; defaults to all words.
        - ``--max-candidates``   *<Optional>* The number of candidate words to use from the given files; defaults to all words.
        - ``--lambda``           *<Optional>* The lambda value used with the ``wmean`` scoring method; defaults to 1.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Bootstrap a seed set of terms.")

    parser.add_argument('-s', '--seed',
                        required=True,
                        help='<Required> The path to the file containing seed keywords, expected to contain one keyword on each line. Alternatively, the output from the :class:`~tools.terms` tool can be provided.')
    parser.add_argument('-f', '--files',
                        nargs='+', required=True,
                        help='<Required> The input corpora where to look for similar keywords, expected to be already tokenized by the `tokenize` tool.')
    parser.add_argument('-m', '--method',
                        type=method, required=True,
                        help='<Required> The method to use to look for similar keywords; supported: `CHI`, `Log`, `PMI`.')
    parser.add_argument('-o', '--output',
                        type=str, required=True,
                        help='<Required> The path to the file where to store the bootstrapped keywords.')
    parser.add_argument('-c', '--candidates',
                        required=False, default=None,
                        help='<Required> The path to the file containing candidate keywords, expected to contain one keyword on each line. Alternatively, the output from the :class:`~tools.terms` tool can be provided. If no candidates are given, all vocabulary keywords are considered candidates.')
    parser.add_argument('-i', '--iterations',
                        type=int, required=False, default=1,
                        help='<Optional> The number of iterations to spend bootstrapping; defaults to 1.')
    parser.add_argument('-k', '--keep',
                        type=int, required=False, default=5,
                        help='<Optional> The number of keywords to keep after each iteration; defaults to 5.')
    parser.add_argument('--choose',
                        type=choose, required=False, default=max,
                        help='<Optional> The function to use to choose new seed terms; defaults to choosing candidates that have the highest scores; supported: `max`, `mean`, `median`, `wmean` (weighted mean).')
    parser.add_argument('--generate',
                        type=int, required=False, default=100,
                        help='<Optional> The number of candidate keywords to generate if no candidates are provided; defaults to 100.')
    parser.add_argument('--max-seed',
                        type=int, required=False, default=None,
                        help='<Optional> The number of seed words to use from the given files; defaults to all words.')
    parser.add_argument('--max-candidates',
                        type=int, required=False, default=None,
                        help='<Optional> The number of candidate words to use from the given files; defaults to all words.')
    parser.add_argument('--lambda',
                        type=float, required=False, default=1,
                        help='<Optional> The lambda value used with the wmean scoring method.')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    args = setup_args()
    cmd = tools.meta(args)
    pcmd = tools.meta(args)

    # get the meta arguments and encode the necessary ones
    cmd['method'] = str(vars(args)['method'])
    pcmd['method'] = str(vars(args)['method'])
    cmd['choose'] = str(vars(args)['choose'])
    pcmd['choose'] = str(vars(args)['choose'])

    # load the seed and candidate keywords
    seed = load_seed(args.seed, args.max_seed)
    pcmd['seed'] = seed

    # if no candidates are provided, select them from among the most common candidates in the given corpora
    candidates = load_candidates(args.candidates, args.max_candidates) if args.candidates else generate_candidates(args.files, generate=args.generate)
    pcmd['candidates'] = candidates

    bootstrapped = bootstrap(args.files, seed, args.method,
                             args.iterations, args.keep, args.choose,
                             candidates=candidates, l=vars(args)['lambda'])

    tools.save(args.output, { 'cmd': cmd, 'pcmd': pcmd, 'bootstrapped': bootstrapped })

def isOwn(output):
    """
    Check whether this tool produced the given output.

    :param output: A dictionary containing the output of a tool or a path to it.
    :type output: dict or str

    :return: A boolean indicating whether this tool produced the given output.
    :rtype: bool
    """

    if tools.is_file(output):
        with open(output) as file:
            output = json.loads(''.join(file.readlines()))

    return 'bootstrapped' in output

def load(output, with_seed=True):
    """
    Load the terms from the given file.

    :param output: A dictionary containing this tool's output.
    :type output: dict
    :param with_seed: A boolean indicating whether to load the seed terms along with the bootstrapped terms.
    :type with_seed: bool

    :return: A list of terms.
    :rtype: list of str
    """


    terms = [ ]

    if tools.is_file(output):
        with open(output) as file:
            output = json.loads(''.join(file.readlines()))

    if with_seed:
        meta = output['pcmd'] if 'pcmd' in output else output['meta']
        terms.extend(meta['seed'])

    terms.extend([ term['term'] if type(term) is dict else term
                   for term in output['bootstrapped'] ])

    return terms

def bootstrap(files, seed, method, iterations, keep, choose, candidates, *args, **kwargs):
    """
    Bootstrap the given seed set from the given files.

    :param files: The input corpora where to look for similar keywords.
    :type files: list of str
    :param seed: The seed set of keywords.
    :type seed: list of str
    :param method: The method to use to look for similar keywords.
    :type method: function
    :param iterations: The number of iterations to spend bootstrapping.
    :type iterations: int
    :param keep: The number of keywords to keep after each iteration.
    :type keep: int
    :param choose: The function to use to choose new seed terms.
    :type choose: func
    :param candidates: The list of candidate keywords. If ``None`` is given, all vocabulary keywords are considered candidates.
    :type candidates: list of str or None

    :return: A list of bootstrapped keywords.
             Each keyword includes the term, its score when chosen, and its rank.
             The ranks are offset by the number of seed terms, and therefore do not start from 1.
    :rtype: list of dict
    """

    terms = [ ]

    """
    For each iteration:

        1. Select the best candidates so far to bootstrap the next candidates,
        2. Use the new candidates to bootstrap new keywords,
        3. Update the scores.
    """
    bootstrapped = [ ]
    scores = { } # the list of candidates and scores given by the seed set

    # select the next seeds
    for i in range(iterations):
        # in the first iteration, the original seeds are used
        if i == 0:
            _terms = seed
        else:
            # in subsequent iterations, the highest scoring candidates are used instead
            scores = filter_candidates(scores, seed, bootstrapped) # filter out candidates that have already been reviewed
            next_seed = choose_next(scores, keep, choose, seed + bootstrapped, *args, **kwargs) # choose the next seed terms
            _terms = [ term for term, _ in next_seed ]
            terms.extend([ { 'term': term,
                             'score': score,
                             'rank': len(seed) + len(terms) + r + 1 }
                           for r, (term, score) in enumerate(next_seed) ])
            bootstrapped.extend(_terms)

        # if there are no candidates left, stop looking
        if not _terms:
            break

        # bootstrap the next seed keywords and save them as bootstrapped
        logger.info(f"Bootstrapping with { ', '.join(_terms) }")
        bootstrapper = method()
        _scores = bootstrapper.bootstrap(files, seed=_terms, candidates=candidates, cache=_terms)

        # get the scores of the new candidates
        scores = update_scores(scores, _scores)

    # add the top candidates to the list of bootstrapped keywords
    scores = filter_candidates(scores, seed, bootstrapped)
    next_seed = choose_next(scores, keep, choose, seed + bootstrapped, *args, **kwargs) # choose the final seed terms
    _terms = [ term for term, _ in next_seed ]
    terms.extend([ { 'term': term,
                     'score': score,
                     'rank': len(seed) + len(terms) + r + 1 }
                   for r, (term, score) in enumerate(next_seed) ])
    bootstrapped.extend(_terms)
    logger.info(f"Bootstrapped { ', '.join(bootstrapped) }")

    return terms

def load_seed(seed_file, max_seed=None):
    """
    Load the seed words from the given seed file.
    The function expects a file generated by the :mod:`~tools.terms` tool, or a plain file with one seed word on each line.

    :param seed_file: The path to the seed file.
    :type seed_file: str
    :param max_seed: The number of seed words to retain.
                     If ``None`` is given, the function retains all seed words.
    :type max_seed: None or int

    :return: A list of seed words.
    :rtype: list of str

    :raises ValueError: When zero or fewer seed words should be retained.
    """

    if max_seed is not None and max_seed <= 0:
        raise ValueError(f"At least one seed word must be used; received { max_seed }")

    seed_list = [ ]

    with open(seed_file, 'r') as f:
        if tools.is_json(seed_file):
            seed_list = Exportable.decode(json.loads(f.readline()))['terms']
            seed_list = [ term['term'] for term in seed_list ]
        else:
            seed_list.extend(f.readlines())
            seed_list = [ word.strip() for word in seed_list ]

    max_seed = max_seed or len(seed_list)
    if not seed_list:
        raise ValueError("The seed list cannot be empty if it is given")
    return seed_list[:max_seed]

def load_candidates(candidate_file, max_candidates=None):
    """
    Load the candidate words from the given candidate file.
    The function expects a file generated by the :mod:`~tools.terms` tool, or a plain file with one candidate word on each line.

    :param candidate_file: The path to the candidate file.
    :type candidate_file: str
    :param max_candidates: The number of candidates words to retain.
                           If ``None`` is given, the function retains all candidates words.
    :type max_candidates: None or int

    :return: A list of candidate words.
    :rtype: list of str

    :raises ValueError: When zero or fewer candidate words should be retained.
    :raises ValueError: When no candidate words are found.
    """

    if max_candidates is not None and max_candidates <= 0:
        raise ValueError(f"At least one candidate word must be used when specified; received { max_candidates }")

    candidate_list = [ ]

    with open(candidate_file, 'r') as f:
        if tools.is_json(candidate_file):
            candidate_list = Exportable.decode(json.loads(f.readline()))['terms']
            candidate_list = [ term['term'] for term in candidate_list ]
        else:
            candidate_list.extend(f.readlines())
            candidate_list = [ word.strip() for word in candidate_list ]

    max_candidates = max_candidates or len(candidate_list)
    if not candidate_list:
        raise ValueError("The candidate list cannot be empty if it is given")
    return candidate_list[:max_candidates]

def generate_candidates(files, generate):
    """
    Generate candidates by looking for the most common keywords in the given files.

    :param files: The input corpora where to look for candidate keywords.
    :type files: list of str or str
    :param generate: The maximum number of candidate keywords to generate.
    :type generate: int

    :return: A list of candidate keywords.
    :rtype: list of str
    """

    vocabulary = probability.p(files)
    vocabulary = sorted(vocabulary, key=vocabulary.get, reverse=True)
    return vocabulary[:generate]

def filter_candidates(candidates, seed, bootstrapped):
    """
    Filter out candidates that were in the original seed set or which were bootstrapped.

    :param candidates: A dictionary with candidates as keys and their scores as values.
    :type candidates: dict
    :param seed: The original seed set.
    :type seed: list of str
    :param bootstrapped: Candidates that have already been bootstrapped.
    :type bootstrapped: list of str

    :return: The list of candidates as a dictionary without words that have already been used for bootstrapping.
    :rtype: dict
    """

    candidates = copy.deepcopy(candidates) # create a copy of the dictionary
    candidates = { candidate: score for candidate, score in candidates.items()
                                    if candidate not in seed + bootstrapped }
    return candidates

def choose_next(candidates, keep, choose=max, bootstrapped=None, *args, **kwargs):
    """
    Choose the next set of candidates that will be added to the seed set.

    :param candidates: A list of candidates from where to pick the next set of seed set elements.
                       They should be provided as a dictionary with the keys being the candidates.
                       The corresponding values are their scores.
    :type candidates: dict
    :param keep: The number of candidates to choose.
    :type keep: int
    :param choose: The function to use to map the candidates' scores to a single value.
                   By default, the candidate score that the function considers is the highest one it has.
                   In other words, the function defaults to choosing the candidates with the highest scores.
    :type choose: func
    :param bootstrapped: The list of seed terms and other terms that have already been bootstrapped.
                         The terms should be provided in the same order as they were bootstrapped.
                         This parameter is only used when the choice function is :func:`~tools.bootstrap.wmean`.
    :type bootstrapped: list of str

    :return: A list of candidates, as a tuple, to add to the seed set with their score.
    :rtype: list of tuple of str and float
    """

    _scores = copy.deepcopy(candidates)
    if choose == wmean:
        _scores = { candidate: choose(scores, bootstrapped, *args, **kwargs) for candidate, scores in _scores.items() } # map the scores to a single value
    else:
        _scores = { candidate: choose(scores.values()) for candidate, scores in _scores.items() } # map the scores to a single value
    _scores = sorted(_scores.items(), key=lambda s: s[1], reverse=True) # reverse the candidates in descending order of their scores
    return _scores[:keep]

def wmean(scores, bootstrapped, l=1):
    """
    Calculate the weighted mean for the given candidate by combining its scores with the ranks of already-bootstrapped terms.
    The weight, :math:`w`, is taken from the exponential distribution:

    .. math::

        w = \\lambda e^{-\\lambda x}

    where :math:`\\lambda` is taken to be 1 by default.

    This function is useful to minimize semantic drift.
    The weighted mean favors terms that are closely-correlated with terms that appear high up in the bootstrapped ranking, and also considers the seed set.

    :param scores: The scores of a candidate term with all other bootstrapped terms.
    :type scores: dict
    :param bootstrapped: A list of seed terms and bootstrapped terms, in the original order.
    :type bootstraped: list of str
    :param l: The exponential distribution's rate parameter.
              The higher the value of :math:`\\lambda`, the less semantic drift the function allows.
    :type l: float

    :return: A single score for the given candidate.
    :rtype: float
    """

    rank = { term: r + 1 for r, term in enumerate(bootstrapped) }
    return sum([ score * (l * math.exp(-l * rank[term])) for term, score in scores.items() ])

def update_scores(candidates, scores):
    """
    Update the scores of the candidates.
    The maximum score is always retained.

    :param candidates: A dictionary with candidates as keys and their current scores as values.
                       The keys should be the candidates themselves.
                       The values are again dictionaries, with seed terms as keys and their scores for the candidate as values.
    :type candidates: dict
    :param scores: The new scores as a dictionary.
                   The keys are tuples: the keyword that extracted the candidate, and the candidate itself.
                   The values are the corresponding values.
    :type scores: dict

    :return: An updated dictionary of candidates with their new scores.
    :rtype: dict
    """

    _candidates = copy.deepcopy(candidates)
    for (seed, candidate), score in scores.items():
        # if the seed and the candidate are the same, skip it.
        if seed == candidate:
            continue

        if candidate not in _candidates:
            # create a new dictionary to hold the scores for the candidate if it doesn't have one already
            _candidates[candidate] = { seed: score }
        else:
            # add the seed term's score for the candidate to the candidate's scores
            _candidates[candidate][seed] = score

    return _candidates

def method(method):
    """
    Convert the given string into a bootstrapping function.
    The accepted methods are:

        #. :func:`~ate.bootstrapping.probability.pmi.PMIBootstrapper`,
        #. :func:`~ate.bootstrapping.probability.chi.ChiBootstrapper`

    :param method: The method string.
    :type method: str

    :return: The function that corresponds to the given method.
    :rtype: function

    :raises argparse.ArgumentTypeError: When the given method string is invalid.
    """

    methods = {
        'pmi': PMIBootstrapper,
        'chi': ChiBootstrapper,
        'log': LogLikelihoodRatioBootstrapper,
    }

    if method.lower() in methods:
        return methods[method.lower()]

    raise argparse.ArgumentTypeError(f"Invalid method value: {method}")

def choose(method):
    """
    Convert the given string into a scoring function.
    The accepted methods are:

        #. :func:`max`
        #. :func:`statistics.mean`
        #. :func:`statistics.median`
        #. :func:`~tools.bootstrap.wmean`

    :param method: The method string.
    :type method: str

    :return: The function that corresponds to the given method.
    :rtype: function

    :raises argparse.ArgumentTypeError: When the given method string is invalid.
    """

    methods = {
        'max': max,
        'mean': statistics.mean,
        'median': statistics.median,
        'wmean': wmean
    }

    if method.lower() in methods:
        return methods[method.lower()]

    raise argparse.ArgumentTypeError(f"Invalid method value: {method}")

if __name__ == "__main__":
    main()
