"""
Test the functionality of the terms tool.
"""

import json
import os
import re
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
 		  os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

from tools import terms
from ate.application import EFIDF

class TestTerms(unittest.TestCase):
	"""
	Test the functionality of the terms tool.
	"""

	def test_instantiate_efidf_missing_idf(self):
		"""
		Test that when the TF-IDF scheme is not given for the EF-IDF, a SystemExit is raised.
		"""

		self.assertRaises(SystemExit, terms.instantiate, EFIDF)

	def no_test_extract_efidf_with_corpora(self):
		"""
		Test that when the EF-IDF receives corpora, it raises a ValueError.
		"""

		idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
		path = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf', 'LIVMUN.json')
		extractor = terms.instantiate(EFIDF, tfidf=idf)
		self.assertRaises(ValueError, extractor.extract, path)

	def no_test_extract_efidf_results(self):
		"""
		Test that when exctracting terms using EF-IDF, the correct results are returned.
		"""

		idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
		events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
		extractor = terms.instantiate(EFIDF, tfidf=idf, base=2)
		extracted = terms.extract(extractor, files)
		self.assertEqual([ 'offsid', 'alisson', 'foul', 'tackl', 'goalkeep' ],
						 list( term['term'] for term in extracted[:5] ))
		self.assertEqual(9.764345, round(extracted[0]['score'], 6))
		self.assertEqual(8.971401, round(extracted[1]['score'], 6))
		self.assertEqual(7.749988, round(extracted[2]['score'], 6))
		self.assertEqual(7.461810, round(extracted[3]['score'], 6))
		self.assertEqual(7.205842, round(extracted[4]['score'], 6))

	def test_extract_efidf_results_without_base(self):
		"""
		Test that when exctracting terms using EF-IDF without a base, the correct results are returned.
		"""

		idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
		events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
		extractor = terms.instantiate(EFIDF, tfidf=idf)
		print(extractor.base)
		extracted = terms.extract(extractor, files)
		self.assertEqual([ 'offsid', 'alisson', 'foul', 'tackl', 'goalkeep' ],
						 list( term['term'] for term in extracted[:5] ))
		self.assertEqual(19.528690, round(extracted[0]['score'], 6))
		self.assertEqual(16.980971, round(extracted[1]['score'], 6))
		self.assertEqual(15.499975, round(extracted[2]['score'], 6))
		self.assertEqual(14.923619, round(extracted[3]['score'], 6))
		self.assertEqual(13.639141, round(extracted[4]['score'], 6))
