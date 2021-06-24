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

By default, the summarization tool uses all documents from each node to construct summaries.
Since this can take a long time and bring down the quality of summaries, you can limit the number of documents to consider by passing the ``--documents`` parameter.
Normally, the summarization tool considers the top quality documents, but if you provide the ``--domain-terms`` parameter, the tool ranks documents using the :class:`~summarization.scorers.domain_scorer.DomainScorer`, preferring on-topic documents.

.. code-block:: bash

    ./tools/summarize.py \\
    --file data/timeline.json \\
    --method MMR \\
    --output data/summaries.json \\
    --length 280 \\
    --documents 200 \\
    --domain-terms data/football.json \\
    --max-domain-terms 50 \\
    --with-query

.. warning::

    The ``--length`` parameter sets the maximum length of summaries.
    This limit is specified in terms of characters, not words.
    Summaries can be shorter than this limit, but not longer.
    If the length is too short, the summary may be empty.

Instead of saving summaries to a JSON file, you can also save them to a CSV file using the ``--format`` parameter:

.. code-block:: bash

    ./tools/summarize.py \\
    --file data/timeline.json \\
    --method MMR \\
    --output data/summaries.csv \\
    --format csv

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
            "meta": null,
            "format": "json",
            "domain_terms": null,
            "max_domain_terms": null,
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
            "meta": null,
            "format": "json",
            "domain_terms": null,
            "max_domain_terms": null,
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
    - ``--meta``             *<Optional>* The file where to save the meta data, defaults to [--file].meta.json (only used if the format is `csv`).
    - ``--format``           *<Optional>* The format of the summaries output file; supported: `json` (default), `csv`.
    - ``--domain-terms``     *<Optional>* The path to a file containing a list of domain terms, expected to contain one keyword on each line. Alternatively, the output from the :class:`~tools.terms` tool can be provided. If given, the loaded terms are used with the :class:`~summarization.scorers.domain_scorer.DomainScorer` to select the top documents.
    - ``--max-domain-terms`` *<Optional>* The number of domain terms to retain; defaults to all terms in the file.
    - ``--documents``        *<Optional>* The maximum number of documents to use when summarizing. If no domain terms are given, preference is given for quality documents, scored by the :class:`~summarization.scorers.tweet_scorer.TweetScorer` or the :class:`~summarization.scorers.domain_scorer.DomainScorer`; defaults to all documents.
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
from summarization.scorers import DomainScorer, TweetScorer
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
        - ``--meta``             *<Optional>* The file where to save the meta data, defaults to [--file].meta.json (only used if the format is `csv`).
        - ``--format``           *<Optional>* The format of the summaries output file; supported: `json` (default), `csv`.
        - ``--domain-terms``     *<Optional>* The path to a file containing a list of domain terms, expected to contain one keyword on each line. Alternatively, the output from the :class:`~tools.terms` tool can be provided. If given, the loaded terms are used with the :class:`~summarization.scorers.domain_scorer.DomainScorer` to select the top documents.
        - ``--max-domain-terms`` *<Optional>* The number of domain terms to retain; defaults to all terms in the file.
        - ``--documents``        *<Optional>* The maximum number of documents to use when summarizing. If no domain terms are given, preference is given for quality documents, scored by the :class:`~summarization.scorers.tweet_scorer.TweetScorer` or the :class:`~summarization.scorers.domain_scorer.DomainScorer`; defaults to all documents.
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
    parser.add_argument('--meta', type=str, required=False,
                        help='<Optional> The file where to save the meta data, defaults to [--file].meta.json (only used if the format is `csv`).')
    parser.add_argument('--format', type=str.lower, required=False, default='json',
                        help='<Optional> The format of the summaries output file; supported: `json` (default), `csv`.')
    parser.add_argument('--domain-terms', type=str, required=False, default=None,
                        help='<Optional> The path to a file containing a list of domain terms, expected to contain one keyword on each line. Alternatively, the output from the `terms` tool can be provided. If given, the loaded terms are used with the Domain Scorer to select the top documents.')
    parser.add_argument('--max-domain-terms', type=int, required=False, default=None,
                        help='<Optional> The number of domain terms to retain; defaults to all terms in the file.')
    parser.add_argument('--documents', type=int, required=False, default=None,
                        help='<Optional> The maximum number of documents to use when summarizing, with a preference for quality documents, scored by the tweet scorer or the domain scorer; defaults to all documents.')
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
    # main program loop

    args = setup_args()

    """
    Get the meta arguments.
    """
    cmd = tools.meta(args)
    pcmd = tools.meta(args)
    cmd['method'] = str(vars(args)['method'])
    pcmd['method'] = str(vars(args)['method'])

    # summarize the timeline
    timeline = load_timeline(args.file)
    streams = load_splits(args.file)
    summarizer = create_summarizer(args.method, l=vars(args)['lambda'])
    terms = load_terms(args.domain_terms, args.max_domain_terms) if args.domain_terms else args.domain_terms
    summaries = summarize(summarizer, timeline, streams, verbose=args.verbose,
                          max_documents=args.documents, length=args.length, clean=args.clean,
                          with_query=args.with_query, query_only=args.query_only,
                          terms=terms)

    # if the file format is CSV, convert summaries to CSV
    if args.format == 'csv':
        headers = [ 'timestamp', 'query', 'summary' ] # the CSV headers
        if streams:
            headers.insert(1, 'split')
        summaries = tabulate(summaries) # tabulate the summaries
        tools.save_csv(args.output, summaries, headers=headers) # save the summaries

        meta = args.meta or args.output.replace('.csv', '.meta.json') # find the meta file path
        pcmd['meta'] = meta # update the processed version
        tools.save(meta, { 'cmd': cmd, 'pcmd': pcmd }) # save the metadata
    else:
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

