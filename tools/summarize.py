#!/usr/bin/env python3

"""
The summarization tool receives a timeline and creates a summary for each node.
This tool is meant to summarize the ``consume`` tool's output retrospectively, after the clusters have been finalized.
Moreover, the summarization tool makes it easier to experiment with different parameters on the fly.

To run the script, you will need to provide, at least, a timeline, an output directory and the method to use to generate summaries:

.. code-block:: bash

    ./tools/summarize.py \\
    --file data/timeline.json \\
    --method MMR \\
    --output data/summaries.json

You can add provide additional parameters to control how the summaries are generated.
If you pass the ``--verbose`` parameter, the summaries will be printed to console as they are generated.

.. code-block:: bash

    ./tools/summarize.py \\
    --file data/timeline.json \\
    --method MMR \\
    --output data/summaries.json \\
    --length 280 \\
    --with-query

When debugging a feature-pivot TDT approach that extracts keywords and creates :class:`~summarization.timeline.nodes.TopicalClusterNode`, you can use this tool to debug too.
Use the ``--query-only`` parameter with the ``--with-query`` parameter to print the keywords from each node alongside the weights associated with them when summarizing:

.. code-block:: bash

    ./tools/summarize.py \\
    --file data/timeline.json \\
    --method MMR \\
    --output data/summaries.json \\
    --length 280 \\
    --with-query \\
    --query-only

.. warning::

    The ``--length`` parameter sets the maximum length of summaries.
    This limit is specified in terms of characters, not words.
    Summaries can be shorter than this limit, but not longer.
    If the length is too short, the summary may be empty.

The output is a JSON file with the following structure:

.. code-block:: json

    {
        "cmd": {
            "_cmd": "EvenTDT/tools/summarize.py --file data/timeline.json --method MMR --output data/summaries.json",
            "_date": "2020-10-21T15:03:55.863896",
            "_timestamp": 1603285435.8639076,
            "file": "eld/CRYCHE.json",
            "method": "<class 'summarization.algorithms.mmr.MMR'>",
            "output": "summaries/summary.json",
            "verbose": true,
            "documents": null,
            "length": 140,
            "clean": false,
            "lambda": 0.5,
            "with_query": true,
            "query_only": false
        },
        "pcmd": {
            "_cmd": "EvenTDT/tools/summarize.py --file data/timeline.json --method MMR --output data/summaries.json",
            "_date": "2020-10-21T15:03:55.863919",
            "_timestamp": 1603285435.8639216,
            "file": "eld/CRYCHE.json",
            "method": "<class 'summarization.algorithms.mmr.MMR'>",
            "output": "summaries/summary.json",
            "verbose": true,
            "documents": null,
            "length": 140,
            "clean": false,
            "lambda": 0.5,
            "with_query": true,
            "query_only": false
        },
        "summaries": [{
            "class": "<class 'summarization.summary.Summary'>",
            "attributes": [ ],
            "documents": [
                { "class": "<class 'nlp.document.Document'>" }
            ]
        }]
    }

The full list of accepted arguments:

    - ``-f --file``          *<Required>* The path to the file containing the timeline to summarize.
    - ``-m --method``        *<Required>* The method to use to generate summaries; supported: :class:`~summarization.algorithms.dgs.DGS`, :class:`~summarization.algorithms.mmr.MMR`.
    - ``-o --output``        *<Required>* The path to the file where to store the generated summaries.
    - ``-v --verbose``       *<Optional>* Print the summaries as they are generated.
    - ``--documents``        *<Optional>* The maximum number of documents to use when summarizing, with a preference for quality documents, scored by the :class:`~summarization.scorers.tweet_scorer.TweetScorer`; defaults to all documents.
    - ``--length``           *<Optional>* The length of each generated summary (in terms of the number of characters); defaults to 140 characters.
    - ``--clean``            *<Optional>* Clean the documents before summarizing.
    - ``--lambda``           *<Optional>* The lambda parameter to balance between relevance and non-redundancy; used only with the :class:`~summarization.algorithms.mmr.MMR` algorithm; defaults to 0.5.
    - ``--with-query``       *<Optional>* Use the centroid of each timeline node's topics as a query for summarization; used only with the :class:`~summarization.algorithms.mmr.MMR` and :class:`~summarization.algorithms.dgs.DGS` algorithms.
    - ``--query-only``       *<Optional>* Print only the query instead of summarizing; used only with the ``--with-query`` parameter.
"""

