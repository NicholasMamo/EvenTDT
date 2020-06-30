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
						   If `None` is given, all words are considered to be candidates.
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
