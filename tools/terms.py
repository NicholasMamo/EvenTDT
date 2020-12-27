#!/usr/bin/env python3

"""
A tool to automatically extract terms from the given corpora.

To run the script, use:

.. code-block:: bash

    ./tools/terms.py \\
    --files data/tokenized_corpus.json \\
    --method tfidf \\
    --tfidf data/idf.json \\
    --output results/tfidf.json

The output is a JSON file with the following structure:

.. code-block:: json

    {
        "cmd": {
            "files": [
                "data/tokenized_corpus.json"
            ],
            "method": "<class 'ate.stat.tfidf.TFIDFExtractor'>",
            "output": "results/tfidf.json",
            "reranker": "None",
            "tfidf": "data/idf.json",
            "general": null,
            "cutoff": 1,
            "base": null,
            "reranker_base": 10,
            "reranker_files": null,
            "_date": "2020-12-27T12:12:22.023277",
            "_timestamp": 1609067542.0232878,
            "_cmd": "./tools/terms.py --files data/tokenized_corpus.json --output results/tfidf.json --method TFIDF --tfidf data/idf.json"
        },
        "pcmd": {
            "files": [
                "data/tokenized_corpus.json"
            ],
            "method": "<class 'ate.stat.tfidf.TFIDFExtractor'>",
            "output": "results/tfidf.json",
            "reranker": "None",
            "tfidf": "data/idf.json",
            "general": null,
            "cutoff": 1,
            "base": null,
            "reranker_base": 10,
            "reranker_files": null,
            "_date": "2020-12-27T12:12:22.023302",
            "_timestamp": 1609067542.023305,
            "_cmd": "./tools/terms.py --files data/tokenized_corpus.json --output results/tfidf.json --method TFIDF --tfidf data/idf.json"
        },
        "terms": [
            {
                "term": "goal",
                "score": 273608.3976284864,
                "rank": 1
            },
            {
                "term": "score",
                "score": 163116.23313871748,
                "rank": 2
            },
            {
                "term": "player",
                "score": 158593.67589002327,
                "rank": 3
            }
        ]
    }

The full list of accepted arguments:

    - ``-f --files``         *<Required>* The input corpora from where to extract domain-specific terms.
    - ``-m --method``        *<Required>* The method to use to extract domain-specific terms; supported: :class:`TF <ate.stat.tf.TFExtractor>`, :class:`TFIDF <ate.stat.tfidf.TFIDFExtractor>`, :class:`Rank <ate.stat.corpus.rank.RankExtractor>`, :class:`Specificity <ate.stat.corpus.specificity.SpecificityExtractor>`, :class:`TFDCF <ate.stat.corpus.tfdcf.TFDCFExtractor>`, :class:`EF <ate.application.event.EF>`, :class:`EFIDF <ate.application.event.EFIDF>`.
    - ``-o --output``        *<Required>* The path to the file where to store the extracted terms.
    - ``-r --reranker``      *<Optional>* The method to use to re-rank terms; supported: :class:`~ate.application.event.Entropy`, :class:`~ate.application.event.Variability`; defaults to no re-ranking.
    - ``--tfidf``            *<Optional>* The TF-IDF scheme to use to extract terms (used only with the :class:`~ate.stat.tfidf.TFIDFExtractor` and the :class:`~ate.application.event.EFIDF` methods).
    - ``--general``          *<Optional>* A path or paths to general corpora used for comparison with the domain-specific corpora (used only with the :class:`~ate.stat.corpus.rank.RankExtractor`, :class:`~ate.stat.corpus.specificity.SpecificityExtractor` and :class:`~ate.stat.corpus.tfdcf.TFDCFExtractor` methods).
    - ``--cutoff``           *<Optional>* The minimum term frequency to consider when ranking terms (used only with the :class:`~ate.stat.corpus.rank.RankExtractor` method).
    - ``--base``             *<Optional>* The logarithmic base (used only with the :class:`~ate.application.event.EFIDF` method).
    - ``--reranker-base``    *<Optional>* The logarithmic base (used only with the :class:`~ate.application.event.Variability` and :class:`~ate.application.event.Entropy` re-rankers); defaults to 10.
    - ``--reranker-files``   *<Optional>* The input corpora to use for the re-ranker.
"""

