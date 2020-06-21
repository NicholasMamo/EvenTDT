#!/usr/bin/env python3

"""
A tool that receives a seed set of terms and looks for similar terms in the given corpora.

To run the script, use:

.. code-block:: bash

    ./tools/bootstrap.py \\
	-s data/seed.txt \\
	-c data/candidates.txt \\
	-f data/tokenized_corpus.json

Accepted arguments:

	- ``-s --seed``			*<Required>* The path to the file containing seed keywords, expected to contain one keyword on each line.
	- ``-f --files``		*<Required>* The input corpora where to look for similar keywords, expected to be already tokenized by the `tokenize` tool.
	- ``-m --method``		*<Required>* The method to use to look for similar keywords; supported: `PMI`, `CHI`.
	- ``-c --candidates``	*<Optional>* The path to the file containing candidate keywords, expected to contain one keyword on each line; if not given, all vocabulary keywords are considered candidates.
	- ``-i --iterations``	*<Optional>* The number of iterations to spend bootstrapping; defaults to 1.
	- ``-k --keep``			*<Optional>* The number of keywords to keep after each iteration; defaults to 5.
	- ``--cutoff``			*<Optional>* The number of keywords to generate if no candidates are provided.
"""

import argparse
import copy
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

from ate.bootstrapping.probability import p, PMI, CHI
from logger import logger

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-s --seed``			*<Required>* The path to the file containing seed keywords, expected to contain one keyword on each line.
		- ``-f --files``		*<Required>* The input corpora where to look for similar keywords, expected to be already tokenized by the `tokenize` tool.
		- ``-m --method``		*<Required>* The method to use to look for similar keywords; supported: `PMI`, `CHI`.
		- ``-c --candidates``	*<Optional>* The path to the file containing candidate keywords, expected to contain one keyword on each line; if not given, all vocabulary keywords are considered candidates.
		- ``-i --iterations``	*<Optional>* The number of iterations to spend bootstrapping; defaults to 1.
		- ``-k --keep``			*<Optional>* The number of keywords to keep after each iteration; defaults to 5.
		- ``--cutoff``			*<Optional>* The number of keywords to generate if no candidates are provided.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser = argparse.ArgumentParser(description="Bootstrap a seed set of terms.")

	parser.add_argument('-s', '--seed',
						required=True,
						help='<Required> The path to the file containing seed keywords, expected to contain one keyword on each line.')
	parser.add_argument('-f', '--files',
						nargs='+', required=True,
						help='<Required> The input corpora where to look for similar keywords, expected to be already tokenized by the `tokenize` tool.')
	parser.add_argument('-m', '--method',
						type=method, required=True,
						help='<Required> The method to use to look for similar keywords; supported: `PMI`, `CHI`.')
	parser.add_argument('-c', '--candidates',
						required=False, default=None,
						help='<Required> The path to the file containing candidate keywords, expected to contain one keyword on each line; if not given, all vocabulary keywords are considered candidates.')
	parser.add_argument('-i', '--iterations',
						type=int, required=False, default=1,
						help='<Optional> The number of iterations to spend bootstrapping; defaults to 1.')
	parser.add_argument('-k', '--keep',
						type=int, required=False, default=5,
						help='<Optional> The number of keywords to keep after each iteration; defaults to 5.')
	parser.add_argument('--cutoff',
						type=int, required=False, default=100,
						help='<Optional> The number of candidate keywords to generate if no candidates are provided; defaults to 100.')

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
	cmd = meta(args)

	"""
	Load the seed and candidate keywords.
	"""
	seed = load_seed(args.seed)
	cmd['seed'] = seed

	"""
	If no candidates are provided, select them from among the most common candidates in the given corpora.
	"""
	candidates = load_candidates(args.candidates) if args.candidates else generate_candidates(args.files, cutoff=args.cutoff)
	cmd['candidates'] = candidates

	bootstrap(args.files, seed, args.method,
			  args.iterations, args.keep,
			  candidates=candidates)

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
	:param candidates: The list of candidate keywords. If `None` is given, all vocabulary keywords are considered candidates.
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
		scores = method(files, next_seed, y=candidates, cache=next_seed)

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

def load_seed(seed_file):
	"""
	Load the seed words from the given seed file.
	The function expects a file with one seed word on each line.

	:param seed_file: The path to the seed file.
	:type seed_file: str

	:return: A list of seed words.
	:rtype: list of str
	"""

	seed_list = [ ]

	with open(seed_file, 'r') as f:
		seed_list.extend(f.readlines())

	seed_list = [ word.strip() for word in seed_list ]
	return seed_list

def load_candidates(candidate_file):
	"""
	Load the candidate words from the given candidate file.
	The function expects a file with one candidate word on each line.

	:param candidate_file: The path to the candidate file.
	:type candidate_file: str

	:return: A list of candidate words.
	:rtype: list of str
	"""

	candidate_list = [ ]

	with open(candidate_file, 'r') as f:
		candidate_list.extend(f.readlines())

	candidate_list = [ word.strip() for word in candidate_list ]
	return candidate_list

def generate_candidates(files, cutoff):
	"""
	Generate candidates by looking for the most common keywords in the given files.

	:param files: The input corpora where to look for candidate keywords.
	:type files: list of str or str
	:param cutoff: The maximum number of candidate keywords to generate.
	:type cutoff: int

	:return: A list of candidate keywords.
	:rtype: list of str
	"""

	vocabulary = p(files)
	vocabulary = sorted(vocabulary, key=vocabulary.get, reverse=True)
	return vocabulary[:cutoff]

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

def meta(args):
	"""
	Get the meta arguments.

	:param args: The command-line arguments.
	:type args: :class:`argparse.Namespace`

	:return: The meta arguments as a dictionary.
	:rtype: dict
	"""

	meta = copy.deepcopy(vars(args))
	meta['method'] = str(meta['method'])
	return meta

def method(method):
	"""
	Convert the given string into a bootstrapping function.
	The accepted methods are:

		#. :func:`~ate.bootstrapping.probability.PMI`,
		#. :func:`~ate.bootstrapping.probability.CHI`

	:param method: The method string.
	:type method: str

	:return: The function that corresponds to the given method.
	:rtype: function

	:raises argparse.ArgumentTypeError: When the given method string is invalid.
	"""

	methods = {
		'pmi': PMI,
		'chi': CHI,
	}

	if method.lower() in methods:
		return methods[method.lower()]

	raise argparse.ArgumentTypeError(f"Invalid method value: {method}")

if __name__ == "__main__":
	main()
