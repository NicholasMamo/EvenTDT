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
