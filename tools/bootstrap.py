#!/usr/bin/env python3

"""
A tool that receives a seed set of terms and looks for similar terms in the given corpora.

To run the script, use:

.. code-block:: bash

    ./tools/bootstrap.py \\
    -s data/seed.txt \\
    -c data/candidates.txt \\
    -o data/bootstrapped.json \\
    -f data/tokenized_corpus.json

The seed and candidates files can be either text files or the output from the ``terms`` tool.
If a text file is given, this tool expects one word on each line.

Accepted arguments:

    - ``-s --seed``            *<Required>* The path to the file containing seed keywords, expected to contain one keyword on each line. Alternatively, the output from the ``terms`` tool can be provided.
    - ``-f --files``        *<Required>* The input corpora where to look for similar keywords, expected to be already tokenized by the `tokenize` tool.
    - ``-m --method``        *<Required>* The method to use to look for similar keywords; supported: `CHI`, `Log`, `PMI`.
    - ``-o --output``        *<Required>* The path to the file where to store the bootstrapped keywords.
    - ``-c --candidates``    *<Optional>* The path to the file containing candidate keywords, expected to contain one keyword on each line. Alternatively, the output from the ``terms`` tool can be provided. If no candidates are given, all vocabulary keywords are considered candidates.
    - ``-i --iterations``    *<Optional>* The number of iterations to spend bootstrapping; defaults to 1.
    - ``-k --keep``            *<Optional>* The number of keywords to keep after each iteration; defaults to 5.
    - ``--generate``        *<Optional>* The number of candidate keywords to generate if no candidates are provided; defaults to 100.
    - ``--max-seed``        *<Optional>* The number of seed words to use from the given files; defaults to all words.
    - ``--max-candidates``    *<Optional>* The number of candidate words to use from the given files; defaults to all words.
"""

import argparse
import json
import os
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

        - ``-s --seed``            *<Required>* The path to the file containing seed keywords, expected to contain one keyword on each line. Alternatively, the output from the ``terms`` tool can be provided.
        - ``-f --files``        *<Required>* The input corpora where to look for similar keywords, expected to be already tokenized by the `tokenize` tool.
        - ``-m --method``        *<Required>* The method to use to look for similar keywords; supported: `CHI`, `Log`, `PMI`.
        - ``-o --output``        *<Required>* The path to the file where to store the bootstrapped keywords.
        - ``-c --candidates``    *<Optional>* The path to the file containing candidate keywords, expected to contain one keyword on each line. Alternatively, the output from the ``terms`` tool can be provided. If no candidates are given, all vocabulary keywords are considered candidates.
        - ``-i --iterations``    *<Optional>* The number of iterations to spend bootstrapping; defaults to 1.
        - ``-k --keep``            *<Optional>* The number of keywords to keep after each iteration; defaults to 5.
        - ``--generate``        *<Optional>* The number of candidate keywords to generate if no candidates are provided; defaults to 100.
        - ``--max-seed``        *<Optional>* The number of seed words to use from the given files; defaults to all words.
        - ``--max-candidates``    *<Optional>* The number of candidate words to use from the given files; defaults to all words.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Bootstrap a seed set of terms.")

    parser.add_argument('-s', '--seed',
                        required=True,
                        help='<Required> The path to the file containing seed keywords, expected to contain one keyword on each line. Alternatively, the output from the ``terms`` tool can be provided.')
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
                        help='<Required> The path to the file containing candidate keywords, expected to contain one keyword on each line. Alternatively, the output from the ``terms`` tool can be provided. If no candidates are given, all vocabulary keywords are considered candidates.')
    parser.add_argument('-i', '--iterations',
                        type=int, required=False, default=1,
                        help='<Optional> The number of iterations to spend bootstrapping; defaults to 1.')
    parser.add_argument('-k', '--keep',
                        type=int, required=False, default=5,
                        help='<Optional> The number of keywords to keep after each iteration; defaults to 5.')
    parser.add_argument('--generate',
                        type=int, required=False, default=100,
                        help='<Optional> The number of candidate keywords to generate if no candidates are provided; defaults to 100.')
    parser.add_argument('--max-seed',
                        type=int, required=False, default=None,
                        help='<Optional> The number of seed words to use from the given files; defaults to all words.')
    parser.add_argument('--max-candidates',
                        type=int, required=False, default=None,
                        help='<Optional> The number of candidate words to use from the given files; defaults to all words.')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    args = setup_args()

    """
    Get the meta arguments.
    """
    cmd = tools.meta(args)
    cmd['method'] = str(vars(args)['method'])

    """
    Load the seed and candidate keywords.
    """
    seed = load_seed(args.seed, args.max_seed)
    cmd['seed'] = seed

    """
    If no candidates are provided, select them from among the most common candidates in the given corpora.
    """
    candidates = load_candidates(args.candidates, args.max_candidates) if args.candidates else generate_candidates(args.files, generate=args.generate)
    cmd['candidates'] = candidates

    bootstrapped = bootstrap(args.files, seed, args.method,
                             args.iterations, args.keep,
                             candidates=candidates)

    tools.save(args.output, { 'meta': cmd, 'bootstrapped': bootstrapped })