import argparse
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

import tools
from logger import logger
from ate import linguistic
from ate.application import EF, EFIDF, Entropy, Variability
from ate.stat import TFExtractor, TFIDFExtractor
from ate.stat.corpus import RankExtractor, SpecificityExtractor, TFDCFExtractor

parser = argparse.ArgumentParser(description="Extract terms from domain-specific corpora.")
def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-f --files``         *<Required>* The input corpora from where to extract domain-specific terms.
        - ``-m --method``        *<Required>* The method to use to extract domain-specific terms; supported: :class:`TF <ate.stat.tf.TFExtractor>`, :class:`TFIDF <ate.stat.tfidf.TFIDFExtractor>`, :class:`Rank <ate.stat.corpus.rank.RankExtractor>`, :class:`Specificity <ate.stat.corpus.specificity.SpecificityExtractor>`, :class:`TFDCF <ate.stat.corpus.tfdcf.TFDCFExtractor>`, :class:`EF <ate.application.event.EF>`, :class:`EFIDF <ate.application.event.EFIDF>`.
        - ``-o --output``        *<Required>* The path to the file where to store the extracted terms.
        - ``-r --reranker``      *<Optional>* The method to use to re-rank terms; supported: :class:`~ate.application.event.Entropy`, :class:`~ate.application.event.Variability`; defaults to no re-ranking.
        - ``--tfidf``            *<Optional>* The TF-IDF scheme to use to extract terms (used only with the :class:`~ate.stat.tfidf.TFIDFExtractor` and the :class:`~ate.application.event.EFIDF` methods).
        - ``--general``          *<Optional>* A path or paths to general corpora used for comparison with the domain-specific corpora (used only with the :class:`~ate.stat.corpus.rank.RankExtractor`, :class:`~ate.stat.corpus.specificity.SpecificityExtractor` and :class:`~ate.stat.corpus.tfdcf.TFDCFExtractor` methods).
        - ``--cutoff``           *<Optional>* The minimum term frequency to consider when ranking terms (used only with the :class:`~ate.stat.corpus.rank.RankExtractor` method).
        - ``--base``             *<Optional>* The logarithmic base (used only with the :class:`~ate.application.event.EFIDF` method).
        - ``--reranker-base``    *<Optional>* The logarithmic base (used only with the :class:`~ate.application.event.Variability` and :class:`~ate.application.event.Entropy` re-rankers); defaults to 10.
        - ``--reranker-files``   *<Optional>* The input corpora to use for the re-ranker.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser.add_argument('-f', '--files',
                        nargs='+', required=True,
                        help='<Required> The input corpora from where to extract domain-specific terms.')
    parser.add_argument('-m', '--method',
                        type=method, required=True,
                        help='<Required> The method to use to extract domain-specific terms; supported: `TF`, `TFIDF`, `Rank`, `Specificity`, `TFDCF`, `EF`, `EFIDF`.')
    parser.add_argument('-o', '--output',
                        type=str, required=True,
                        help='<Required> The path to the file where to store the extracted terms.')
    parser.add_argument('-r', '--reranker',
                        type=reranker, required=False,
                        help='<Optional> The method to use to re-rank terms; supported: `Entropy`, `Variability`; defaults to no re-ranking.')
    parser.add_argument('--tfidf', required=False,
                        help='<Optional> The TF-IDF scheme to use to extract terms (used only with the `TF-IDF` method).')
    parser.add_argument('--general',
                        nargs='+', required=False,
                        help='<Optional> A path or paths to general corpora used for comparison with the domain-specific corpora (used only with the `Rank`, `Specificity` and `TF-DCF` methods).')
    parser.add_argument('--cutoff',
                        type=int, default=1, required=False,
                        help='<Optional> The minimum term frequency to consider when ranking terms (used only with the `Rank` method).')
    parser.add_argument('--base',
                        type=int, default=None, required=False,
                        help='<Optional> The logarithmic base (used only with the `EF-IDF` method).')
    parser.add_argument('--reranker-base',
                        type=int, default=10, required=False,
                        help='<Optional> The logarithmic base (used only with the `Variability` and `Entropy` re-rankers); defaults to 10.')
    parser.add_argument('--reranker-files',
                        nargs='+', required=False,
                        help='<Optional> The input corpora to use for the re-ranker.')

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
    cmd['method'], pcmd['method'] = str(vars(args)['method']), str(vars(args)['method'])
    cmd['reranker'], pcmd['reranker'] = str(vars(args)['reranker']), str(vars(args)['reranker'])

    """
    Create the extractor and extract the terms.
    """
    args = vars(args)
    extractor = create_extractor(args['method'],
                                 tfidf=args['tfidf'], general=args['general'], cutoff=args['cutoff'],
                                 base=args['base'])
    terms = extract(extractor=extractor, files=args['files'])

    """
    Create the re-ranker if it is given.
    """
    if args['reranker']:
        reranker = create_reranker(args['reranker'], base=args['reranker_base'])
        if not args['reranker_files']:
            parser.error("One or more paths to corpora are required when using a re-ranker (use the ``--reranker-files`` command-line parameter).")
        terms = rerank(reranker, args['reranker_files'], terms)

    tools.save(args['output'], { 'cnd': cmd, 'pcmd': pcmd, 'terms': terms })

