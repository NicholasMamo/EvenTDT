"""
Pointwise Mutual Information (PMI) measures how much information one variable gives about another.
It is a symmetric measure, computed as:

.. math::

    PMI(x,y) = \\log( \\frac{p(x,y)}{p(x)p(y)} )

where `x` and `y` are the two variables.
"""

import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate import linguistic
from ate.bootstrapping import Bootstrapper
from ate.stat import probability

class PMIBootstrapper(Bootstrapper):
    """
    The Pointwise Mutual Information (PMI) bootstrapper scores candidate terms based on how much they correlate with seed terms.

    :ivar base: The base of the logarithm, defaults to 2.
    :vartype base: float
    """

    def __init__(self, base=2):
        """
        Create the PMI bootstrapper with the logarithmic base to use in the calculation.

        :param base: The base of the logarithm, defaults to 2.
        :type base: float
        """

        self.base = base

    def bootstrap(self, corpora, seed=None, candidates=None, cache=None):
        """
        Calculate the Pointwise Mutual-Information (PMI) between the seed set terms and the candidate terms..

        :param corpora: A corpus, or corpora, of documents.
                        If a string is given, it is assumed to be one corpus.
                        If a list is given, it is assumed to be a list of corpora.

                        .. note::

                            It is assumed that the corpora were extracted using the tokenizer tool.
                            Therefore each line should be a JSON string representing a document.
                            Each document should have a `tokens` attribute.
        :type corpora: str or list of str
        :param seed: The terms for which to compute the probability.
                     These terms are combined as a cross-product with all terms in `candidates`.
                     The terms can be provided as:

                     - A single word,
                     - A list of terms,
                     - A tuple, or
                     - A list of tuples.

                     A tuple translates to joint probabilities.
                     If nothing is given, it is replaced with the corpora's vocabulary.
        :type seed: None or str or list of str or tuple or list of tuple
        :param candidates: The terms for which to compute the probability.
                           These terms are combined as a cross-product with all terms in `seed`.
                           The terms can be provided as:

                           - A single word,
                           - A list of terms,
                           - A tuple, or
                           - A list of tuples.

                           A tuple translates to joint probabilities.
                           If nothing is given, it is replaced with the corpora's vocabulary.
        :type candidates: None or str or list of str or tuple or list of tuple
        :param cache: A list of terms that are re-used often and which should be cached.
                      If an empty list or ``None`` is given, no cache is used.

                      .. note::

                          Cache should be used when there is a lot of repetition.
                          For example, `seed` can be used as cache when `seed` is small and `candidates` is large.
                          If the data is small, using cache can be detrimental.
        :type cache: None or list of str

        :return: The scores of each seed term for each candidate.
                 Bootstrapping computes a score for the cross-product of the seed set and candidates.
                 In other words, there is a score for every possible combination of terms in the seed set, and terms in the candidates.
                 The PMI scores are returned as a dictionary.
                 The keys are these pairs, and their PMI are the values.
        :rtype: dict
        """

        pmi = { }

        """
        The list of tokens in `seed` and `candidates` is always made into a list, even if it's a list of one string or tuple.
        """
        corpora = self.to_list(corpora)
        seed, candidates = seed or [ ], candidates or [ ]
        seed = [ seed ] if type(seed) is tuple or type(seed) is str else seed
        candidates = [ candidates ] if type(candidates) is tuple or type(candidates) is str else candidates

        if not seed:
            seed = linguistic.vocabulary(corpora)

        if not candidates:
            candidates = linguistic.vocabulary(corpora)

        """
        Get the 'vocabulary' for which to compute probabilities.
        This vocabulary is made up of all the elements in `seed` and `candidates`, as well as the cross-product between them.
        """
        prior = list(set(seed + candidates))
        prob = probability.p(corpora, focus=prior+probability.joint_vocabulary(seed, candidates), cache=cache)

        """
        Calculate the PMI from the probabilities.
        """
        for term in seed:
            for candidate in candidates:
                pmi[(term, candidate)] = self._pmi(prob, term, candidate)

        return pmi

    def _pmi(self, prob, x, y):
        """
        Calculate the Pointwise Mutual Information (PMI) of `x` and `y` based on the given probabilities.

        :param prob: A probability calculation, possibly calculated using the :func:`ate.stat.probability.p` function.
                     This is used as cache for the probabilities.
                     The keys are the tokens, including the joint probability of `x` and `y`, and the values are their probabilities.
        :type prob: dict
        :param x: The first token or tuple of tokens to use to calculate the PMI.
        :type x: str or tuple of str
        :param y: The second token or tuple of tokens to use to calculate the PMI.
        :type y: str or tuple of str
        :param base: The base of the logarithm, defaults to 2.
        :type base: float

        :return: The PMI of `x` and `y`.
        :rtype: float
        """

        joint = probability.joint_vocabulary(x, y)[0]
        if not prob[x] or not prob[y] or not prob[joint]:
            return 0

        return math.log(prob[joint]/( prob[x] * prob[y] ), self.base)
