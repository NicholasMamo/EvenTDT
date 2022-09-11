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
            "merge": false,
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
            "merge": false,
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
    - ``--merge``            *<Optional>* Merge split timelines after combining them, creating one summary from nodes in separate timelines that broke at the same time; defaults to `False` if not given.
    - ``--domain-terms``     *<Optional>* The path to a file containing a list of domain terms, expected to contain one keyword on each line. Alternatively, the output from the :class:`~tools.terms` tool can be provided. If given, the loaded terms are used with the :class:`~summarization.scorers.domain_scorer.DomainScorer` to select the top documents.
    - ``--max-domain-terms`` *<Optional>* The number of domain terms to retain; defaults to all terms in the file.
    - ``--documents``        *<Optional>* The maximum number of documents to use when summarizing. If no domain terms are given, preference is given for quality documents, scored by the :class:`~summarization.scorers.tweet_scorer.TweetScorer` or the :class:`~summarization.scorers.domain_scorer.DomainScorer`; defaults to all documents.
    - ``--length``           *<Optional>* The length of each generated summary (in terms of the number of characters); defaults to 140 characters.
    - ``--clean``            *<Optional>* Clean the documents before summarizing.
    - ``--reporting``        *<Optional>* The reporting level, or the tweets retained by the summarizers algorithms: `ALL` (default), `ORIGINAL` (exclude retweets), `VERIFIED` (tweets by verified users).
    - ``--with-query``       *<Optional>* Use the centroid of each timeline node's topics as a query for summarization; used only with the :class:`~summarization.algorithms.mmr.MMR` and :class:`~summarization.algorithms.dgs.DGS` algorithms.
    - ``--query-only``       *<Optional>* Print only the query instead of summarizing; used only with the ``--with-query`` parameter.
    - ``--lambda``           *<Optional>* The lambda parameter to balance between relevance and non-redundancy; used only with the :class:`~summarization.algorithms.mmr.MMR` algorithm; defaults to 0.5.
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
from queues.consumers.algorithms import ReportingLevel
from summarization.algorithms import DGS, MMR
from summarization.scorers import DomainScorer, TweetScorer
from summarization.timeline.nodes import TopicalClusterNode
import tools
from tools import consume, terms, bootstrap
import twitter
from vsm.clustering import Cluster

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
        - ``--merge``            *<Optional>* Merge split timelines after combining them, creating one summary from nodes in separate timelines that broke at the same time; defaults to `False` if not given.
        - ``--domain-terms``     *<Optional>* The path to a file containing a list of domain terms, expected to contain one keyword on each line. Alternatively, the output from the :class:`~tools.terms` tool can be provided. If given, the loaded terms are used with the :class:`~summarization.scorers.domain_scorer.DomainScorer` to select the top documents.
        - ``--max-domain-terms`` *<Optional>* The number of domain terms to retain; defaults to all terms in the file.
        - ``--documents``        *<Optional>* The maximum number of documents to use when summarizing. If no domain terms are given, preference is given for quality documents, scored by the :class:`~summarization.scorers.tweet_scorer.TweetScorer` or the :class:`~summarization.scorers.domain_scorer.DomainScorer`; defaults to all documents.
        - ``--length``           *<Optional>* The length of each generated summary (in terms of the number of characters); defaults to 140 characters.
        - ``--clean``            *<Optional>* Clean the documents before summarizing.
        - ``--reporting``        *<Optional>* The reporting level, or the tweets retained by the summarizers algorithms: `ALL` (default), `ORIGINAL` (exclude retweets), `VERIFIED` (tweets by verified users).
        - ``--with-query``       *<Optional>* Use the centroid of each timeline node's topics as a query for summarization; used only with the :class:`~summarization.algorithms.dgs.DGS` algorithm.
        - ``--query-only``       *<Optional>* Print only the query instead of summarizing; used only with the ``--with-query`` parameter.
        - ``--lambda``           *<Optional>* The lambda parameter to balance between relevance and non-redundancy; used only with the :class:`~summarization.algorithms.mmr.MMR` algorithm; defaults to 0.5.

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
    parser.add_argument('--merge', action='store_true',
                        help='<Optional> Merge split timelines after combining them, creating one summary from nodes in separate timelines that broke at the same time; defaults to False if not given.')
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
    parser.add_argument('--reporting', type=reporting, required=False, default='ALL',
                        help='<Optional> The reporting level, or the tweets retained by the summarizers algorithms: `ALL` (default), `ORIGINAL` (exclude retweets), `VERIFIED` (tweets by verified users).')
    parser.add_argument('--with-query', action='store_true', required=False,
                        help="<Optional> Use the centroid of each timeline node's topics as a query for summarization; used only with the `DGS` algorithm).")
    parser.add_argument('--query-only', action='store_true', required=False,
                        help='<Optional> Print only the query instead of summarizing; used only with the ``--with-query`` parameter.')
    parser.add_argument('--lambda', type=float, metavar='[0-1]', required=False, default=0.5,
                        help='<Optional> The lambda parameter to balance between relevance and non-redundancy; used only with the `MMR` algorithm; defaults to 0.5).')
    
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
    cmd['method'], pcmd['method'] = str(vars(args)['method']), str(vars(args)['method'])
    cmd['reporting'], pcmd['reporting'] = str(vars(args)['reporting']), str(vars(args)['reporting'])

    # summarize the timeline
    timeline = load_timeline(args.file)
    streams = load_splits(args.file)
    summarizer = create_summarizer(args.method, l=vars(args)['lambda'])
    terms = load_terms(args.domain_terms, args.max_domain_terms) if args.domain_terms else args.domain_terms
    summaries = summarize(summarizer, timeline, streams, merge=args.merge, verbose=args.verbose,
                          max_documents=args.documents, length=args.length, clean=args.clean,
                          with_query=args.with_query, query_only=args.query_only,
                          terms=terms, reporting=args.reporting)

    # if the file format is CSV, convert summaries to CSV
    if args.format == 'csv':
        headers = [ 'timestamp', 'query', 'summary' ] # the CSV headers
        if streams:
            headers.insert(1, 'split')
            headers.insert(0, 'node')
        summaries = tabulate(summaries, headers) # tabulate the summaries
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
    :rtype: :class:`~summarization.timeline.Timeline`
    """

    return consume.load(file)

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

def summarize(summarizer, timeline, splits, merge=False, verbose=False, max_documents=None, length=140,
              clean=False, with_query=True, query_only=False, terms=None, reporting=ReportingLevel.ALL):
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
    :param merge: A boolean indicating whether to merge split timelines, creating one summary for nodes in separate timelines if they occurred close to each other.
    :type merge: bool
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
    :param reporting: The reporting level, whether to use all tweets, original tweets (excluding retweets) or only verified tweets.
    :type reporting: :class:`~queues.consumers.algorithms.ReportingLevel`

    :return: A list of list of summaries, corresponding to each node.
             Each list can have multiple summaries in case of split timelines.
    :rtype: list of list of :class:`~summarization.summary.Summary`
    """

    summaries = [ ]

    cleaner = TweetCleaner(remove_alt_codes=True, complete_sentences=True,
                           collapse_new_lines=True, collapse_whitespaces=True,
                           capitalize_first=True, remove_unicode_entities=False, remove_urls=True,
                           split_hashtags=True, remove_retweet_prefix=True)

    combined = combine(timeline, splits)

    for nodes in combined:
        summaries.append([ ])

        # if the summaries should be merged, create one summary for all nodes in close proximity
        if merge:
            # get all documents in all nodes
            documents = [ document for node in nodes for document in node.get_all_documents() ]
            for document in documents:
                document.text = cleaner.clean(document.text) if clean else document.text
            documents = filter_documents(documents, max_documents, terms=terms, reporting=reporting)

            # create the query by getting the centroid from all nodes
            query = None
            if with_query and all( type(node) is TopicalClusterNode for node in nodes ):
                query = construct_query(nodes)

                # if only the query is of interest, print only the query terms in descending order of importance
                if query_only:
                    query = sorted(query.dimensions.items(), key=lambda q: q[1], reverse=True)
                    logger.info(f"""{ datetime.fromtimestamp(node.created_at).ctime() }: { ', '.join([ f"{ term } ({ round(weight, 2) })" for term, weight in query ]) }""")
                    continue

            # generate the summary
            summary = summarizer.summarize(documents, length, query=query)
            summary.attributes['timestamp'] = nodes[0].created_at
            summary.attributes['node_id'] = [ node.id for node in nodes ]
            if query:
                summary.attributes['query'] = query.dimensions
            if verbose:
                logger.info(f"{ datetime.fromtimestamp(node.created_at).ctime() }: { str(summary) }")
            summaries[-1].append(summary)
        else:
            for node in nodes:
                """
                Extract and filter the documents to consider for summarization.
                Cleaning happens before selecting the documents so that the clean text is considered.
                """
                documents = node.get_all_documents()
                for document in documents:
                    document.text = cleaner.clean(document.text) if clean else document.text
                documents = filter_documents(documents, max_documents, terms=terms, reporting=reporting)

                # create the query from the node's centroid
                query = None
                if with_query and type(node) is TopicalClusterNode:
                    query = construct_query(node)

                    # if only the query is of interest, print only the query terms in descending order of importance
                    if query_only:
                        query = sorted(query.dimensions.items(), key=lambda q: q[1], reverse=True)
                        logger.info(f"""{ datetime.fromtimestamp(node.created_at).ctime() }: { ', '.join([ f"{ term } ({ round(weight, 2) })" for term, weight in query ]) }""")
                        continue

                # generate the summary
                summary = summarizer.summarize(documents, length, query=query)
                summary.attributes['timestamp'] = node.created_at
                summary.attributes['node_id'] = [ node.id ]
                if splits:
                    summary.attributes['split'] = str(node.attributes['split'])
                if query:
                    summary.attributes['query'] = query.dimensions
                if verbose:
                    logger.info(f"{ datetime.fromtimestamp(node.created_at).ctime() }: { str(summary) }", process=summary.attributes.get('split'))
                summaries[-1].append(summary)

    return summaries