def create_extractor(method, tfidf=None, general=None, cutoff=None, base=None):
    """
    Instantiate the method based on the arguments that it accepts.

    :param method: The class type of the method to instantiate.
    :type method: :class:`~ate.extractor.Extractor`
    :param tfidf: The path to a file containing the TF-IDF scheme.
                  It is required with the :func:`~ate.stat.tfidf.TFIDFExtractor` and :class:`~ate.application.event.EFIDF`.
    :type tfidf: None or str
    :param general: A path, or paths, to files containing general corpora.
                    This parameter is required for the :class:`~ate.stat.corpus.tfdcf.TFDCFExtractor`, :class:`~ate.stat.corpus.specificity.SpecificityExtractor` and :class:`~ate.stat.corpus.rank.RankExtractor`.
    :type general: None or str or list of str
    :param cutoff: The cut-off to use with the :class:`~ate.stat.corpus.rank.RankExtractor`.
    :type cutoff: None or int
    :param base: The logarithmic base to use with the :class:`~ate.application.event.EFIDF`.
    :type base: None or float

    :return: The created extractor.
    :rtype: :class:`~ate.extractor.Extractor`
    """

    if method == TFIDFExtractor:
        if tfidf is None:
            parser.error("The TF-IDF scheme is required with the TF-IDF method.")

        return method(tools.load(tfidf)['tfidf'])
    elif method == TFDCFExtractor:
        if general is None:
            parser.error("One or more paths to general corpora are required with TF-DCF method.")

        return method(general)
    elif method == SpecificityExtractor:
        if general is None:
            parser.error("One or more paths to general corpora are required with domain specificity method.")

        return method(general)
    elif method == RankExtractor:
        if general is None:
            parser.error("One or more paths to general corpora are required with rank difference method.")

        return method(general, cutoff=cutoff)
    elif method == EFIDF:
        if tfidf is None:
            parser.error("The TF-IDF scheme is required with the EF-IDF method.")

        tfidf = tools.load(tfidf)['tfidf']
        base = int(base) if base else base
        return method(tfidf, base=base)

    return method()

def create_reranker(method, base=None):
    """
    Instantiate the reranker based on the arguments that it accepts.

    :param method: The class type of the reranker to instantiate.
    :type method: :class:`~ate.extractor.Extractor`
    :param base: The logarithmic base to use with the :class:`~ate.application.event.Entropy` or :class:`~ate.application.event.Variability` extractors.
    :type base: None or float

    :return: The created extractor.
    :rtype: :class:`~ate.extractor.Extractor`
    """

    if method == Variability or method == Entropy:
        base = int(base) if base else base
        return method(base=base)

    return method()

