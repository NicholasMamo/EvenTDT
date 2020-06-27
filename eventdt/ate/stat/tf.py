"""
Term Frequency (TF) is a simple ATE approach that ranks terms based on the number of times that they appear.
"""

import json
import os
import sys

paths = [ os.path.join(os.path.dirname(__file__), '..'),
 		  os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

from extractor import Extractor
from nlp.term_weighting import TF

class TFExtractor(Extractor):
	"""
	The TF extractor uses the TF term-weighting scheme to score all tokens in the given corpora.
	The class expects tokenized corpora.
	"""

	def extract(self, corpora, candidates=None):
		"""
		Extract terms from the given corpora.

		:param corpora: A path to a corpus or a list of paths to corpora where to look for terms.
						This extractor expects the corpora to be tokenized.
		:type corpora: str or list of str
		:param candidates: A list of terms for which to calculate a score.
						   If `None` is given, all words are considered to be candidates.
		:type candidates: None or list of str

		:return: A dictionary with terms as keys and their TF scores as values.
		:rtype: dict
		"""

		scores = { } if not candidates else dict.fromkeys(candidates, 0)

		corpora = self.to_list(corpora)
		scheme = TF()
		for corpus in corpora:
			with open(corpus, 'r') as f:
				for line in f:
					document = scheme.create(json.loads(line)['tokens'])
					for term, score in document.dimensions.items():
						if (candidates and term in candidates) or not candidates:
							scores[term] = scores.get(term, 0) + score

		return scores