def combine(timelines, splits=None):
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

        # create the combined timeline
        created_at = 0
        for node in _nodes:
            if node.created_at -  created_at >= expiry: # create a new combined node if the current node has expired
                nodes.append([ ])
                created_at = node.created_at
            nodes[-1].append(node)
    else:
        nodes = [ [ node ] for node in timelines.nodes ]

    return nodes

def tabulate(combined, headers):
    """
    Convert the given summaries into a table-like structure to prepare to save them as CSV files.
    This format stores only a basic representation of summaries, including when the summary was originally created, the query and the actual summary.

    :param combined: A list of summaries to tabulate.
    :type combined: list of list of :class:`~summarization.summary.Summary`
    :param headers: The ordered headers to tabulate the data.
    :type headers: list of str

    :return: A list of lists, where each outer list is a summary.
             Each summary is made up of a list containing of the summary's details.
    :rtype: list of list
    """

    table = [ ]

    # go through each summary and tabulate it as a row
    for node, summaries in enumerate(combined):
        for summary in summaries:
            table.append({ header: '' for header in headers })
            query = summary.attributes.get('query', { })
            query = sorted(query.items(), key=lambda q: q[1], reverse=True) # sort the query in descending order of weight
            table[-1]['query'] = json.dumps(query)
            table[-1]['timestamp'] = str(summary.attributes['timestamp'])
            table[-1]['summary'] = str(summary)

            # add the splits
            if 'split' in headers:
                table[-1]['split'] = str(summary.attributes.get('split'))

            # add the node number
            if 'node' in headers:
                table[-1]['node'] = node

            # convert into an actual list of strings
            table[-1] = [ table[-1][header] for header in headers ]

    return table

