"""
The log-likelihood ratio compares the observed co-occurrence of terms with their expected co-occurrence.
The expected co-occurrence, or the null hypothesis, is the number of times two terms appear if they were independent of each other.

The log-likelihood ratio is calculated as follows:

.. math::

	-2ln(\\lambda) = 2 \\cdot O ln(\\frac{O}{E})

where :math:`E` is the expected number of co-occurrences of two terms and :math:`O` is the actual number of observed co-occurrences.
The :math:`O` before the logarithm boosts common terms.

With this equation:

- Terms that appear more often than expected (that is, they are positively correlated) will have a positive logarithm;
- Terms that appear as often as expected (that is, they are independent) will have a logarithm of 0; and
- Terms that appear less often as expected (that is, they are negatively correlated), will have a negative logarithm.

To calculate the log-likelihood ratio, this algorithm uses a contingency table:

+-------------------------+-------------------------+-------------------------+
|                         || :math:`t_1`            | :math:`\\overline{t_1}`  |
+=========================+=========================+=========================+
| :math:`t_2`             || A                      | B                       |
+-------------------------+-------------------------+-------------------------+
| :math:`\\overline{t_2}`  || C                      | D                       |
+-------------------------+-------------------------+-------------------------+

In this table, the cells represent the following:

- `A`: terms :math:`t_1` and :math:`t_2` co-occur;
- `B`: terms :math:`t_2` appears, but :math:`t_1` doesn't;
- `C`: terms :math:`t_1` appears, but :math:`t_2` doesn't; and
- `D`: neither terms :math:`t_1` nor :math:`t_2` appear.
"""

import json
import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

import ate
from ate import linguistic
from ate.bootstrapping import Bootstrapper
from ate.stat import probability

class LogLikelihoodRatioBootstrapper(Bootstrapper):
	"""
	The log-likelihood ratio bootstrapper scores candidate terms based on how often they appear with seed terms.
	"""

	def bootstrap(self, corpora, seed=None, candidates=None, cache=None):
		"""
		Calculate the log-likelihood ratio statistic of co-occurrence for the seed set terms and the candidate terms.

		:param corpora: A corpus, or corpora, of documents.
						If a string is given, it is assumed to be one corpus.
						If a list is given, it is assumed to be a list of corpora.

						.. note::

							It is assumed that the corpora were extracted using the tokenizer tool.
							Therefore each line should be a JSON string representing a document.
							Each document should have a `tokens` attribute.
		:type corpora: str or list of str
		:param seed: The terms for which to compute the log-likelihood ratio.
					 These terms are combined as a cross-product with all terms in ``candidates``.
					 The terms can be provided as:

					 - A single word,
					 - A list of terms,
					 - A tuple, or
					 - A list of tuples.

					 A tuple translates to joint probabilities.
					 If nothing is given, it is replaced with the corpora's vocabulary.
		:type seed: None or str or list of str or tuple or list of tuple
		:param candidates: The terms for which to compute the log-likelihood ratio.
						   These terms are combined as a cross-product with all terms in ``seed``.
						   The terms can be provided as:

						   - A single word,
						   - A list of terms,
						   - A tuple, or
						   - A list of tuples.

						   A tuple translates to joint probabilities.
						   If nothing is given, it is replaced with the corpora's vocabulary.
		:type candidates: None or str or list of str or tuple or list of tuple
		:param cache: A list of terms that are re-used often and which should be cached.
					  If an empty list or `None` is given, no cache is used.

					  .. note::

						  Cache should be used when there is a lot of repetition.
						  For example, ``seed`` can be used as cache when ``seed`` is small and ``candidates`` is large.
						  If the data is small, using cache can be detrimental.
		:type cache: None or list of str

		:return: The scores of each seed term for each candidate.
				 Bootstrapping computes a score for the cross-product of the seed set and candidates.
				 In other words, there is a score for every possible combination of terms in the seed set, and terms in the candidates.
				 The log-likelihood ratio statistic scores are returned as a dictionary.
				 The keys are these pairs, and their log-likelihood ratio statistics are the values.
		:rtype: dict
		"""

		llratio = { }

		"""
		Convert the corpora and tokens into a list if they aren't already.
		The list of seed terms and candidates is always made into a list, even if it's a list of one string.
		"""
		corpora = self.to_list(corpora)
		seed = [ seed ] if type(seed) is str else seed
		candidates = [ candidates ] if type(candidates) is str else candidates

		"""
		Create the contingency tables and calculate the log-likelihood ratio statistic for each pair.
		"""
		tables = self._contingency_table(corpora, seed, candidates, cache=cache)
		llratio = { pair: self._ratio(table) for pair, table in tables.items() }

		return llratio

	def _contingency_table(self, corpora, seed, candidates, cache=None):
		"""
		Create the contingency tables for all the pairs of terms in ``seed`` and ``candidates``.
		All the terms in ``seed`` are matched with all terms in ``candidates`` in a cross-product fashion.

		:param corpora: A corpus, or corpora, of documents.
						If a string is given, it is assumed to be one corpus.
						If a list is given, it is assumed to be a list of corpora.

						.. note::

							It is assumed that the corpora were extracted using the tokenizer tool.
							Therefore each line should be a JSON string representing a document.
							Each document should have a `tokens` attribute.
		:type corpora: str or list of str
		:param seed: The terms for which to compute the log-likelihood ratio statistic.
					 These terms are combined as a cross-product with all terms in ``candidates``.
					 The terms can be provided as:

					 - A single word,
					 - A list of terms,
					 - A tuple, or
					 - A list of tuples.

					 A tuple translates to joint probabilities.
					 If nothing is given, it is replaced with the corpora's vocabulary.
		:type seed: None or str or list of str or tuple or list of tuple
		:param candidates: The terms for which to compute the log-likelihood ratio statistic.
						   These terms are combined as a cross-product with all terms in ``seed``.
						   The terms can be provided as:

						   - A single word,
						   - A list of terms,
						   - A tuple, or
						   - A list of tuples.

						   A tuple translates to joint probabilities.
						   If nothing is given, it is replaced with the corpora's vocabulary.
		:type candidates: None or str or list of str or tuple or list of tuple
		:param cache: A list of terms that are re-used often and which should be cached.
					  If an empty list or `None` is given, no cache is used.

					  .. note::

						  Cache should be used when there is a lot of repetition.
						  For example, ``seed`` can be used as cache when ``seed`` is small and ``candidates`` is large.
						  If the data is small, using cache can be detrimental.
		:type cache: None or list of str

		:return: A dictionary of contingency tables.
				 The keys are the pairs of the terms.
				 The values are four-tuples representing the values of cells in the order:

				 	1. Top-left,
					2. Top-right,
					3. Bottom-left, and
					4. Bottom-right.
		:rtype: dict
		"""

		return { }

	def _ratio(self, table):
		"""
		Calculate the log-likelihood ratio statistic from the given table.
		The log-likelihood ratio statistic is:

		- Positive if the two terms are correlated. The higher the statistic, the more correlated the two terms are.
		- Negative if the two terms are negatively correlated. The lower the statistic, the less correlated the two terms are.
		- Zero if the two terms are independent.

		:param table: The contingency table as a four-tuple.
					  The values are four-tuples representing the values of cells in the order:

		 			 	1. Top-left,
		 				2. Top-right,
		 				3. Bottom-left, and
		 				4. Bottom-right.
		:type table: tuple of int

		:return: The log-likelihood ratio statistic.
		:rtype: float
		"""

		return 0
