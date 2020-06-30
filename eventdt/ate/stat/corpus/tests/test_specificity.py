"""
Test the functionality of the domain specificity extractor functions.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate import linguistic
from ate.stat import probability
from ate.stat.corpus import SpecificityExtractor

class TestSpecificityExtractor(unittest.TestCase):
	"""
	Test the functionality of the domain specificity extractor functions.
	"""

	def test_unknown_words_all_not_in_domain(self):
		"""
		Test that all unknown words are not in the domain words.
		"""

		domain = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		domain_words = linguistic.vocabulary(domain)
		general_words = linguistic.vocabulary(general)
		general_words = dict.fromkeys(general_words, 1/len(general_words))

		extractor = SpecificityExtractor(general)
		self.assertTrue(all( word not in general_words for word in extractor._unknown(domain_words, general_words) ))

	def test_unknown_words_dict_all_not_in_domain(self):
		"""
		Test that all unknown words are not in the domain words even when providing the domain words as a dictionary.
		"""

		domain = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		domain_words = linguistic.vocabulary(domain)
		general_words = linguistic.vocabulary(general)
		domain_words = dict.fromkeys(domain_words, 1/len(domain_words))
		general_words = dict.fromkeys(general_words, 1/len(general_words))

		extractor = SpecificityExtractor(general)
		self.assertTrue(all( word not in general_words for word in extractor._unknown(domain_words, general_words) ))

	def test_unknown_words_zero_probability(self):
		"""
		Test that all unknown words are not in the domain words.
		"""

		domain = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		domain_words = linguistic.vocabulary(domain)
		general_words = linguistic.vocabulary(general)
		general_words = dict.fromkeys(general_words, 1/len(general_words))

		self.assertTrue('willian' not in general_words)
		self.assertTrue('willian' in domain_words)
		general_words['willian'] = 0

		extractor = SpecificityExtractor(general)
		self.assertTrue('willian' in extractor._unknown(domain_words, general_words))

	def test_unknown_words_unique(self):
		"""
		Test that all unknown words are unique.
		"""

		domain = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		domain_words = linguistic.vocabulary(domain)
		general_words = linguistic.vocabulary(general)
		general_words = dict.fromkeys(general_words, 1/len(general_words))

		extractor = SpecificityExtractor(general)
		self.assertEqual(len(set(extractor._unknown(domain_words, general_words))),
						 len(extractor._unknown(domain_words, general_words)))

	def test_rank_unknown_words_not_in_domain(self):
		"""
		Test that when ranking unknown words, words that do not appear in the domain are excluded.
		"""

		domain = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		domain_words = linguistic.vocabulary(domain)
		general_words = linguistic.vocabulary(general)
		general_words = dict.fromkeys(general_words, 1/len(general_words))

		extractor = SpecificityExtractor(general)
		unknown_words = extractor._unknown(domain_words, general_words)

		probabilities = probability.p(domain)
		scores = probabilities
		self.assertTrue('superlongword' not in domain_words)
		unknown_words.append('superlongword')

		unknown_scores = extractor._rank_unknown_words(unknown_words, scores, probabilities)
		self.assertFalse('superlongword' in unknown_scores)

	def test_rank_unknown_words_probability_zero(self):
		"""
		Test that when ranking unknown words with a probability of zero in the domain, they are excluded.
		"""

		domain = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		domain_words = linguistic.vocabulary(domain)
		general_words = linguistic.vocabulary(general)
		general_words = dict.fromkeys(general_words, 1/len(general_words))

		extractor = SpecificityExtractor(general)
		unknown_words = extractor._unknown(domain_words, general_words)

		probabilities = probability.p(domain)
		scores = probabilities
		self.assertTrue('superlongword' not in domain_words)
		unknown_words.append('superlongword')
		probabilities['superlongword'] = 0

		unknown_scores = extractor._rank_unknown_words(unknown_words, scores, probabilities)
		self.assertFalse('superlongword' in unknown_scores)

	def test_rank_unknown_words_empty_scores(self):
		"""
		Test that when there are no scores, the rankings start from 0.
		"""

		domain = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		domain_words = linguistic.vocabulary(domain)
		general_words = linguistic.vocabulary(general)
		general_words = dict.fromkeys(general_words, 1/len(general_words))

		extractor = SpecificityExtractor(general)
		unknown_words = extractor._unknown(domain_words, general_words)
		probabilities = probability.p(domain)
		scores = probabilities
		unknown_scores = extractor._rank_unknown_words(unknown_words, scores, probabilities)

		self.assertTrue(all( score > 0 for score in scores.values() ))

	def test_rank_unknown_words_order(self):
		"""
		Test that when ranking unknown words, words that appear more often in the domain have a higher score.
		"""

		domain = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		domain_words = linguistic.vocabulary(domain)
		general_words = linguistic.vocabulary(general)
		general_words = dict.fromkeys(general_words, 1/len(general_words))

		extractor = SpecificityExtractor(general)
		unknown_words = extractor._unknown(domain_words, general_words)
		probabilities = probability.p(domain)
		scores = probabilities
		unknown_scores = extractor._rank_unknown_words(unknown_words, scores, probabilities)

		ranking = sorted(unknown_scores, key=unknown_scores.get, reverse=True)
		for (i, term) in enumerate(ranking[:-1]):
			self.assertGreaterEqual(unknown_scores[term], unknown_scores[ranking[i + 1]])
			self.assertGreaterEqual(probabilities[term], probabilities[ranking[i + 1]])

	def test_rank_unknown_words_min(self):
		"""
		Test that when ranking unknown words, the lowest scoring word has the lowest probablity among the unknown words.
		"""

		domain = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		domain_words = linguistic.vocabulary(domain)
		general_words = linguistic.vocabulary(general)
		general_words = dict.fromkeys(general_words, 1/len(general_words))

		extractor = SpecificityExtractor(general)
		unknown_words = extractor._unknown(domain_words, general_words)
		probabilities = probability.p(domain)
		scores = probabilities
		unknown_scores = extractor._rank_unknown_words(unknown_words, scores, probabilities)
		unknown_probabilities = { term: probabilities[term] for term in unknown_words }
		self.assertEqual(min(unknown_probabilities, key=unknown_probabilities.get),
						 min(unknown_scores, key=unknown_scores.get))

	def test_rank_unknown_words_max(self):
		"""
		Test that when ranking unknown words, the highest scoring word has the highest probablity among the unknown words.
		"""

		domain = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		domain_words = linguistic.vocabulary(domain)
		general_words = linguistic.vocabulary(general)
		general_words = dict.fromkeys(general_words, 1/len(general_words))

		extractor = SpecificityExtractor(general)
		unknown_words = extractor._unknown(domain_words, general_words)
		probabilities = probability.p(domain)
		scores = probabilities
		unknown_scores = extractor._rank_unknown_words(unknown_words, scores, probabilities)
		unknown_probabilities = { term: probabilities[term] for term in unknown_words }
		self.assertEqual(max(unknown_probabilities, key=unknown_probabilities.get),
						 max(unknown_scores, key=unknown_scores.get))