import argparse
from datetime import datetime
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

        - ``-f --file``          *<Required>* The path to the file containing the timeline to summarize.
        - ``-m --method``        *<Required>* The method to use to generate summaries; supported: :class:`~summarization.algorithms.dgs.DGS`, :class:`~summarization.algorithms.mmr.MMR`.
        - ``-o --output``        *<Required>* The path to the file where to store the generated summaries.
        - ``-v --verbose``       *<Optional>* Print the summaries as they are generated.
        - ``--documents``        *<Optional>* The maximum number of documents to use when summarizing, with a preference for quality documents, scored by the :class:`~summarization.scorers.tweet_scorer.TweetScorer`; defaults to all documents.
        - ``--length``           *<Optional>* The length of each generated summary (in terms of the number of characters); defaults to 140 characters.
        - ``--clean``            *<Optional>* Clean the documents before summarizing.
        - ``--lambda``           *<Optional>* The lambda parameter to balance between relevance and non-redundancy; used only with the :class:`~summarization.algorithms.mmr.MMR` algorithm; defaults to 0.5.
        - ``--with-query``       *<Optional>* Use the centroid of each timeline node's topics as a query for summarization; used only with the :class:`~summarization.algorithms.dgs.DGS` algorithm.
        - ``--query-only``       *<Optional>* Print only the query instead of summarizing; used only with the ``--with-query`` parameter.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Summarize a timeline.")

    parser.add_argument('-f', '--file', type=str, required=True,
                        help='<Required> The path to the file containing the timeline to summarize.')
    parser.add_argument('-m', '--method', type=method, required=True,
                        help='<Required> The method to use to generate summaries; supported: `DGS`, `MMR`.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The path to the file where to store the generated summaries.')
    parser.add_argument('-v', '--verbose', action='store_true', required=False, default=False,
                        help='<Optional> Print the summaries as they are generated.')
    parser.add_argument('--documents', type=int, required=False, default=None,
                        help='<Optional> The maximum number of documents to use when summarizing, with a preference for quality documents, scored by the tweet scorer; defaults to all documents.')
    parser.add_argument('--length', type=int, required=False, default=140,
                        help='<Optional> The length of each generated summary (in terms of the number of characters); defaults to 140 characters.')
    parser.add_argument('--clean', action='store_true', required=False,
                        help="<Optional> Clean the documents before summarizing.")
    parser.add_argument('--lambda', type=float, metavar='[0-1]', required=False, default=0.5,
                        help='<Optional> The lambda parameter to balance between relevance and non-redundancy; used only with the `MMR` algorithm; defaults to 0.5).')
    parser.add_argument('--with-query', action='store_true', required=False,
                        help="<Optional> Use the centroid of each timeline node's topics as a query for summarization; used only with the `DGS` algorithm).")
    parser.add_argument('--query-only', action='store_true', required=False,
                        help='<Optional> Print only the query instead of summarizing; used only with the ``--with-query`` parameter.')

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
    pcmd = tools.meta(args)
    cmd['method'] = str(vars(args)['method'])
    pcmd['method'] = str(vars(args)['method'])

    """
    Summarize the timeline.
    """
    timeline = load_timeline(args.file)
    summarizer = create_summarizer(args.method, l=vars(args)['lambda'])
    summaries = summarize(summarizer, timeline, verbose=args.verbose,
                          max_documents=args.documents, length=args.length, clean=args.clean,
                          with_query=args.with_query, query_only=args.query_only)

    tools.save(args.output, { 'summaries': summaries, 'cmd': cmd, 'pcmd': pcmd })

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
    :rtype: :class:`~summarization.timeline.
    """

    with open(file) as f:
        data = json.loads(''.join(f.readlines()))
        return Exportable.decode(data)['timeline']

def create_summarizer(method, l=0.5):
    """
    Instantiate the summarization algorithm based on the arguments that it accepts.

    :param method: The class type of the method to instantiate.
    :type method: :class:`~summarization.algorithms.SummarizationAlgorithm`
    :param l: The lambda parameter to balance between relevance and non-redundancy; used only with the :class:`~summarization.algorithms.mmr.MMR` algorithm.
    :type l: float

    :return: The created summarization algorithm.
    :rtype: :class:`~summarization.algorithms.SummarizationAlgorithm`
    """

    if method == MMR:
        return method(l=l)

    return method()

def summarize(summarizer, timeline, verbose=False, max_documents=None, length=140,
              clean=False, with_query=False, query_only=True):
    """
    Summarize the given timeline using the given algorithm.
    This function iterates over all of the timeline's nodes and summarizes them individually.

    :param summarizer: The summarization method to use.
    :type summarizer: :class:`~summarization.algorithms.SummarizationAlgorithm`
    :param timeline: The timeline to summarize.
    :type timeline: :class:`~summarization.timeline`.
    :param verbose: A boolean indicating whether to print the summaries as they are generated.
    :type verbose: bool
    :param max_documents: The maximum number of documents to use when summarizing, with a preference for long documents.
    :type max_documents: int or None
    :param length: The length of each generated summary (in terms of the number of characters); defaults to 140 characters.
    :type length: int
    :param clean: A boolean indicating whether to clean documents before summarizing.
    :type clean: bool
    :param with_query: A boolean indicating whether to use the centroid of each timeline node's topics as a query for summarization.
                       This is used only with the :class:`~summarization.algorithms.dgs.DGS` algorithm.
    :type with_query: bool
    :param query_only: Print only the query instead of summarizing; used only when the ``with_query`` parameters is set to ``True``.
    :type query_only: bool

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
        if with_query and type(node) is TopicalClusterNode:
            query = construct_query(node)

            """
            If only the query is of interest, print only the query terms in descending order of importance.
            """
            if query_only:
                query = sorted(query.dimensions.items(), key=lambda q: q[1], reverse=True)
                logger.info(f"""{ datetime.fromtimestamp(node.created_at).ctime() }: { ', '.join([ f"{ term } ({ round(weight, 2) })" for term, weight in query ]) }""")
                continue

        """
        Generate the sumamry.
        """
        summary = summarizer.summarize(documents, length, query=query)
        if verbose:
            logger.info(f"{ datetime.fromtimestamp(node.created_at).ctime() }: { str(summary) }")
        summaries.append(summary)

    return summaries

def construct_query(node):
    """
    Construct a summarization query from the given node.

    :param node: The node from which to extract the query.
    :type node: :class:`~summarization.timeline.nodes.Node`

    :return: A vector, representing the topical query.
    :rtype: :class:`~vsm.vector.Vector`
    """

    return Cluster(vectors=node.topics).centroid

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
