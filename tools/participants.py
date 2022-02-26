#!/usr/bin/env python3

"""
A tool to automatically extract participants from the given corpora.
This tool is meant to run on the understanding corpora to extract the event's participants.

To use a ready-made model, use:

.. code-block:: bash

    ./tools/participants.py \\
    -f data/understanding.json \\
    --clean \\
    --model ELDParticipantDetector \\
    --tfidf data/idf.json \\
    -o data/participants.json

Alternatively, you can create your own model:

.. code-block:: bash

    ./tools/participants.py \\
    -f data/understanding.json \\
    --clean \\
    --extractor EntityExtractor \\
    --scorer TFScorer \\
    --filter RankFilter -k 10 \\
    -o data/participants.json

You can modify an existing model by providing the components yourself.
For example, this snippet uses the :class:`~apd.extractors.local.entity_extractor.EntityExtractor` instead of the default :class:`~apd.extractors.local.twitterner_entity_extractor.TwitterNEREntityExtractor`:

.. code-block:: bash

    ./tools/participants.py \\
    -f data/understanding.json \\
    --clean \\
    --model ELDParticipantDetector \\
    --tfidf data/idf.json \\
    --extractor EntityExtractor \\
    -o data/participants.json

Accepted arguments:

    - ``-f --file``             *<Required>* The input corpus from where to extract participants.
    - ``-o --output``           *<Required>* The path to the file where to store the extracted participants.
    - ``-m --model``            *<Optional>* The type of model to use; supported: `ELDParticipantDetector`; defaults to a normal participant detector.
    - ``--extractor``           *<Optional>* The extractor to use to extract candidate participants; supported: `EntityExtractor` (default), `TokenExtractor`, `TwitterNEREntityExtractor`.
    - ``--scorer``              *<Optional>* The scorer to use to score candidate participants; supported: `TFScorer` (default), `DFScorer`, `LogDFScorer`, `LogTFScorer`.
    - ``--filter``              *<Optional>* The filter to use to filter candidate participants; supported: `RankFilter`, `ThresholdFilter`; defaults to no filter.
    - ``-k``                    *<Optional>* The number of candidates to retain when filtering candidates (used only with the `RankFilter`).
    - ``--threshold``           *<Optional>* The score threshold to use when filtering candidates (used only with the `ThresholdFilter`).
    - ``--tfidf``               *<Optional>* The TF-IDF scheme to use when creating documents (used only with the `ELDParticipantDetector` model).
"""

import argparse
import copy
import json
import numbers
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

import tools
from apd import ParticipantDetector, ELDParticipantDetector
from apd.extractors import local
from apd.scorers.local import *
from apd.filters import Filter
from apd.filters.local import *
from logger import logger
from nlp.cleaners import TweetCleaner
from nlp.document import Document
from nlp.tokenizer import Tokenizer
import twitter