def bootstrap(files, seed, method, iterations, keep, candidates):
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
    :param candidates: The list of candidate keywords. If ``None`` is given, all vocabulary keywords are considered candidates.
    :type candidates: list of str or None

    :return: A list of bootstrapped keywords.
    :rtype: list of str
    """

    bootstrapped = [ ]

    """
    For each iteration:

        1. Select the best candidates so far to bootstrap the next candidates,
        2. Use the new candidates to bootstrap new keywords,
        3. Update the scores.
    """
    candidate_scores = { } # the list of candidates and their best scores yet
    for i in range(iterations):
        """
        Select the next seeds.
        In the first iteration, the original seeds are used.
        In subsequent iterations, the highest scoring candidates are used instead.
        """
        if i == 0:
            next_seed = seed
        else:
            """
            Filter out candidates that have already been reviewed.
            Then, Choose the top seeds to bootstrap with next.
            """
            candidate_scores = filter_candidates(candidate_scores, seed, bootstrapped)
            next_seed = sorted(candidate_scores, key=candidate_scores.get, reverse=True)[:keep]
            bootstrapped.extend(next_seed)

        """
        If there are no promising candidates left, stop looking.
        """
        if not next_seed:
            break

        """
        Bootstrap the next seed keywords and save them as bootstrapped.
        """
        logger.info(f"Bootstrapping with { ', '.join(next_seed) }")
        bootstrapper = method()
        scores = bootstrapper.bootstrap(files, seed=next_seed, candidates=candidates, cache=next_seed)

        """
        Get the scores of the new candidates.
        """
        candidate_scores = update_scores(candidate_scores, scores)

    """
    Add the top candidates to the list of bootstrapped keywords.
    """
    candidate_scores = filter_candidates(candidate_scores, seed, bootstrapped)
    final = sorted(candidate_scores, key=candidate_scores.get, reverse=True)[:keep]
    bootstrapped.extend(final)
    logger.info(f"Bootstrapped { ', '.join(bootstrapped) }")

    return bootstrapped

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

    candidates = dict(candidates) # create a copy of the dictionary
    candidates = { candidate: score for candidate, score in candidates.items()
                                    if candidate not in seed + bootstrapped }
    return candidates

def update_scores(candidates, scores):
    """
    Update the scores of the candidates.
    The maximum score is always retained.

    :param candidates: A dictionary with candidates as keys and their scores as values.
    :type candidates: dict
    :param scores: The new scores as a dictionary.
                   The keys are tuples: the keyword that extracted the candidate, and the candidate itself.
                   Only the candidate is considered.
                   The values are the corresponding values.
    :type scores: dict

    :return: An updated dictionary of candidates with their new scores.
    :rtype: dict
    """

    candidates = dict(candidates)
    for (seed, candidate), score in scores.items():
        """
        If the seed and the candidate are the same, skip it.
        """
        if seed == candidate:
            continue

        if candidate not in candidates:
            candidates[candidate] = score
        else:
            candidates[candidate] = max(candidates.get(candidate), score)

    return candidates

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

if __name__ == "__main__":
    main()
