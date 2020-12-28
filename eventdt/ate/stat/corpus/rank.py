"""
Rank difference is a corpus comparison approach proposed by Kit and Liu.
The metric compares the rank of a term in the domain versus its rank in general corpora:

.. math::

    τ(w) = \\frac{r_D(w)}{|V_D|} - \\frac{r_B(w)}{|V_B|}

where :math:`w` is the word for which rank difference is calculated.
:math:`r_D(w)` and :math:`r_B(w)` are the ranks of the word :math:`w` in the domain and background corpora respectively.
Similarly, :math:`V_D` and :math:`V_B` are the total number of words in the domain and background corpora respectively.

The ranking mechanism can be any metric.
In this implementation, like in Kit and Liu's first approach, we use term frequency.
Note that rank 1 is the least common word.

The rank difference is bound in the range :math:`[1, -1)`:

- The maximum score, :math:`1`, is obtained when the word is at the top of its ranking in the domain—:math:`r_D(w) = |V_D|`—and the word does not appear in the background—:math:`r_B(w) = 0`.
- The minimum score, :math:`-1`, is exclusive.
  The rank difference tends to :math:`-1` when the word appears least frequently in the domain —:math:`r_D(w) = 1`—and the word is the most frequent in the background—:math:`r_B(w) = |V_B|`.

This approach actually bounds the rank difference in the range :math:`[1, -1]`.
This special case of a score of :math:`-1` occurs when a word does not appear in the domain, but it is the most frequent in the background.

.. note::

    Implementation based on the metric described in `Measuring mono-word termhood by rank difference via corpus comparison by Kit and Liu (2008) <https://benjamins.com/catalog/term.14.2.05kit>`_.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate import linguistic
from ate.stat.corpus import ComparisonExtractor
from ate.stat import TFExtractor

class RankExtractor(ComparisonExtractor):
    """
    The rank difference extractor stores a list of general corpora.
    It calculates the rank of terms in the general corpora.
    Then, the algorithm compares them with the terms' ranks in the domain.

    Since Twitter corpora include many typos and informal conversation habits, the distribution of words is very long-tailed.
    This means that the standard rank extractor implementation punishes terms that appear a few times in the general corpora.
    This is because even terms that appear 5 times are ranked very highly.
    Therefore this implementation allows a cutoff value that excludes terms with a lower term frequency.

    :ivar cutoff: The minimum term frequency of a term to be considered.
    :vartype cutoff: float
    """

    def __init__(self, general, cutoff=1):
        """
        Create the corpus comparison extractor with the general corpora and the policy to deal with unknown words.

        :param general: A path or a list of paths to general corpora, to be used for comparison.
                        Corpus comparison approaches expect the corpora to be tokenized.
        :type general: str or list of str
        :param cutoff: The minimum term frequency of a term to be considered.
                       The value is inclusive, so the default value of 1 includes all terms.
        :type cutoff: float

        :raises ValueError: When the cutoff is not an integer.
        :raises ValueError: When the cutoff is not positive.
        """

        super().__init__(general)

        """
        Validate the cutoff.
        """
        if type(cutoff) is not int or cutoff < 1:
            raise ValueError("The cutoff value must be a positive integer")

        self.cutoff = cutoff

    def extract(self, corpora, candidates=None):
        """
        Extract terms by scoring them using rank difference.

        :param corpora: A path to a corpus or a list of paths to corpora where to look for terms.
        :type corpora: str or list of str
        :param candidates: A list of terms which may be extracted.
                           If ``None`` is given, all words are considered to be candidates.

                           .. note::

                               If candidates are given, the cutoff point is ignored.
        :type candidates: None or list of str

        :return: A dictionary with terms as keys and their rank difference scores as values.
        :rtype: dict
        """

        scores = { }

        """
        Count the term frequencies of the terms in the domain and in the general corpora.
        """
        extractor = TFExtractor()
        tf_d = extractor.extract(corpora, candidates)
        tf_b = extractor.extract(self.general, candidates)

        """
        Filter the candidates if no candidates are given.
        """
        if not candidates:
            tf_d = self._filter_terms(tf_d)
            tf_b = self._filter_terms(tf_b)

        """
        Rank the terms in ascending order of their term frequency.
        """
        r_d = self._rank(tf_d)
        r_b = self._rank(tf_b)

        """
        Count the length of the rankings.
        """
        V_d = len(r_d)
        V_b = len(r_b)

        """
        To simplify the calculation, the rankings are converted into dictionaries.
        The algorithm uses it to calculate the scores for all domain terms.
        """
        r_d = { term: r + 1 for r, term in enumerate(r_d) }
        r_b = { term: r + 1 for r, term in enumerate(r_b) }
        if V_b:
            scores.update({ term: r_d[term] / V_d - r_b.get(term, 0) / V_b for term in r_d })
        else:
            scores.update({ term: r_d[term] / V_d for term in r_d })

        return scores

    def _filter_terms(self, tf):
        """
        Filter out terms with a lower term frequency than the extractor's cutoff point.

        :param tf: A dictionary containing term frequencies.
                   The keys are the terms, and the values are their frequencies.
        :type tf: dict

        :return: A new term frequency dictionary with terms having a term frequency equal to or higher than the cutoff point.
                 The keys are the terms, and the values are their frequencies.
        :rtype: dict
        """

        return { term: score for term, score in tf.items()
                              if score >= self.cutoff }

    def _rank(self, tf):
        """
        Rank the given terms in ascending order of their term frequency.

        :param tf: A dictionary containing term frequencies.
                   The keys are the terms, and the values are their frequencies.
        :type tf: dict

        :return: A sorted list of terms in ascending order of their frequencies.
        :rtype: list of str
        """

        return sorted(tf, key=tf.get, reverse=False)