parser = argparse.ArgumentParser(description="Extract event participants from the understanding corpora.")
def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-f --file``             *<Required>* The input corpus from where to extract participants.
        - ``-o --output``           *<Required>* The path to the file where to store the extracted participants.
        - ``-m --model``            *<Optional>* The type of model to use; supported: `ELDParticipantDetector`; defaults to a normal participant detector.
        - ``--extractor``           *<Optional>* The extractor to use to extract candidate participants; supported: `EntityExtractor` (default), `TokenExtractor`, `TwitterNEREntityExtractor`.
        - ``--scorer``              *<Optional>* The scorer to use to score candidate participants; supported: `TFScorer` (default), `DFScorer`, `LogDFScorer`, `LogTFScorer`.
        - ``--filter``              *<Optional>* The filter to use to filter candidate participants; supported: `RankFilter`, `ThresholdFilter`; defaults to no filter.
        - ``-k``                    *<Optional>* The number of candidates to retain when filtering candidates (used only with the `RankFilter`).
        - ``--threshold``           *<Optional>* The score threshold to use when filtering candidates (used only with the `ThresholdFilter`).
        - ``--tfidf``               *<Optional>* The TF-IDF scheme to use when creating documents (used only with the `ELDParticipantDetector` model).

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser.add_argument('-f', '--file', type=str, required=True,
                        help='<Required> The input corpus from where to extract participants.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The path to the file where to store the extracted terms.')
    parser.add_argument('-m', '--model', type=model, required=False, default=ParticipantDetector,
                        help='<Optional> The type of model to use; supported: `ELDParticipantDetector`; defaults to a normal participant detector.')
    parser.add_argument('--extractor', type=extractor, required=False, default=None,
                        help='<Optional> The extractor to use to extract candidate participants; supported: `EntityExtractor` (default), `TokenExtractor`, `TwitterNEREntityExtractor`.')
    parser.add_argument('--scorer', type=scorer, required=False, default=None,
                        help='<Optional> The scorer to use to score candidate participants; supported: `TFScorer` (default), `DFScorer`, `LogDFScorer`, `LogTFScorer`.')
    parser.add_argument('--filter', type=filter, required=False, default=None,
                        help='<Optional> The filter to use to filter candidate participants; supported: `RankFilter`, `ThresholdFilter`; defaults to no filter.')
    parser.add_argument('-k', required=False,
                        help='<Optional> The number of candidates to retain when filtering candidates (used only with the `RankFilter`).')
    parser.add_argument('--threshold', required=False,
                        help='<Optional> The score threshold to use when filtering candidates (used only with the `ThresholdFilter`).')
    parser.add_argument('--tfidf', required=False, default=None,
                        help='<Optional> The TF-IDF scheme to use when creating documents (used only with the `ELDParticipantDetector` model).')

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
    cmd, pcmd = tools.meta(args), tools.meta(args)

    args = vars(args)
    detector = create_detector(model=args.pop('model'), extractor=args.pop('extractor'),
                               scorer=args.pop('scorer'), filter=args.pop('filter'),
                               corpus=args['file'], **args)

    cmd['model'], pcmd['model'] = str(type(detector).__name__), str(type(detector).__name__)
    cmd['extractor'], pcmd['extractor'] = str(type(detector.extractor).__name__), str(type(detector.extractor).__name__)
    cmd['scorer'], pcmd['scorer'] = str(type(detector.scorer).__name__), str(type(detector.scorer).__name__)
    cmd['filter'], pcmd['filter'] = str(type(detector.filter).__name__), str(type(detector.filter).__name__)
    cmd['resolver'], pcmd['resolver'] = str(type(detector.resolver).__name__), str(type(detector.resolver).__name__)
    cmd['extrapolator'], pcmd['extrapolator'] = str(type(detector.extrapolator).__name__), str(type(detector.extrapolator).__name__)
    cmd['postprocessor'], pcmd['postprocessor'] = str(type(detector.postprocessor).__name__), str(type(detector.postprocessor).__name__)

    scored, filtered, resolved, extrapolated, postprocessed = detect(detector=detector, corpus=args['file'])
    tools.save(args['output'], { 'cmd': cmd, 'pcmd': pcmd,
                                 'scored': scored, 'filtered': filtered,
                                 'resolved': resolved, 'extrapolated': extrapolated, 'postprocessed': postprocessed })

def create_detector(model, extractor, scorer, filter, corpus=None, *args, **kwargs):
    """
    Create all the components of the participant detector.

    :param model: The class of the participant detector to use to extract participants.
    :type model: :class:`~apd.participant_detector.ParticipantDetector`
    :param extractor: The class of the extractor with which to extract candidate participants.
    :type extractor: :class:`~apd.extractors.extractor.Extractor`
    :param scorer: The class of the scorer with which to score candidate participants.
    :type scorer: :class:`~apd.scorers.scorer.Scorer`
    :param filter: The class of the filter with which to filter candidate participants.
    :type filter: :class:`~apd.filters.filter.Filter`
    :param corpus: A list of :class:`~nlp.document.Document` making up the corpus.
    :type corpus: list of :class:`~nlp.document.Document`

    :return: The created participant detector.
    :rtype: :class:`~apd.participant_detector.ParticipantDetector`
    """

    extractor = create_extractor(extractor, *args, **kwargs)
    scorer = create_scorer(scorer, *args, **kwargs)
    filter = create_filter(filter, *args, **kwargs)
    detector = create_model(model, extractor, scorer, filter, corpus=corpus, *args, **kwargs)
    logger.info(f"Extractor: { type(detector.extractor).__name__ }")
    logger.info(f"Scorer: { type(detector.scorer).__name__ }")
    logger.info(f"Filter: { type(detector.filter).__name__ }")
    logger.info(f"Resolver: { type(detector.resolver).__name__ }")
    logger.info(f"Extrapolator: { type(detector.extrapolator).__name__ }")
    logger.info(f"Postprocessor: { type(detector.postprocessor).__name__ }")

    return detector