def load_splits(file):
    """
    Load the splits, or streams from the given file.

    :param file: The path to the file where the timeline is saved.
                 This function assumes that the timeline was created using the ``consume`` tool.
    :type file: str

    :return: A list of splits.
    :rtype: list of list of str
    """

    with open(file) as f:
        data = json.loads(''.join(f.readlines()))
        return data['pcmd']['splits'] if 'pcmd' in data and 'splits' in data['pcmd'] and data['pcmd']['splits'] else [ ]

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

def summarize(summarizer, timeline, splits, verbose=False, max_documents=None, length=140,
              clean=False, with_query=True, query_only=False, terms=None):
    """
    Summarize the given timeline using the given algorithm.
    This function iterates over all of the timeline's nodes and summarizes them individually.

    :param summarizer: The summarization method to use.
    :type summarizer: :class:`~summarization.algorithms.SummarizationAlgorithm`
    :param timeline: The timeline to summarize.
                     In case of a split stream, the timeline could be a list of timelines instead.
    :type timeline: :class:`~summarization.timeline.Timeline` or list of :class:`~summarization.timeline.Timeline`
    :param splits: A list of splits, one for each timeline.
    :type splits: list of list of str
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
    :param terms: A list of domain terms.
                  If given, the function scores documents using the :class:`~summarization.scorers.domain_scorer.DomainScorer` instead of the :class:`~summarization.scorers.tweet_scorer.TweetScorer`.
    :type terms: list of str

    :return: A list of list of summaries, corresponding to each node.
             Each list can have multiple summaries in case of split timelines.
    :rtype: list of list of :class:`~summarization.summary.Summary`
    """

    summaries = [ ]

    cleaner = TweetCleaner(remove_alt_codes=True, complete_sentences=True,
                           collapse_new_lines=True, collapse_whitespaces=True,
                           capitalize_first=True, remove_unicode_entities=False, remove_urls=True,
                           split_hashtags=True, remove_retweet_prefix=True)

    merged = merge(timeline, splits)

    for nodes in merged:
        summaries.append([ ])
        for node in nodes:
            """
            Extract and filter the documents to consider for summarization.
            Cleaning happens before selecting the documents so that the clean text is considered.
            """
            documents = node.get_all_documents()
            if clean:
                for document in documents:
                    document.text = cleaner.clean(document.text)
            documents = filter_documents(documents, max_documents, terms=terms)

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
            summary.attributes['timestamp'] = node.created_at
            if query:
                summary.attributes['query'] = query.dimensions
            if verbose:
                logger.info(f"{ datetime.fromtimestamp(node.created_at).ctime() }: { str(summary) }")
            summaries[-1].append(summary)

    return summaries

