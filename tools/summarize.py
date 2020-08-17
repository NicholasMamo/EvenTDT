#!/usr/bin/env python3

"""
The summarization tool receives a timeline and creates a summary for each node.
This tool is meant to summarize the ``consume`` tool's output retrospectively, after all tweets have been assigned to the correct cluster.
Moreover, the summarization tool makes it easier to experiment with different parameters on the fly.

To run the script, use:

.. code-block:: bash

    ./tools/summarize.py \\
	--file data/timeline.json \\
	--method MMR \\
	--output data/summaries.json \\
	--documents 50 \\
	--length 280 \\
	--clean \\
	--with-query

Accepted arguments:

	- ``-f --file``			*<Required>* The path to the file containing the timeline to summarize.
	- ``-m --method``		*<Required>* The method to use to generate summaries; supported: `DGS`, `MMR`.
	- ``-o --output``		*<Required>* The path to the file where to store the generated summaries.
	- ``-v --verbose``		*<Optional>* Print the summaries as they are generated.
	- ``--documents``		*<Optional>* The maximum number of documents to use when summarizing, with a preference for quality documents, scored by the :class:`~summarization.scorers.tweet_scorer.TweetScorer`; defaults to all documents.
	- ``--length``			*<Optional>* The length of each generated summary (in terms of the number of characters); defaults to 140 characters.
	- ``--clean``			*<Optional>* Clean the documents before summarizing.
	- ``--lambda``			*<Optional>* The lambda parameter to balance between relevance and non-redundancy (used only with the :class:`~summarization.algorithms.mmr.MMR` algorithm; defaults to 0.5).
	- ``--with-query``		*<Optional>* Use the centroid of each timeline node's topics as a query for summarization (used only with the :class:`~summarization.algorithms.dgs.DGS` algorithm).
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

from logger import logger
from nlp.cleaners import TweetCleaner
from objects.exportable import Exportable
from summarization.algorithms import DGS, MMR
from summarization.scorers import TweetScorer
from summarization.timeline.nodes import TopicalClusterNode
from vsm.clustering import Cluster
import tools

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``			*<Required>* The path to the file containing the timeline to summarize.
		- ``-m --method``		*<Required>* The method to use to generate summaries; supported: `DGS`, `MMR`.
		- ``-o --output``		*<Required>* The path to the file where to store the generated summaries.
		- ``-v --verbose``		*<Optional>* Print the summaries as they are generated.
		- ``--documents``		*<Optional>* The maximum number of documents to use when summarizing, with a preference for quality documents, scored by the :class:`~summarization.scorers.tweet_scorer.TweetScorer`; defaults to all documents.
		- ``--length``			*<Optional>* The length of each generated summary (in terms of the number of characters); defaults to 140 characters.
		- ``--clean``			*<Optional>* Clean the documents before summarizing.
		- ``--lambda``			*<Optional>* The lambda parameter to balance between relevance and non-redundancy (used only with the :class:`~summarization.algorithms.mmr.MMR` algorithm; defaults to 0.5).
		- ``--with-query``		*<Optional>* Use the centroid of each timeline node's topics as a query for summarization (used only with the :class:`~summarization.algorithms.dgs.DGS` algorithm).

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
	"""

	parser = argparse.ArgumentParser(description="Summarize a timeline.")

	parser.add_argument('-f', '--file',
						type=str, required=True,
						help='<Required> The path to the file containing the timeline to summarize.')
	parser.add_argument('-m', '--method',
						type=method, required=True,
						help='<Required> The method to use to generate summaries; supported: `DGS`, `MMR`.')
	parser.add_argument('-o', '--output',
						type=str, required=True,
						help='<Required> The path to the file where to store the generated summaries.')
	parser.add_argument('-v', '--verbose',
						action='store_true', required=False, default=False,
						help='<Optional> Print the summaries as they are generated.')
	parser.add_argument('--documents',
						type=int, required=False, default=None,
						help='<Optional> The maximum number of documents to use when summarizing, with a preference for quality documents, scored by the tweet scorer; defaults to all documents.')
	parser.add_argument('--length',
						type=int, required=False, default=140,
						help='<Optional> The length of each generated summary (in terms of the number of characters); defaults to 140 characters.')
	parser.add_argument('--clean',
						action='store_true', required=False,
						help="<Optional> Clean the documents before summarizing.")
	parser.add_argument('--lambda',
						type=float, metavar='[0-1]', required=False, default=0.5,
						help='<Optional> The lambda parameter to balance between relevance and non-redundancy (used only with the `MMR` algorithm; defaults to 0.5).')
	parser.add_argument('--with-query',
						action='store_true', required=False,
						help="<Optional> Use the centroid of each timeline node's topics as a query for summarization (used only with the `DGS` algorithm).")

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
	Summarize the timeline.
	"""
	timeline = load_timeline(args.file)
	summarizer = create_summarizer(args.method, l=vars(args)['lambda'])
	summaries = summarize(summarizer, timeline, verbose=args.verbose,
						  max_documents=args.documents, length=args.length,
						  with_query=args.with_query, clean=args.clean)

	tools.save(args.output, { 'summaries': summaries, 'meta': cmd })

def method(method):
	"""
	Convert the given string into a summarization class.
	The accepted classes are:

		#. :class:`~summarization.algorithms.mmr.MMR`
		#. :class:`~summarization.algorithms.dgs.DGS`

	:param method: The method string.
	:type method: str

	:return: The class type that corresponds to the given method.
	:rtype: :class:`~summarization.algorithms.SummarizationAlgorithm`

	:raises argparse.ArgumentTypeError: When the given method string is invalid.
	"""

	methods = {
		'dgs': DGS,
		'mmr': MMR,
	}

	if method.lower() in methods:
		return methods[method.lower()]

	raise argparse.ArgumentTypeError(f"Invalid method value: { method }")

def load_timeline(file):
	"""
	Load the timeline from the given file.

	:param file: The path to the file where the timeline is saved.
				 This function assumes that the timeline was created using the ``consume`` tool.
	:type file: str

	:return: The loaded timeline.
	:rtype: :class:`~summarization.timeline.Timeline`
	"""

	with open(file) as f:
		data = json.loads(''.join(f.readlines()))
		return Exportable.decode(data)['timeline']

def create_summarizer(method, l=0.5):
	"""
	Instantiate the summarization algorithm based on the arguments that it accepts.

	:param method: The class type of the method to instantiate.
	:type method: :class:`~summarization.algorithms.SummarizationAlgorithm`
	:param l: The lambda parameter to balance between relevance and non-redundancy (used only with the :class:`~summarization.algorithms.mmr.MMR` algorithm).
	:type l: float

	:return: The created summarization algorithm.
	:rtype: :class:`~summarization.algorithms.SummarizationAlgorithm`
	"""

	if method == MMR:
		return method(l=l)

	return method()

def summarize(summarizer, timeline, verbose=False, max_documents=None, length=140,
			  with_query=False, clean=False):
	"""
	Summarize the given timeline using the given algorithm.
	This function iterates over all of the timeline's nodes and summarizes them individually.

	:param summarizer: The summarization method to use.
	:type summarizer: :class:`~summarization.algorithms.SummarizationAlgorithm`
	:param timeline: The timeline to summarize.
	:type timeline: :class:`~summarization.timeline.Timeline`
	:param verbose: A boolean indicating whether to print the summaries as they are generated.
	:type verbose: bool
	:param max_documents: The maximum number of documents to use when summarizing, with a preference for long documents.
	:type max_documents: int or None
	:param length: The length of each generated summary (in terms of the number of characters); defaults to 140 characters.
	:type length: int
	:param with_query: A boolean indicating whether to use the centroid of each timeline node's topics as a query for summarization.
	 				   This is used only with the :class:`~summarization.algorithms.dgs.DGS` algorithm.
	:type with_query: bool
	:param clean: A boolean indicating whether to clean documents before summarizing.
	:type clean: bool

	:return: A list of summaries, corresponding to each node.
	:rtype: list of :class:`~summarization.summary.Summary`
	"""

	summaries = [ ]

	for node in timeline.nodes:
		"""
		Extract and filter the documents to consider for summarization.
		Cleaning happens before selecting the documents so that the clean text is considered.
		"""
		documents = node.get_all_documents()
		if clean:
			cleaner = TweetCleaner(remove_alt_codes=True, complete_sentences=True,
								   collapse_new_lines=True, collapse_whitespaces=True,
								   capitalize_first=True,
								   remove_unicode_entities=True, remove_urls=True,
								   remove_hashtags=True, remove_retweet_prefix=True)
			for document in documents:
				document.text = cleaner.clean(document.text)
		documents = filter_documents(documents, max_documents)

		"""
		Construct the query if need be.
		Queries can only be used if:

		1. The appropriate flag is given,
		2. The summarizer is :class:`~summarization.algorithms.dgs.DGS`, and
		3. The node is topical (it stores a topic).
		"""
		query = None
		if with_query and type(summarizer) is DGS and type(node) is TopicalClusterNode:
			query = Cluster(vectors=node.topics).centroid

		"""
		Generate the sumamry.
		"""
		summary = summarizer.summarize(documents, length, query=query)
		if verbose:
			logger.info(str(summary))
		summaries.append(summary)

	return summaries

def filter_documents(documents, max_documents=None):
	"""
	Filter the given list of documents.
	This function removes duplicates.

	If the maximum number of documents is given, the longest documents are retained.

	:param documents: The list of documents to filter.
	:type documents: list of :class:`~nlp.document.Document`
	:param max_documents: The maximum number of documents to use when summarizing, with a preference for long documents.
						  If ``None`` is given, all documents are used.
	:type max_documents: int or None

	:return: The filtered list of documents without duplicates.
	:rtype documents: list of :class:`~nlp.document.Document`
	"""

	"""
	Remove duplicates.
	Immediately after, load the documents again to ensure that they are in the same order.
	"""
	filtered = { document.text.lower(): document for document in documents }
	documents = [ document for document in documents
						   if document in filtered.values() ]

	"""
	If the number of documents is given, sort them in ascending order of score and retain only the top ones.
	"""
	scorer = TweetScorer()
	if max_documents is not None:
		for document in documents:
			tokens = document.text.split()
			document.attributes['tokens'] = tokens

		documents = sorted(documents, key=lambda document: scorer.score(document), reverse=True)

		for document in documents:
			del document.attributes['tokens']

		return documents[:max_documents]
	else:
		return documents


if __name__ == "__main__":
	main()