def detect(detector, corpus):
    """
    Detect participants from the given corpus.

    :param detector: The participant detector to use to extract participants.
    :type detector: :class:`~apd.participant_detector.ParticipantDetector`
    :param corpus: The path to the corpus.
    :type corpus: str

    :return: A list of participants detected at each stage: the extracted, scored, filtered, resolved, extrapolated and post-processed participants.
    :rtype: tuple of list of str
    """

    extracted, scored, filtered, resolved, extrapolated, postprocessed = detector.detect(corpus=corpus)
    return (rank(scored), rank(filtered),
            rank(resolved), rank(extrapolated), rank(postprocessed))

def rank(participants):
    """
    Convert the list of participants into a ranked list.
    The ranked list includes not just the participant but also the associated rank for easier parsing.

    :param participants: The list of participants to rank.
    :type participants: list of str

    :return: A ranked list of participants as a dictionary, each including, at least:

             - ``participant``, and
             - ``rank.
    :rtype: list of dict
    """

    ranked = [ ]

    participants = copy.deepcopy(participants)

    # if the participants are a dictionary, assume that the key is the participant's name and the value its score
    if type(participants) is dict and all( isinstance(value, numbers.Number) for value in participants.values() ):
        # sort the participants in descending order of score first
        ranked = sorted(participants.items(), key=lambda participant: participant[1], reverse=True)
        ranked = [ { 'participant': participant, 'score': score, 'rank': rank + 1 } for rank, (participant, score) in enumerate(ranked) ]

    # if the list of participants is a list, assumed that it has already been sorted
    if type(participants) is list:
        ranked = [ { 'participant': participant, 'rank': rank + 1 } for rank, participant in enumerate(participants) ]

    return ranked

def create_model(model, extractor, scorer, filter, corpus, tfidf=None, *args, **kwargs):
    """
    Create a participant detector model from the given components.

    :param model: The class of the participant detector to use to extract participants.
    :type model: :class:`~apd.participant_detector.ParticipantDetector`
    :param extractor: The extractor with which to extract candidate participants.
    :type extractor: :class:`~apd.extractors.extractor.Extractor`
    :param scorer: The scorer with which to score candidate participants.
    :type scorer: :class:`~apd.scorers.scorer.Scorer`
    :param filter: The filter with which to filter candidate participants.
    :type filter: :class:`~apd.filters.filter.Filter`
    :param corpus: A list of :class:`~nlp.document.Document` making up the corpus.
    :type corpus: list of :class:`~nlp.document.Document`
    :param tfidf: The path the TF-IDF scheme.
    :type tfidf: str

    :return: A new participant detector model.
    :rtype: :class:`~apd.participant_detector.ParticipantDetector`

    :raises ValueError: When the TF-IDF scheme is not given.
    """

    if model.__name__ == ELDParticipantDetector.__name__:
        if tfidf is None:
            raise ValueError("The TF-IDF scheme is required with the ELDParticipantDetector model.")
        scheme = tools.load(tfidf)['tfidf']
        return model(scheme=scheme, corpus=corpus, extractor=extractor, scorer=scorer, filter=filter, *args, **kwargs)
    elif model.__name__ == ParticipantDetector.__name__:
        extractor = extractor or local.EntityExtractor()
        scorer = scorer or TFScorer()
        return model(extractor, scorer, filter, *args, **kwargs)

def create_extractor(extractor, *args, **kwargs):
    """
    Create an extractor from the given class.

    :param extractor: The class of the extractor with which to extract candidate participants.
    :type extractor: :class:`~apd.extractors.extractor.Extractor`
    """

    return extractor() if extractor else extractor

def create_scorer(scorer, *args, **kwargs):
    """
    Create a scorer from the given class.

    :param scorer: The class of the scorer with which to score candidate participants.
    :type scorer: :class:`~apd.scorers.scorer.Scorer`
    """

    return scorer() if scorer else scorer