def load_terms(file, max_terms=None):
    """
    Load the terms from the given term file.
    The function expects a file with one term word on each line.

    :param file: The path to the term file.
    :type file: str
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

    if terms.is_own(file):
        term_list = terms.load(file)
    elif bootstrap.is_own(file):
        term_list = bootstrap.load(file)
    else:
        with open(file, 'r') as f:
            term_list.extend(f.readlines())
            term_list = [ word.strip() for word in term_list ]

    max_terms = max_terms or len(term_list)
    if not term_list:
        raise ValueError("The term list cannot be empty if it is given")
    return term_list[:max_terms]

def construct_query(nodes):
    """
    Construct a summarization query from the given nodes.

    :param nodes: The nodes from which to extract the query, or a list of nodes.
    :type nodes: :class:`~summarization.timeline.nodes.Node` or list of :class:`~summarization.timeline.nodes.Node`

    :return: A vector, representing the topical query.
    :rtype: :class:`~vsm.vector.Vector`
    """

    if type(nodes) is list:
        topics = [ topic for node in nodes for topic in node.topics ]
        return Cluster(vectors=topics).centroid
    else:
        return Cluster(vectors=nodes.topics).centroid

def filter_documents(documents, max_documents=None, terms=None, reporting=ReportingLevel.ALL):
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
    :param reporting: The reporting level, whether to use all tweets, original tweets (excluding retweets) or only verified tweets.
    :type reporting: :class:`~queues.consumers.algorithms.ReportingLevel`

    :return: The filtered list of documents without duplicates.
    :rtype documents: list of :class:`~nlp.document.Document`
    """

    # remove duplicates and then load the documents again to ensure that they are in the same order
    filtered = { document.text.lower(): document for document in documents }
    documents = [ document for document in documents
                           if document in filtered.values() ]

    # add attributes to check if the documents are retweets if they are missing
    for document in documents:
        if (document.is_verified is None or document.is_retweet is None) and document.tweet:
            document.attributes['is_verified'] = twitter.is_verified(document.tweet)
            document.attributes['is_retweet'] = twitter.is_retweet(document.tweet)

    # in the 'ORIGINAL' reporting strategy, remove retweets unless all documents are retweets
    if reporting == ReportingLevel.ORIGINAL and any( not document.is_retweet for document in documents ):
        documents = [ document for document in documents if not document.is_retweet ]

    # in the 'VERIFIED' reporting strategy, remove tweets by unverified authors unless all documents are by them
    if reporting == ReportingLevel.VERIFIED and any( document.is_verified for document in documents ):
        documents = [ document for document in documents if document.is_verified ]

    # if the number of documents is given, sort them in ascending order of score and retain only the top ones
    scorers = [ DomainScorer(terms) ] if terms else [ ]
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

def reporting(level):
    """
    Convert the given reporting level to an actual enumerable.

    :param level: The name of the reporting level to use: `ALL`, `ORIGINAL` or `VERIFIED`.
    :type level: str

    :return: A reporting level enumerable.
    :rtype: :class:`~queues.consumers.algorithms.ReportingLevel`
    """

    return {
        'ALL': ReportingLevel.ALL,
        'ORIGINAL': ReportingLevel.ORIGINAL,
        'VERIFIED': ReportingLevel.VERIFIED,
    }[level.upper()]

if __name__ == "__main__":
    main()
