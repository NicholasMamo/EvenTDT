"""
The DEPICT participant detector is a complete solution based on the one proposed in _Reading Between Events: Exploring the Role of Machine Understanding in Event Tracking_.
By default, this participant detector uses the following configuration:

    #. :class:`~apd.extractors.local.annotation_extractor.AnnotationExtractor`,
    #. :class:`~apd.scorers.local.tf_scorer.TFScorer`,
    #. :class:`~apd.filters.local.rank_filter.RankFilter` with a ``k`` of 50,
    #. :class:`~apd.resolvers.external.wikipedia_search_resolver.WikipediaSearchResolver`,
    #. :class:`~apd.extrapolators.external.wikipedia_attribute_extrapolator.WikipediaAttributeExtrapolator`, and
    #. :class:`~apd.postprocessors.external.wikipedia_attribute_postprocessor.WikipediaAttributePostprocessor`.

.. note::

    The DEPICT participant detector uses, by default, the :class:`~apd.extractors.local.annotation_extractor.AnnotationExtractor`.
    If you are working with corpora collected using the Twitter APIv1, use another extractor, such as the :class:`~apd.extractors.local.entity_extractor.EntityExtractor` or :class:`~apd.extractors.local.twitterner_entity_extractor.TwitterNEREntityExtractor`.
"""

import os
import sys
from nltk.corpus import stopwords

paths = [ os.path.join(os.path.dirname(__file__)),
           os.path.join(os.path.dirname(__file__), '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from participant_detector import ParticipantDetector
from extractors.local import AnnotationExtractor
from scorers.local import TFScorer
from filters.local import RankFilter
from resolvers.external import WikipediaSearchResolver
from extrapolators.external import WikipediaAttributeExtrapolator
from postprocessors.external import WikipediaAttributePostprocessor
from nlp.tokenizer import Tokenizer

class DEPICTParticipantDetector(ParticipantDetector):
    """
    By default the DEPICT participant detector uses the following configuration:

        #. :class:`~apd.extractors.local.annotation_extractor.AnnotationExtractor`,
        #. :class:`~apd.scorers.local.tf_scorer.TFScorer`,
        #. :class:`~apd.filters.local.rank_filter.RankFilter` with a ``k`` of 50,
        #. :class:`~apd.resolvers.external.wikipedia_search_resolver.WikipediaSearchResolver`,
        #. :class:`~apd.extrapolators.external.wikipedia_attribute_extrapolator.WikipediaAttributeExtrapolator`, and
        #. :class:`~apd.postprocessors.external.wikipedia_attribute_postprocessor.WikipediaAttributePostprocessor`.

    However, they can be overriden in the constructor.
    """

    def __init__(self, scheme=None, corpus=None, extractor=None, scorer=None, filter=None,
                 resolver=None, extrapolator=None, postprocessor=None, *args, **kwargs):
        """
        Create the DEPICT participant detector.
        Any parameter that is not given uses the default configuration.


        :param scheme: The term-weighting scheme to use by the :class:`~apd.resolvers.external.wikipedia_search_resolver.WikipediaSearchResolver`.
                       These documents are used to compare the similarity with the domain of the candidates.
        :type scheme: :class:`~nlp.weighting.TermWeightingScheme`
        :param corpus: The path to the corpus of documents.
                       These documents may be tokenized already, but this class re-tokenizes them with its own :class:`~nlp.tokenizer.Tokenizer`.
        :type corpus: list of :class:`~nlp.document.Document`
        :param extractor: The participant detector's extractor.
                          This component is used to find candidate participants.
                          If it is not given, it defaults to the :class:`~apd.extractors.local.annotation_extractor.AnnotationExtractor`.
        :type extractor: None :class:`~apd.extractors.extractor.Extractor`
        :param scorer: The participant detector's scorer.
                       This component is used to give a score to the extractor's candidate participants.
                       If it is not given, it defaults to the :class:`~apd.scorers.local.tf_scorer.TFScorer`.
        :type scorer: None or :class:`~apd.scorers.scorer.Scorer`
        :param filter: The participant detector's filter.
                       This component is used to exclude candidates that are unlikely to be participants.
                       If it is not given, it defaults to the :class:`~apd.filters.local.rank_filter.RankFilter` with a ``k`` of 50.
        :type filter: None or :class:`~apd.filters.filter.Filter`
        :param resolver: The participant detector's resolver.
                         This component looks for the real keywords associated with a participant.
                         If it is not given, it defaults to the :class:`~apd.resolvers.external.wikipedia_search_resolver.WikipediaSearchResolver`.
        :type resolver: None or :class:`~apd.resolvers.resolver.Resolver`
        :param extrapolator: The participant detector's extrapolator.
                             This component looks for additional participants that might not be in the corpus.
                             If it is not given, it defaults to the :class:`~apd.extrapolators.external.wikipedia_attribute_extrapolator.WikipediaAttributeExtrapolator`.
        :type extrapolator: None or :class:`~apd.extrapolators.extrapolator.Extrapolator`
        :param postprocessor: The participant detector's postprocessor.
                              This component modifies the found participants.
                              If it is not given, it defaults to the :class:`~apd.postprocessors.external.wikipedia_attribute_postprocessor.WikipediaAttributePostprocessor`.
        :type postprocessor: None or :class:`~apd.postprocessors.postprocessor.Postprocessor`
        """

        """
        Tokenize the corpus.
        """
        tokenizer = Tokenizer(stopwords=stopwords.words('english'),
                              normalize_words=True, character_normalization_count=3,
                              remove_unicode_entities=True)

        """
        Set up the DEPICT participant detector.
        """
        extractor = extractor or AnnotationExtractor(*args, **kwargs)
        scorer = scorer or TFScorer(*args, **kwargs)
        filter = filter or RankFilter(keep=50, *args, **kwargs)
        resolver = resolver or WikipediaSearchResolver(scheme, tokenizer, 0.1, corpus, *args, **kwargs)
        extrapolator = extrapolator or WikipediaAttributeExtrapolator(prune=1, fetch=200, head_only=True, *args, **kwargs)
        postprocessor = postprocessor or WikipediaAttributePostprocessor(*args, **kwargs)

        super().__init__(extractor, scorer, filter, resolver, extrapolator, postprocessor)