def create_filter(filter, k=None, threshold=None, *args, **kwargs):
    """
    Create a filter from the given class.

    :param filter: The class of the filter with which to filter candidate participants.
    :type filter: :class:`~apd.filters.filter.Filter`
    :param k: The number of candidates to retain when filtering.
              This is used only with the :class:`~apd.filters.local.rank_filter.RankFilter`.
    :type k: int
    :param threshold: The score threshold to use when filtering candidates.
                       This is used only with the :class:`~appd.filters.local.threshold_filter.ThresholdFilter`.

    :raises ValueError: When a :class:`~apd.filters.local.rank_filter.RankFilter` is to be created, but _k_ is not given.
    :raises ValueError: When a :class:`~appd.filters.local.threshold_filter.ThresholdFilter` is to be created, but the threshold is not given.
    """

    if not filter:
        return filter

    if filter.__name__ == RankFilter.__name__:
        if k is None:
            raise ValueError("The Rank Filter requires the `k` parameter (the number of candidates to retain).")
        return filter(int(k))
    if filter.__name__ == ThresholdFilter.__name__:
        if threshold is None:
            raise ValueError("The Threshold Filter requires the `threshold` parameter (the minimum score of a candidate to retain it).")
        return filter(float(threshold))

    return filter()

def model(method):
    """
    Convert the given string into a model class.
    The accepted classes are:

        #. :class:`~apd.eld_participant_detector.ELDParticipantDetector`

    :param method: The model string.
    :type method: str

    :return: The participant detector type that corresponds to the given method.
    :rtype: :class:`~apd.participant_detector.ParticipantDetector`
    """

    if method.lower() == 'eldparticipantdetector':
        return ELDParticipantDetector

    raise argparse.ArgumentTypeError(f"Invalid model: {method}")

def extractor(method):
    """
    Convert the given string into an extractor class.
    The accepted classes are:

        #. :class:`~apd.extractors.local.EntityExtractor`
        #. :class:`~apd.extractors.local.TokenExtractor`
        #. :class:`~apd.extractors.local.TwitterNEREntityExtractor`

    :param method: The extractor string.
    :type method: str

    :return: The extractor type that corresponds to the given method.
    :rtype: :class:`~apd.extractors.extractor.Extractor`
    """

    methods = {
        'entityextractor': local.EntityExtractor,
        'tokenextractor': local.TokenExtractor,
    }

    if method.lower() in methods:
        return methods[method.lower()]
    elif method.lower() == 'twitternerentityextractor':
        from apd.extractors.local.twitterner_entity_extractor import TwitterNEREntityExtractor
        return TwitterNEREntityExtractor

    raise argparse.ArgumentTypeError(f"Invalid extractor method: {method}")

def scorer(method):
    """
    Convert the given string into a scorer class.
    The accepted classes are:

        #. :class:`~apd.scorers.local.DFScorer`
        #. :class:`~apd.scorers.local.LogDFScorer`
        #. :class:`~apd.scorers.local.LogTFScorer`
        #. :class:`~apd.scorers.local.TFScorer`

    :param method: The scorer string.
    :type method: str

    :return: The extractor type that corresponds to the given method.
    :rtype: :class:`~apd.scorers.scorer.Scorer`
    """

    methods = {
        'dfscorer': DFScorer,
        'logdfscorer': LogDFScorer,
        'logtfscorer': LogTFScorer,
        'tfscorer': TFScorer,
    }

    if method.lower() in methods:
        return methods[method.lower()]

    raise argparse.ArgumentTypeError(f"Invalid scorer method: {method}")

def filter(method):
    """
    Convert the given string into a filter class.
    The accepted classes are:

        #. :class:`~apd.filters.local.RankFilter`
        #. :class:`~apd.filters.local.ThresholdFilter`

    :param method: The filter string.
    :type method: str

    :return: The extractor type that corresponds to the given method.
    :rtype: :class:`~apd.filters.filter.Filter`
    """

    methods = {
        'rankfilter': RankFilter,
        'thresholdfilter': ThresholdFilter,
    }

    if method.lower() in methods:
        return methods[method.lower()]

    raise argparse.ArgumentTypeError(f"Invalid filter method: {method}")

if __name__ == "__main__":
    main()
