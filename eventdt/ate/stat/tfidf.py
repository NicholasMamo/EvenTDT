"""
TF-IDF is a strong and common baseline for ATE tasks.
The approach scores tokens based on their accumulated TF-IDF score.
"""

import json
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from extractor import Extractor

class TFIDFExtractor(Extractor):
	"""
	The TF-IDF extractor uses a TF-IDF scheme to score all tokens in the given corpora.
	The class expects tokenized corpora.

	:ivar scheme: The scheme used by the TF-IDF extractor to score tokens.
	:vartype scheme: :class:`~nlp.term_weighting.tfidf.TFIDF`
	"""

	def __init__(self, scheme):
		"""
		Create the TF-IDF extractor with the given scheme.

		:param scheme: The scheme used by the TF-IDF extractor to score tokens.
		:type scheme: :class:`~nlp.term_weighting.tfidf.TFIDF`
		"""

		self.scheme = scheme

	def extract(self, corpora, candidates=None):
		"""
		Extract terms from the given corpora.

		:param corpora: A path to a corpus or a list of paths to corpora where to look for terms.
						This extractor expects the corpora to be tokenized.
		:type corpora: str or list of str
		:param candidates: A list of terms for which to calculate a score.
						   If `None` is given, all words are considered to be candidates.
		:type candidates: None or list of str

		:return: A dictionary with terms as keys and their scores as values.
		:rtype: dict
		"""

		scores = { } if not candidates else dict.fromkeys(candidates, 0)

		corpora = self.to_list(corpora)
		for corpus in corpora:
			with open(corpus, 'r') as f:
				for line in f:
					document = self.scheme.create(json.loads(line)['tokens'])
					for term, score in document.dimensions.items():
						if (candidates and term in candidates) or not candidates:
							scores[term] = scores.get(term, 0) + score

		return scores
