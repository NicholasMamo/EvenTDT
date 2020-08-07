"""
Test the functionality of the correlation tool.
"""

import json
import os
import sys
import unittest

from datetime import datetime

paths = [ os.path.join(os.path.dirname(__file__), '..'),
 		  os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

import correlation
from eventdt.ate.bootstrapping.probability import ChiBootstrapper, PMIBootstrapper
from logger import logger

logger.set_logging_level(logger.LogLevel.ERROR)

class TestCorrelation(unittest.TestCase):
	"""
	Test the functionality of the correlation tool.
	"""

	def test_extract_dict(self):
		"""
		Test that the correlation returns a dictionary of keywords.
		"""

		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
		terms = [ 'first', 'second', 'half', 'underway' ]

		extractor = correlation.create_extractor(PMIBootstrapper)
		c = correlation.extract(extractor, files, terms)
		self.assertEqual(dict, type(c))
		self.assertTrue(all( type(c.get(v)) is dict for v in c ))

	def test_extract_all_keywords(self):
		"""
		Test that the correlation returns all initial terms.
		"""

		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
		terms = [ 'first', 'second', 'half', 'underway' ]

		extractor = correlation.create_extractor(PMIBootstrapper)
		c = correlation.extract(extractor, files, terms)
		self.assertEqual(set(terms), set(c))

	def test_extract_nested_all_keywords(self):
		"""
		Test that the correlation returns all initial terms in the nested dictionaries.
		"""

		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
		terms = [ 'first', 'second', 'half', 'underway' ]

		extractor = correlation.create_extractor(PMIBootstrapper)
		c = correlation.extract(extractor, files, terms)
		self.assertTrue(all( set(terms) == set(v) for v in c.values() ))

	def test_extract_nested_all_keywords(self):
		"""
		Test that the correlation returns all initial terms in the nested dictionaries.
		"""

		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
		terms = [ 'first', 'second', 'half', 'underway' ]

		extractor = correlation.create_extractor(PMIBootstrapper)
		c = correlation.extract(extractor, files, terms)
		self.assertTrue(all( set(terms) == set(v) for v in c.values() ))

	def test_extract_pmi_symmetric(self):
		"""
		Test that the correlation with PMI is symmetric.
		"""

		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
		terms = [ 'first', 'second', 'half', 'underway' ]

		extractor = correlation.create_extractor(PMIBootstrapper)
		c = correlation.extract(extractor, files, terms)
		for t1 in terms:
			for t2 in terms:
				self.assertEqual(c[t1][t2], c[t2][t1])

	def test_extract_chi_symmetric(self):
		"""
		Test that the correlation with CHI is symmetric.
		"""

		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
		terms = [ 'first', 'second', 'half', 'underway' ]

		extractor = correlation.create_extractor(ChiBootstrapper)
		c = correlation.extract(extractor, files, terms)
		for t1 in terms:
			for t2 in terms:
				self.assertEqual(c[t1][t2], c[t2][t1])

	def test_extract_unknown_words(self):
		"""
		Test that the correlation of unknown words is 0.
		"""

		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
		terms = [ 'first', 'second', 'half', 'underway', 'superlongword' ]

		extractor = correlation.create_extractor(ChiBootstrapper)
		c = correlation.extract(extractor, files, terms)
		self.assertTrue(all( c['superlongword'][term] == 0 for term in terms ))

	def test_extract(self):
		"""
		Test that the extraction makes sense.
		"""

		files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
		terms = [ 'first', 'second', 'half', 'underway', 'yellow', 'card' ]

		extractor = correlation.create_extractor(PMIBootstrapper)
		c = correlation.extract(extractor, files, terms)
		self.assertGreater(c['first']['half'], c['yellow']['half'])
		self.assertGreater(c['yellow']['card'], c['first']['card'])
