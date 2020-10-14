"""
Term Frequency-Disjoint Corpora Frequency (TF-DCF) is an ATE approach proposed by Lopes et al.
TF-DCF compares the term frequency of a term in a domain corpus against general corpora:

.. math::

    tf-dcf_t^{(c)} = \\frac{tf_t^{(c)}}{\\prod_{\\forall g \\in G} 1 + \\log( 1 + tf_t^{(g)} )}

where :math:`t` is the term for which TF-DCF is being calculated.
:math:`c` and :math:`G` are the domain-specific corpus and the general corpora respectively.
:math:`tf_t^{(c)}` is the term frequency of term :math:`t` in corpus :math:`(c)`.

.. note::

    Implementation based on the metric outlined in `Estimating term domain relevance through term frequency, disjoint corpora frequency - tf-dcf by Lopes et al. (2016) <https://www.sciencedirect.com/science/article/abs/pii/S0950705115004979>`_.
    This paper is based on an earlier paper by the same authors.
"""

import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate.stat.corpus import ComparisonExtractor
from ate.stat import TFExtractor

class TFDCFExtractor(ComparisonExtractor):
    """
    The TF-DCF extractor stores a list of general corpora.
    It uses these corpora to identify terms that appear very often in domain-specific corpora than in the general corpora.
    """

    def extract(self, corpora, candidates=None):
        """
        Extract terms by scoring them using TF-DCF.

        :param corpora: A path to a corpus or a list of paths to corpora where to look for terms.
        :type corpora: str or list of str
        :param candidates: A list of terms which may be extracted.
                           If `None` is given, all words are considered to be candidates.
        :type candidates: None or list of str

        :return: A dictionary with terms as keys and their TF-DCF scores as values.
        :rtype: dict
        """

        scores = { }

        """
        The TF-DCF is based on term frequency, both for the TF component and the DCF component.
        """
        extractor = TFExtractor()

        """
        Extract the TF from the domain-specific corpora.
        """
        tf = extractor.extract(corpora, candidates)

        """
        Calculate the DCF scores of the terms from the general corpora.
        """
        dcf = { }
        for corpus in self.general:
            tf_g = extractor.extract(corpus, candidates)
            for term in tf:
                dcf[term] = dcf.get(term, 1) * (1 + math.log(1 + tf_g.get(term, 0), 10))

        """
        Combine the TF and DCF scores.
        """
        scores = { term: tf[term] / dcf[term] for term in tf }
        return scores
