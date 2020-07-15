"""
Test the functionality of the IDF tool.
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

import idf

class TestIDF(unittest.TestCase):
	"""
	Test the functionality of the IDF tool.
	"""

	def test_construct_all_lines(self):
		"""
		Test that when creating an IDF table, the number of documents is equal to the number of lines.
		"""

		file = 'eventdt/tests/corpora/CRYCHE-100.json'

		"""
		Create an IDF and assert that it has all lines.
		"""
		tfidf = idf.construct(file, remove_retweets=False, stem=True)
		self.assertEqual(100, tfidf.global_scheme.documents)

	def test_construct_no_retweets_fewer_documents(self):
		"""
		Test that when creating an IDF table without retweets, the number of documents is fewer.
		"""

		file = 'eventdt/tests/corpora/CRYCHE-100.json'

		"""
		Create an IDF with retweets and another without retweets.
		"""
		tfidf = idf.construct(file, remove_retweets=False, stem=True)
		tfidf_wo_rt = idf.construct(file, remove_retweets=True, stem=True)

		"""
		Assert that the IDF with retweets has more documents than the one without retweets.
		"""
		self.assertGreater(tfidf.global_scheme.documents, tfidf_wo_rt.global_scheme.documents)

	def test_construct_no_retweets_subset(self):
		"""
		Test that when creating an IDF table without retweets, its terms are a subset of the IDF with retweets.
		"""

		file = 'eventdt/tests/corpora/CRYCHE-100.json'

		"""
		Create an IDF with retweets and another without retweets.
		"""
		tfidf = idf.construct(file, remove_retweets=False, stem=True)
		tfidf_wo_rt = idf.construct(file, remove_retweets=True, stem=True)

		"""
		Assert that all of the terms in the IDF without retweets are in the IDF with retweets.
		"""
		self.assertTrue(all( term in tfidf.global_scheme.idf for term in tfidf_wo_rt.global_scheme.idf ))

		"""
		Assert that the DF of all terms in the IDF without retweets are less than or equal to the DF of the IDF with retweets.
		"""
		self.assertTrue(all( tfidf_wo_rt.global_scheme.idf[term] <= tfidf.global_scheme.idf[term] for term in tfidf_wo_rt.global_scheme.idf ))
