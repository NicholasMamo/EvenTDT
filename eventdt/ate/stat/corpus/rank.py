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
	"""

	def extract(self, corpora, candidates=None):
		"""
		Extract terms by scoring them using rank difference.

		:param corpora: A path to a corpus or a list of paths to corpora where to look for terms.
		:type corpora: str or list of str
		:param candidates: A list of terms which may be extracted.
						   If `None` is given, all words are considered to be candidates.
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