def extract(extractor, files):
    """
    Extract terms using the given extractor from the given files.

    :param extractor: The extractor to use to extract terms.
    :type extractor: :class:`~ate.extractor.Extractor`
    :param files: The input corpora from where to extract domain-specific terms.
    :type files: str or list of str

    :return: A list of terms, each as a dictionary including its:

             - ``term``,
             - ``score``, and
             - ``rank``.
    :rtype: list of dict
    """

    terms = extractor.extract(files)
    terms = sorted(terms.items(), key=lambda term: term[1], reverse=True)
    terms = [ { 'term': term, 'score': score, 'rank': rank + 1 } for rank, (term, score) in enumerate(terms) ]
    return terms

def rerank(reranker, files, terms):
    """
    Re-rank the given terms by using the given re-ranker.
    The re-ranker first scores terms from the given files.
    Then, it multiplies the original scores with the re-ranker's scores.

    :param reranker: The reranker to use to score the terms.
    :type reranker: :class:`~ate.extractor.Extractor`
    :param files: The input corpora from where to extract domain-specific terms.
    :type files: str or list of str
    :param terms: The list of terms to re-rank.
                  This list must be a list of dictionaries extracted by the :func:`~tools.terms.extract` function.
    :type terms: list of dict

    :return: A list of terms, each as a dictionary including its:

             - ``term``,
             - ``score``, and
             - ``rank``.
    :rtype: list of dict
    """

    terms = list( dict( term ) for term in terms ) # make a copy
    candidates = [ term['term'] for term in terms ]
    reranked = reranker.extract(files, candidates=candidates)
    terms = [ { 'term': term['term'], 'score': term['score'] * reranked[term['term']] } for term in terms ]
    terms = sorted(terms, key=lambda term: term.get('score'), reverse=True)
    terms = [ { 'term': term['term'], 'score': term['score'], 'rank': rank + 1 } for rank, term in enumerate(terms) ]
    return terms

def method(method):
    """
    Convert the given string into an ATE class.
    The accepted classes are:

        #. :class:`~ate.stat.tfidf.TFExtractor`
        #. :class:`~ate.stat.tfidf.TFIDFExtractor`
        #. :class:`~ate.stat.corpus.rank.RankExtractor`
        #. :class:`~ate.stat.corpus.specificity.SpecificityExtractor`
        #. :class:`~ate.stat.corpus.tfdcf.TFDCFExtractor`
        #. :class:`~ate.application.event.EF`
        #. :class:`~ate.application.event.EFIDF`

    :param method: The method string.
    :type method: str

    :return: The class type that corresponds to the given method.
    :rtype: :class:`~ate.extractor.Extractor`

    :raises argparse.ArgumentTypeError: When the given method string is invalid.
    """

    methods = {
        'tf': TFExtractor,
        'tfidf': TFIDFExtractor,
        'rank': RankExtractor,
        'specificity': SpecificityExtractor,
        'tfdcf': TFDCFExtractor,
        'ef': EF,
        'efidf': EFIDF,
    }

    if method.lower() in methods:
        return methods[method.lower()]

    raise argparse.ArgumentTypeError(f"Invalid method value: { method }")

def reranker(method):
    """
    Convert the given string into an ATE class used for re-ranking.
    The accepted classes are:

        #. :class:`~ate.application.event.Variability`
        #. :class:`~ate.application.event.Entropy`

    :param method: The method string.
    :type method: str

    :return: The class type that corresponds to the given method.
    :rtype: :class:`~ate.extractor.Extractor`

    :raises argparse.ArgumentTypeError: When the given method string is invalid.
    """

    methods = {
        'variability': Variability,
        'entropy': Entropy,
    }

    if method.lower() in methods:
        return methods[method.lower()]

    raise argparse.ArgumentTypeError(f"Invalid re-ranker value: { method }")

if __name__ == "__main__":
    main()
