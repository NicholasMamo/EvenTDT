"""
Domain specificity is a corpus comparison approach proposed by Park et al.
The metric promotes terms that appears in the domain corpus more frequently than in general corpora:

.. math::

    specificity(w) = \\frac{p_d(w)}{p_g(w)} = \\frac{\\frac{c_d(w)}{N_d}}{\\frac{c_g(w)}{N_g}}

where :math:`w` is the word for which domain specificity is calculated.
:math:`p_d(w)` and :math:`p_g(w)` are the probabilities that the word :math:`w` appears in the domain-specific corpus :math:`d` and the general corpus :math:`g` respectively.
Domain specificity can also be expressed in terms of token frequency.
:math:`c_d(w)` and :math:`c_g(w)` are word :math:`w`'s frequency in the domain-specific corpus :math:`d` and the general corpus :math:`g` respectively.
Similarly, :math:`N_d` and :math:`N_g` are the number of words in the domain-specific corpus :math:`d` and the general corpus :math:`g` respectively.

.. note::

    Implementation based on the metric described in `An Empirical Analysis of Word Error Rate and Keyword Error Rate by Park et al. (2008) <https://www.isca-speech.org/archive/interspeech_2008/i08_2070.html>`_.
    Domain specificity was also used in the field of ATE by `Chung et al. (2003) in A Corpus Comparison Approach for Terminology Extraction <https://www.jbe-platform.com/content/journals/10.1075/term.9.2.05chu>`_, among others.
"""

import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate.stat.corpus import ComparisonExtractor
from ate.stat import probability

class SpecificityExtractor(ComparisonExtractor):
    """
    The domain specificity extractor stores a list of general corpora.
    It uses these corpora to identify terms that appear very often in domain-specific corpora than in the general corpora.
    Since this metric is based on probability in the general corpora, the specificity of an unknown word is infinite.
    Therefore the domain specificity extractor allows a policy to ignore unknown words.

    :ivar ignore_unknown: A boolean indicating whether to ignore words that do not appear in the general corpora.
                          If `True`, unknown words are ignored and not included in the scores.
                          If `False`, the score of unknown words is set to be higher than the scores of known words.
                          The more often an unknown word appears in the domain-specific corpora, the higher its score.
    :vartype ignore_unknown: bool
    """

    def __init__(self, general, ignore_unknown=True):
        """
        Create the corpus comparison extractor with the general corpora and the policy to deal with unknown words.

        :param general: A path or a list of paths to general corpora, to be used for comparison.
                        Corpus comparison approaches expect the corpora to be tokenized.
        :type general: str or list of str
        :param ignore_unknown: A boolean indicating whether to ignore words that do not appear in the general corpora.
                               If `True`, unknown words are ignored and not included in the scores.
                               If `False`, the score of unknown words is set to be higher than the scores of known words.
                               The more often an unknown word appears in the domain-specific corpora, the higher its score.
                               The policy defaults to ignoring unknown words.
                               This is because Twitter suffers from misspellings and informal writing.
                               This behavior leads to many unknown words.
        :type ignore_unknown: bool
        """

        super().__init__(general)
        self.ignore_unknown = ignore_unknown

    def extract(self, corpora, candidates=None):
        """
        Extract terms by scoring them using domain specificity.

        :param corpora: A path to a corpus or a list of paths to corpora where to look for terms.
        :type corpora: str or list of str
        :param candidates: A list of terms which may be extracted.
                           If ``None`` is given, all words are considered to be candidates.
                           If candidate terms are given, the `ignore_unknown` policy is overriden.
        :type candidates: None or list of str

        :return: A dictionary with terms as keys and their domain specificity scores as values.
        :rtype: dict
        """

        scores = { }

        """
        Calculate the word probabilities.
        """
        p_d = probability.p(corpora, candidates)
        p_g = probability.p(self.general, candidates)

        """
        Calculate the scores for all known words.
        """
        unknown_words = self._unknown(p_d, p_g)
        scores.update({ term: p_d[term] / p_g[term] for term in p_d
                                                     if term not in unknown_words })

        """
        If unknown words should not be ignored, set their score.
        """
        if not self.ignore_unknown or candidates:
            scores.update(self._rank_unknown_words(unknown_words, scores, p_d))

        return scores

    def _unknown(self, domain_words, general_words):
        """
        Get the list of the unknown words in the general words.
        These are either words that are not in the domain words, or words that have a probability of 0.

        :param domain_words: A list of words found in the domain.
        :type domain_words: list of str or dict
        :param general_words: A dictionary with words as keys and their probabilities of appearing in the general corpora as values.
        :type general_words: dict

        :return: A list of words that either appear in the domain, but not in the general corpora, or which have a probability of 0 of appearing in the general corpora.
        :rtype: list of str
        """

        unknown = [ word for word in domain_words
                         if word not in general_words ]
        unknown.extend([ word for word in general_words
                               if not general_words[word] ])
        return unknown

    def _rank_unknown_words(self, unknown, scores, probabilities):
        """
        Rank the unknown terms.
        All unknown terms have a higher score than the known terms (because their score should be, theoretically, infinite).
        However, since not all unknown words are equal, the scores are not all infinite.
        Instead, the scores start from the highest known score.

        .. note::

            Terms that appear neither in the domain nor in the general corpora are akin to a fraction :math:`\\frac{0}{0}`.
            In this case, the function gives them a score of 0.

        :param unknown: A list of unknown words.
        :type unknown: list of str
        :param scores: The current known scores as a dictionary.
                       The terms are the keys and the values are the corresponding scores.
        :type scores: dict
        :param probabilities: The probabilities of the domain words.
                              The terms are the keys and the values are the corresponding probabilities.
        :type probabilities: dict

        :return: A dictionary of scores for the unknown terms.
                 The terms are the keys and the values are the corresponding scores.
        :rtype: dict
        """

        unknown_scores = { }

        """
        Remove unknown terms that do not appear in the domain either.
        """
        terms = [ term for term in unknown
                       if term in probabilities and
                             probabilities.get(term) ]

        """
        Get the maximum score of known words.
        If there are no known words, start from 0.
        This may happen when all domain words are unknown.
        """
        max_score = max(scores.values()) if scores else 0

        """
        Sort the terms in ascending order of their probability of appearing in the domain.
        """
        terms = sorted(terms, key=probabilities.get, reverse=False)

        """
        Rank the unknown terms.
        The scores start from the maximum score and increase with an increment of 1.
        Terms that appear neither in the domain nor in the general corpora get a score of 0.
        """
        unknown_scores.update({ term: max_score + (i + 1) for (i, term) in enumerate(terms) })
        unknown_scores.update({ term: 0 for term in unknown
                                         if not probabilities.get(term) })

        return unknown_scores
