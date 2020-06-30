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

	def test_extract(self):
		"""
		Test that the extracted terms make sense.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = SpecificityExtractor(general)
		terms = extractor.extract(corpora)
		terms = sorted(terms, key=terms.get, reverse=True)
		self.assertTrue('chelsea' in terms[:10])
		self.assertTrue('crystal' in terms[:10])
		self.assertTrue('hazard' in terms[:10])
		self.assertTrue('cfc' in terms[:10])

	def test_extract_positive(self):
		"""
		Test that the scores of all extracted terms are positive.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = SpecificityExtractor(general)
		terms = extractor.extract(corpora)
		self.assertLess(0, min(terms.values()))

	def test_extract_ignore_unknown_excludes_words_from_one_corpus(self):
		"""
		Test that the domain specificity extractor excludes unknown terms from one corpus when the policy is set to ignore unknown terms.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = SpecificityExtractor(general, ignore_unknown=True)
		vocabulary = linguistic.vocabulary(corpora)
		terms = extractor.extract(corpora)
		self.assertTrue(any( term not in terms for term in vocabulary ))

	def test_extract_ignore_unknown_excludes_words_from_multiple_corpora(self):
		"""
		Test that the domain specificity extractor excludes unknown terms from multiple corpora when the policy is set to ignore unknown terms.
		"""

		corpora = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
		 			os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = SpecificityExtractor(general, ignore_unknown=True)
		vocabulary = linguistic.vocabulary(corpora)
		terms = extractor.extract(corpora)
		self.assertTrue(any( term not in terms for term in vocabulary ))

	def test_extract_not_ignore_unknown_includes_all_words_from_one_corpus(self):
		"""
		Test that the domain specificity extractor includes unknown terms from one corpus when the policy is set not to ignore unknown terms.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = SpecificityExtractor(general, ignore_unknown=False)
		vocabulary = linguistic.vocabulary(corpora)
		terms = extractor.extract(corpora)
		self.assertFalse(any( term not in terms for term in vocabulary ))

	def test_extract_not_ignore_unknown_includes_all_words_from_multiple_corpora(self):
		"""
		Test that the domain specificity extractor includes unknown terms from multiple corpora when the policy is set not to ignore unknown terms.
		"""

		corpora = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
		 			os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = SpecificityExtractor(general, ignore_unknown=False)
		vocabulary = linguistic.vocabulary(corpora)
		terms = extractor.extract(corpora)
		self.assertFalse(any( term not in terms for term in vocabulary ))

	def test_extract_all_multiple_corpora(self):
		"""
		Test that the domain specificity extractor extracts all terms from multiple corpora.
		"""

		corpora = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
		 			os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = SpecificityExtractor(general)
		terms_1 = extractor.extract(corpora[0])
		terms_2 = extractor.extract(corpora[1])
		terms_combined = extractor.extract(corpora)
		self.assertTrue(all( term in terms_combined for term in terms_1 ))
		self.assertTrue(all( term in terms_combined for term in terms_2 ))

	def test_extract_candidates(self):
		"""
		Test that the domain specificity extractor extracts scores for only select candidates if they are given.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = SpecificityExtractor(general)
		terms = extractor.extract(corpora, candidates=[ 'chelsea', 'goal' ])
		self.assertEqual({ 'chelsea', 'goal' }, set(terms.keys()))

	def test_extract_candidates_ignore_unknown(self):
		"""
		Test that the domain specificity extractor extracts scores for select candidates even if they are unknown.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = SpecificityExtractor(general, ignore_unknown=True)

		"""
		Ensure that 'cesc' is an unknown word and therefore missing from the extracted terms.
		"""
		terms = extractor.extract(corpora)
		self.assertFalse('cesc' in terms)

		"""
		Specifically look for the same term.
		"""
		terms = extractor.extract(corpora, candidates=[ 'chelsea', 'goal', 'cesc' ])
		self.assertEqual({ 'chelsea', 'goal', 'cesc' }, set(terms.keys()))

	def test_extract_candidates_ignore_unknown_domain(self):
		"""
		Test that the domain specificity extractor extracts scores for select candidates even if they are unknown in the domain and in the general corpora.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = SpecificityExtractor(general, ignore_unknown=True)

		"""
		Ensure that 'superlongword' is an unknown word and therefore missing from the extracted terms.
		"""
		terms = extractor.extract(corpora)
		self.assertFalse('superlongword' in terms)

		"""
		Specifically look for the same term.
		"""
		terms = extractor.extract(corpora, candidates=[ 'chelsea', 'goal', 'superlongword' ])
		self.assertEqual({ 'chelsea', 'goal', 'superlongword' }, set(terms.keys()))

	def test_extract_candidates_same_scores(self):
		"""
		Test that the domain specificity extractor's scores for known candidates are the same as when candidates are not given.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		extractor = SpecificityExtractor(general)
		candidate_terms = extractor.extract(corpora, candidates=[ 'chelsea', 'goal' ])
		terms = extractor.extract(corpora)
		self.assertEqual(terms['chelsea'], candidate_terms['chelsea'])
		self.assertEqual(terms['goal'], candidate_terms['goal'])

	def test_extract_unknown_above_known(self):
		"""
		Test that the domain specificity extractor ranks unknown words above known words.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		"""
		Ensure that 'cesc' is an unknown word and therefore missing from the extracted terms.
		"""
		extractor = SpecificityExtractor(general, ignore_unknown=True)
		terms = extractor.extract(corpora)
		self.assertFalse('cesc' in terms)

		"""
		Include unknown words and ensure that they rank higher than known words.
		"""
		extractor = SpecificityExtractor(general, ignore_unknown=False)
		terms = extractor.extract(corpora)
		self.assertGreater(terms['cesc'], terms['chelsea'])
		self.assertGreater(terms['cesc'], terms['goal'])

	def test_extract_unknown_popular_above_unknown_unpopular(self):
		"""
		Test that the domain specificity extractor ranks popular unknown words above unpopular unknown words.
		"""

		corpora = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
		general = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'sample-1.json')

		"""
		Ensure that 'cesc' is an unknown word and therefore missing from the extracted terms.
		"""
		extractor = SpecificityExtractor(general, ignore_unknown=True)
		terms = extractor.extract(corpora)
		self.assertFalse('cesc' in terms)
		self.assertFalse('sarri' in terms)

		"""
		Include unknown words and ensure that they rank higher than known words.
		"""
		extractor = SpecificityExtractor(general, ignore_unknown=False)
		terms = extractor.extract(corpora)
		self.assertGreater(terms['sarri'], terms['cesc'])

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
		Test that when ranking unknown words, words that do not appear in the domain get a score of 0.
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
		self.assertEqual(0, unknown_scores['superlongword'])

	def test_rank_unknown_words_probability_zero(self):
		"""
		Test that when ranking unknown words with a probability of zero in the domain, they get a score of 0.
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
		self.assertEqual(0, unknown_scores['superlongword'])

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

		self.assertTrue(all( score > 0 for score in unknown_scores.values() ))

	def test_rank_unknown_words_with_scores(self):
		"""
		Test that when there are scores of known words, the rankings start from the maximum score.
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

		self.assertTrue(all( score > max(scores.values()) for score in unknown_scores.values() ))

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