def merge(timelines, splits=None):
    """
    Merge the given timelines and extract a list of lists of nodes.

    :param timeline: The timeline to summarize.
                     In case of a split stream, the timeline could be a list of timelines instead.
    :type timeline: :class:`~summarization.timeline.Timeline` or list of :class:`~summarization.timeline.Timeline`
    :param splits: A list of splits, one for each timeline.
                   If `None` is given, it is assumed that only one timeline is given.
    :type splits: list of list of str

    :return: A list of list of nodes.
             Each outer list is made up of an inner list of nodes published at around the same time, as specified by the timeline's expiry.
             The split, if applicable, is saved as an attribute on each node.
    :rtype: list of list of :class:`~summarization.timeline.nodes.Node`
    """

    nodes = [ ]

    if splits:
        # add the stream to each node
        for timeline, split in zip(timelines, splits):
            for node in timeline.nodes:
                node.attributes['split'] = split

        # get a list of nodes sorted in chronological order
        _nodes = [ node for timeline in timelines for node in timeline.nodes ]
        _nodes = sorted(_nodes, key=lambda node: node.created_at)

        expiry = timelines[0].expiry # get the expiry of the first timeline, assuming that all timelines have the same expiry

        # create the merged timeline
        created_at = 0
        for node in _nodes:
            if node.created_at -  created_at >= expiry: # create a new combined node if the current node has expired
                nodes.append([ ])
                created_at = node.created_at
            nodes[-1].append(node)
    else:
        nodes = [ [ node ] for node in timelines.nodes ]

    return nodes

def tabulate(merged):
    """
    Convert the given summaries into a table-like structure to prepare to save them as CSV files.
    This format stores only a basic representation of summaries, including when the summary was originally created, the query and the actual summary.

    :param merged: A list of summaries to tabulate.
    :type merged: list of list of :class:`~summarization.summary.Summary`

    :return: A list of lists, where each outer list is a summary.
             Each summary is made up of a list containing of the summary's details.
    :rtype: list of list
    """

    table = [ ]

    # go through each summary and tabulate it as a row
    for summaries in merged:
        for summary in summaries:
            query = summary.attributes.get('query', { })
            query = sorted(query.items(), key=lambda q: q[1], reverse=True) # sort the query in descending order of weight
            table.append([ summary.attributes['timestamp'], json.dumps(dict(query)), str(summary)])

    return table

def load_terms(term_file, max_terms=None):
    """
    Load the terms from the given term file.
    The function expects a file with one term word on each line.

    :param term_file: The path to the term file.
    :type term_file: str
    :param max_terms: The number of terms to retain.
                      If ``None`` is given, the function retains all terms.
    :type max_terms: None or int

    :return: A list of terms.
    :rtype: list of str

    :raises ValueError: When zero or fewer terms should be retained.
    """

    if max_terms is not None and max_terms <= 0:
        raise ValueError(f"At least one term must be used; received { max_terms }")

    term_list = [ ]

    with open(term_file, 'r') as f:
        if tools.is_json(term_file):
            term_list = Exportable.decode(json.loads(f.readline()))['terms']
            term_list = [ term['term'] for term in term_list ]
        else:
            term_list.extend(f.readlines())
            term_list = [ word.strip() for word in term_list ]

    max_terms = max_terms or len(term_list)
    if not term_list:
        raise ValueError("The term list cannot be empty if it is given")
    return term_list[:max_terms]

def construct_query(node):
    """
    Construct a summarization query from the given node.

    :param node: The node from which to extract the query.
    :type node: :class:`~summarization.timeline.nodes.Node`

    :return: A vector, representing the topical query.
    :rtype: :class:`~vsm.vector.Vector`
    """

    return Cluster(vectors=node.topics).centroid

def filter_documents(documents, max_documents=None, terms=None):
    """
    Filter the given list of documents.
    This function removes duplicates.

    If the maximum number of documents is given, the longest documents are retained.

    :param documents: The list of documents to filter.
    :type documents: list of :class:`~nlp.document.Document`
    :param max_documents: The maximum number of documents to use when summarizing, with a preference for long documents.
                          If ``None`` is given, all documents are used.
    :type max_documents: int or None
    :param terms: A list of domain terms.
                  If given, the function scores documents using the :class:`~summarization.scorers.domain_scorer.DomainScorer` instead of the :class:`~summarization.scorers.tweet_scorer.TweetScorer`.
    :type terms: list of str

    :return: The filtered list of documents without duplicates.
    :rtype documents: list of :class:`~nlp.document.Document`
    """

    # remove duplicates and then load the documents again to ensure that they are in the same order
    filtered = { document.text.lower(): document for document in documents }
    documents = [ document for document in documents
                           if document in filtered.values() ]

    # if the number of documents is given, sort them in ascending order of score and retain only the top ones
    scorers = [ ]
    if terms:
        scorers.append(DomainScorer(terms))
    scorers.append(TweetScorer())

    # pre-process the terms for the tweet scorer if need be
    for document in documents:
        tokens = document.text.split()
        document.attributes['tokens'] = tokens

    if max_documents is not None:
        documents = sorted(documents, key=lambda document: [ scorer.score(document) for scorer in scorers ], reverse=True)

        # post-process the terms for the tweet scorer if need be
        for document in documents:
            del document.attributes['tokens']

        return documents[:max_documents]

    return documents

if __name__ == "__main__":
    main()
