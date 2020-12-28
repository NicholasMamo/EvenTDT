#!/usr/bin/env python3

"""
A tool to automatically extract terms from the given corpora.

To extract terms, you need to specify one or more files where to look for them, the method to use to extract terms, and where to save them.
Most commonly, the input files should be tokenized corpora created using the :mod:`~tools.tokenizer` tool.
However, the input can vary.
Some :mod:`~ate.application.event` approaches expect :class:`~summarization.timeline.Timeline` files.

Most ATE methods require or accept additional parameters that control their behavior.
For example, to use the TF-IDF method, you need to specify a TF-IDF term-weighting scheme.

.. code-block:: bash

    ./tools/terms.py \\
    --files data/tokenized_corpus.json \\
    --method tfidf \\
    --tfidf data/idf.json \\
    --output results/tfidf.json

You can create more complex behaviour by using a re-ranker.
Re-rankers compute new scores for the terms extracted by the base ATE method specified using the ``--method`` parameter.

Using re-rankers is completely optional, but if you choose to use on, the process is similar to before.
You need to specify a re-ranker method, as well as any other files it expects, but there is no need to specify an output file.
Re-rankers accept the same parameters as normal methods, but with the ``reranker-`` prefix.

.. code-block:: bash

    ./tools/terms.py \\
    --files data/tokenized_corpus.json \\
    --method tfidf \\
    --tfidf data/idf.json \\
    --reranker EF \\
    --reranker-files data/timeline.json \\
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
            "keep": null,
            "tfidf": "data/idf.json",
            "general": null,
            "cutoff": 1,
            "base": null,
            "idfs": null,
            "reranker": "<class 'ate.application.event.EF'>",
            "reranker-files": [
                "data/timeline.json"
            ],
            "reranker-keep": null,
            "reranker-tfidf": "data/idf.json",
            "reranker-general": null,
            "reranker-cutoff": 1,
            "reranker-base": null,
            "reranker-idfs": null,
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
            "keep": null,
            "tfidf": "data/idf.json",
            "general": null,
            "cutoff": 1,
            "base": null,
            "idfs": null,
            "reranker": "<class 'ate.application.event.EF'>",
            "reranker-files": [
                "data/timeline.json"
            ],
            "reranker-keep": null,
            "reranker-tfidf": "data/idf.json",
            "reranker-general": null,
            "reranker-cutoff": 1,
            "reranker-base": null,
            "reranker-idfs": null,
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

    - ``-f --files``            *<Required>* The input corpora from where to extract domain-specific terms.
    - ``-m --method``           *<Required>* The method to use to extract domain-specific terms; supported: :class:`TF <ate.stat.tf.TFExtractor>`, :class:`TFIDF <ate.stat.tfidf.TFIDFExtractor>`, :class:`Rank <ate.stat.corpus.rank.RankExtractor>`, :class:`Specificity <ate.stat.corpus.specificity.SpecificityExtractor>`, :class:`TFDCF <ate.stat.corpus.tfdcf.TFDCFExtractor>`, :class:`EF <ate.application.event.EF>`, :class:`LogEF <ate.application.event.LogEF>`, :class:`EF-IDF <ate.application.event.EFIDF>`.
    - ``-o --output``           *<Required>* The path to the file where to store the extracted terms.
    - ``--keep``                *<Optional>* The number of terms to return, ordered in descending order of score; defaults to all terms.
    - ``--tfidf``               *<Optional>* The TF-IDF scheme to use to extract terms (used only with the :class:`~ate.stat.tfidf.TFIDFExtractor` and the :class:`~ate.application.event.EFIDF` methods).
    - ``--general``             *<Optional>* A path or paths to general corpora used for comparison with the domain-specific corpora (used only with the :class:`~ate.stat.corpus.rank.RankExtractor`, :class:`~ate.stat.corpus.specificity.SpecificityExtractor` and :class:`~ate.stat.corpus.tfdcf.TFDCFExtractor` methods).
    - ``--cutoff``              *<Optional>* The minimum term frequency to consider when ranking terms (used only with the :class:`~ate.stat.corpus.rank.RankExtractor` method).
    - ``--base``                *<Optional>* The logarithmic base (used only with the :class:`LogEF <ate.application.event.LogEF>`, :class:`~ate.application.event.EFIDF` and :class:`~ate.application.event.EFIDFEntropy` methods).
    - ``--idfs``                *<Optional>* The IDF files to use to calculate entropy (used only with the :class:`~ate.application.event.EFIDFEntropy` method)

When using a re-ranker, these arguments are also accepted:

    - ``--reranker``            *<Optional>* The method to use to re-rank the terms extracted by the base method; supported :class:`TF <ate.stat.tf.TFExtractor>`, :class:`TFIDF <ate.stat.tfidf.TFIDFExtractor>`, :class:`Rank <ate.stat.corpus.rank.RankExtractor>`, :class:`Specificity <ate.stat.corpus.specificity.SpecificityExtractor>`, :class:`TFDCF <ate.stat.corpus.tfdcf.TFDCFExtractor>`, :class:`EF <ate.application.event.EF>`, :class:`LogEF <ate.application.event.LogEF>`, :class:`EF-IDF <ate.application.event.EFIDF>`, :class:`EF-IDF-Entropy <ate.application.event.EFIDFEntropy>`.
    - ``--reranker-files``      *<Optional>* The corpora to use to calculate the new, re-ranked score for terms.
    - ``--reranker-keep``       *<Optional>* The number of terms to return, ordered in descending order of score; defaults to all terms.
    - ``--reranker-tfidf``      *<Optional>* The TF-IDF scheme to use to extract terms (used only with the :class:`~ate.stat.tfidf.TFIDFExtractor` and the :class:`~ate.application.event.EFIDF` methods).
    - ``--reranker-general``    *<Optional>* A path or paths to general corpora used for comparison with the domain-specific corpora (used only with the :class:`~ate.stat.corpus.rank.RankExtractor`, :class:`~ate.stat.corpus.specificity.SpecificityExtractor` and :class:`~ate.stat.corpus.tfdcf.TFDCFExtractor` methods).
    - ``--reranker-cutoff``     *<Optional>* The minimum term frequency to consider when ranking terms (used only with the :class:`~ate.stat.corpus.rank.RankExtractor` method).
    - ``--reranker-base``       *<Optional>* The logarithmic base (used only with the :class:`LogEF <ate.application.event.LogEF>`, :class:`~ate.application.event.EFIDF` and :class:`~ate.application.event.EFIDFEntropy` methods).
    - ``--reranker-idfs``       *<Optional>* The IDF files to use to calculate entropy (used only with the :class:`~ate.application.event.EFIDFEntropy` method)
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
from ate.application import EF, LogEF, EFIDF, EFIDFEntropy
from ate.stat import TFExtractor, TFIDFExtractor
from ate.stat.corpus import RankExtractor, SpecificityExtractor, TFDCFExtractor

parser = argparse.ArgumentParser(description="Extract terms from domain-specific corpora.")
def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-f --files``            *<Required>* The input corpora from where to extract domain-specific terms.
        - ``-m --method``           *<Required>* The method to use to extract domain-specific terms; supported: :class:`TF <ate.stat.tf.TFExtractor>`, :class:`TFIDF <ate.stat.tfidf.TFIDFExtractor>`, :class:`Rank <ate.stat.corpus.rank.RankExtractor>`, :class:`Specificity <ate.stat.corpus.specificity.SpecificityExtractor>`, :class:`TFDCF <ate.stat.corpus.tfdcf.TFDCFExtractor>`, :class:`EF <ate.application.event.EF>`, :class:`LogEF <ate.application.event.LogEF>`, :class:`EF-IDF <ate.application.event.EFIDF>`.
        - ``-o --output``           *<Required>* The path to the file where to store the extracted terms.
        - ``--keep``                *<Optional>* The number of terms to return, ordered in descending order of score; defaults to all terms.
        - ``--tfidf``               *<Optional>* The TF-IDF scheme to use to extract terms (used only with the :class:`~ate.stat.tfidf.TFIDFExtractor` and the :class:`~ate.application.event.EFIDF` methods).
        - ``--general``             *<Optional>* A path or paths to general corpora used for comparison with the domain-specific corpora (used only with the :class:`~ate.stat.corpus.rank.RankExtractor`, :class:`~ate.stat.corpus.specificity.SpecificityExtractor` and :class:`~ate.stat.corpus.tfdcf.TFDCFExtractor` methods).
        - ``--cutoff``              *<Optional>* The minimum term frequency to consider when ranking terms (used only with the :class:`~ate.stat.corpus.rank.RankExtractor` method).
        - ``--base``                *<Optional>* The logarithmic base (used only with the :class:`LogEF <ate.application.event.LogEF>`, :class:`~ate.application.event.EFIDF` and :class:`~ate.application.event.EFIDFEntropy` methods).
        - ``--idfs``                *<Optional>* The IDF files to use to calculate entropy (used only with the :class:`~ate.application.event.EFIDFEntropy` method)

        - ``--reranker``            *<Optional>* The method to use to re-rank the terms extracted by the base method; supported :class:`TF <ate.stat.tf.TFExtractor>`, :class:`TFIDF <ate.stat.tfidf.TFIDFExtractor>`, :class:`Rank <ate.stat.corpus.rank.RankExtractor>`, :class:`Specificity <ate.stat.corpus.specificity.SpecificityExtractor>`, :class:`TFDCF <ate.stat.corpus.tfdcf.TFDCFExtractor>`, :class:`EF <ate.application.event.EF>`, :class:`LogEF <ate.application.event.LogEF>`, :class:`EF-IDF <ate.application.event.EFIDF>`, :class:`EF-IDF-Entropy <ate.application.event.EFIDFEntropy>`.
        - ``--reranker-files``      *<Optional>* The corpora to use to calculate the new, re-ranked score for terms.
        - ``--reranker-keep``       *<Optional>* The number of terms to return, ordered in descending order of score; defaults to all terms.
        - ``--reranker-tfidf``      *<Optional>* The TF-IDF scheme to use to extract terms (used only with the :class:`~ate.stat.tfidf.TFIDFExtractor` and the :class:`~ate.application.event.EFIDF` methods).
        - ``--reranker-general``    *<Optional>* A path or paths to general corpora used for comparison with the domain-specific corpora (used only with the :class:`~ate.stat.corpus.rank.RankExtractor`, :class:`~ate.stat.corpus.specificity.SpecificityExtractor` and :class:`~ate.stat.corpus.tfdcf.TFDCFExtractor` methods).
        - ``--reranker-cutoff``     *<Optional>* The minimum term frequency to consider when ranking terms (used only with the :class:`~ate.stat.corpus.rank.RankExtractor` method).
        - ``--reranker-base``       *<Optional>* The logarithmic base (used only with the :class:`LogEF <ate.application.event.LogEF>`, :class:`~ate.application.event.EFIDF` and :class:`~ate.application.event.EFIDFEntropy` methods).
        - ``--reranker-idfs``       *<Optional>* The IDF files to use to calculate entropy (used only with the :class:`~ate.application.event.EFIDFEntropy` method)

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser.add_argument('-f', '--files', nargs='+', required=True,
                        help='<Required> The input corpora from where to extract domain-specific terms.')
    parser.add_argument('-m', '--method', type=method, required=True,
                        help='<Required> The method to use to extract domain-specific terms; supported: `TF`, `TFIDF`, `Rank`, `Specificity`, `TFDCF`, `EF`, `LogEF`, `EF-IDF`.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The path to the file where to store the extracted terms.')
    parser.add_argument('--keep', type=int, required=False, help='<Optional> The number of terms to return, ordered in descending order of score; defaults to all terms.')
    parser.add_argument('--tfidf', required=False, help='<Optional> The TF-IDF scheme to use to extract terms (used only with the `TF-IDF` method).')
    parser.add_argument('--general', nargs='+', required=False,
                        help='<Optional> A path or paths to general corpora used for comparison with the domain-specific corpora (used only with the `Rank`, `Specificity` and `TF-DCF` methods).')
    parser.add_argument('--cutoff', type=int, default=1, required=False,
                        help='<Optional> The minimum term frequency to consider when ranking terms (used only with the `Rank` method).')
    parser.add_argument('--base', type=int, default=None, required=False,
                        help='<Optional> The logarithmic base (used only with the `LogEF`, `EF-IDF` and `EF-IDF-Entropy` methods).')
    parser.add_argument('--idfs', nargs='+', required=False,
                        help='<Optional> The IDF files to use to calculate entropy (used only with the `EF-IDF-Entropy` method).')

    parser.add_argument('--reranker', type=method, required=False,
                        help='<Optional> The method to use to re-rank the terms extracted by the base method; supported `TF`, `TFIDF`, `Rank`, `Specificity`, `TFDCF`, `EF`, `LogEF`, `EF-IDF`.')
    parser.add_argument('--reranker-files', nargs='+', required=False,
                        help='<Required> The corpora to use to calculate the new, re-ranked score for terms.')
    parser.add_argument('--reranker-keep', type=int, required=False,
                        help='<Optional> The number of terms to return, ordered in descending order of score; defaults to all terms.')
    parser.add_argument('--reranker-tfidf', required=False,
                        help='<Optional> The TF-IDF scheme to use to extract terms (used only with the `TF-IDF` method).')
    parser.add_argument('--reranker-general', nargs='+', required=False,
                        help='<Optional> A path or paths to general corpora used for comparison with the domain-specific corpora (used only with the `Rank`, `Specificity` and `TF-DCF` methods).')
    parser.add_argument('--reranker-cutoff', type=int, default=1, required=False,
                        help='<Optional> The minimum term frequency to consider when ranking terms (used only with the `Rank` method).')
    parser.add_argument('--reranker-base', type=int, default=None, required=False,
                        help='<Optional> The logarithmic base (used only with the `LogEF`, `EF-IDF` and `EF-IDF-Entropy` methods).')
    parser.add_argument('--reranker-idfs', nargs='+', required=False,
                        help='<Optional> The IDF files to use to calculate entropy (used only with the `EF-IDF-Entropy` method).')

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

    """
    Create the extractor and extract the terms.
    """
    args = vars(args)
    extractor = create_extractor(args['method'], tfidf=args['tfidf'], general=args['general'],
                                 cutoff=args['cutoff'], base=args['base'])
    terms = extract(extractor=extractor, files=args['files'], keep=args['keep'], idfs=args['idfs'])

    """
    Extract the re-ranker parameters and re-rank.
    """
    if args['reranker']:
        pass

    tools.save(args['output'], { 'cmd': cmd, 'pcmd': pcmd, 'terms': terms })

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
    elif method == LogEF:
        base = int(base) if base else base
        return method(base=base) if base else method()
    elif method == EFIDF:
        if tfidf is None:
            parser.error("The TF-IDF scheme is required with the EF-IDF method.")

        tfidf = tools.load(tfidf)['tfidf']
        base = int(base) if base else base
        return method(tfidf, base=base)
    elif method == EFIDFEntropy:
        if tfidf is None:
            parser.error("The TF-IDF scheme is required with the EF-IDF-Entropy method.")

        tfidf = tools.load(tfidf)['tfidf']
        base = int(base) if base else base
        return method(tfidf, base=base)

    return method()

def extract(extractor, files, keep=None, idfs=None):
    """
    Extract terms using the given extractor from the given files.

    :param extractor: The extractor to use to extract terms.
    :type extractor: :class:`~ate.extractor.Extractor`
    :param files: The input corpora from where to extract domain-specific terms.
    :type files: str or list of str
    :param keep: The number of terms to return, ordered in descending order of score.
                 If ``None`` is given, all terms are returned.
    :type keep: int or None
    :param idfs: The IDF files, used by some extractors (:class:`~ate.application.event.EFIDFEntropy`) as part of the extraction.
    :type idfs: str or list of str

    :return: A list of terms, each as a dictionary including its:

             - ``term``,
             - ``score``, and
             - ``rank``.
    :rtype: list of dict
    """

    if type(extractor) == EFIDFEntropy:
        terms = extractor.extract(files, idfs=idfs)
    else:
        terms = extractor.extract(files)
    terms = sorted(terms.items(), key=lambda term: term[1], reverse=True)
    terms = terms[:keep] if keep else terms
    terms = [ { 'term': term, 'score': score, 'rank': rank + 1 } for rank, (term, score) in enumerate(terms) ]
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
        #. :class:`~ate.application.event.LogEF`
        #. :class:`~ate.application.event.EFIDF`
        #. :class:`~ate.application.event.EFIDFEntropy`

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
        'logef': LogEF,
        'efidf': EFIDF,
        'efidfentropy': EFIDFEntropy,
    }

    if method.lower() in methods:
        return methods[method.lower()]

    raise argparse.ArgumentTypeError(f"Invalid method value: { method }")

def reranker_params(params):
    """
    Extract the re-ranker parameters and remove the ``--reranker-`` prefix.

    :param args: A dictionary where the keys are the parameters and the values are the command-line arguments.
    :type args: dict

    :return: Another dictionary containing only the re-ranker parameters.
             The ``--reranker`` is left untouched, whereas ``--reranker-``-prefixed parameters lose the prefix.
    :rtype: dict
    """

    prefix = 'reranker_'
    reranker_params = { 'reranker': params.get('reranker') } if 'reranker' in params else { }
    reranker_params.update({ param[len(prefix):]: value for param, value in params.items() if param.startswith(prefix) })
    return reranker_params

if __name__ == "__main__":
    main()
