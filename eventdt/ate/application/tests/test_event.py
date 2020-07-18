"""
Test the functionality of the event-based ATE approaches.
"""

import json
import math
import os
import string
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..') ,
		  os.path.join(os.path.dirname(__file__), '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

from objects.exportable import Exportable
import event
from nlp.term_weighting import TFIDF

class TestEvent(unittest.TestCase):
	"""
	Test the functionality of the event-based ATE approaches.
	"""

	def test_ef_one_timeline(self):
		"""
		Test that when providing one timeline, the algorithm extracts terms only from it.
		"""

		path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')
		extractor = event.EF()
		self.assertTrue(extractor.extract(path))

	def test_ef_multiple_timeline(self):
		"""
		Test that when providing multiple timelines, the algorithm extracts terms from all of them.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json') ]
		extractor = event.EF()
		terms = extractor.extract(paths)
		self.assertTrue(terms)
		self.assertTrue(all( term in terms for term in extractor.extract(paths[0]) ))
		self.assertTrue(all( term in terms for term in extractor.extract(paths[1]) ))

	def test_ef_lower_limit(self):
		"""
		Test that the minimum event frequency is 1, not 0.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json') ]
		extractor = event.EF()
		terms = extractor.extract(paths)
		self.assertEqual(1, min(terms.values()))

	def test_ef_max_limit(self):
		"""
		Test that the maximum event frequency is equivalent to the number of timelines provided.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json') ]
		extractor = event.EF()
		terms = extractor.extract(paths)
		self.assertEqual(len(paths), max(terms.values()))

	def test_ef_integers(self):
		"""
		Test that the event frequency is always an integer.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json') ]
		extractor = event.EF()
		terms = extractor.extract(paths)
		self.assertTrue(all( type(value) == int for value in terms.values() ))

	def test_ef_all_terms(self):
		"""
		Test that the event frequency includes all breaking terms.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json') ]

		"""
		Calculate the event frequency.
		"""
		extractor = event.EF()
		ef_terms = extractor.extract(path)

		"""
		Extract all terms from the timelines.
		"""
		all_terms = set()
		for timeline in paths:
			with open(timeline, 'r') as f:
				data = json.loads(''.join(f.readlines()))

				"""
				Decode the timeline and extract all the terms in it.
				"""
				timeline = Exportable.decode(data)['timeline']
				terms = set( term for node in timeline.nodes
								  for topic in node.topics
								  for term in topic.dimensions )
				all_terms = all_terms.union(terms)

		"""
		Assert that all terms are in the event frequency.
		"""
		self.assertEqual(all_terms, set(ef_terms))

	def test_ef_all_terms(self):
		"""
		Test that the event frequency includes all breaking terms.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		extractor = event.EF()
		ef_terms = extractor.extract(paths)
		extractor = event.LogEF()
		log_ef_terms = extractor.extract(paths)
		self.assertEqual(ef_terms.keys(), log_ef_terms.keys())

	def test_ef_extract_candidates(self):
		"""
		Test that the EF extractor extracts scores for only select candidates if they are given.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		extractor = event.EF()
		terms = extractor.extract(paths, candidates=[ 'chelsea', 'goal' ])
		self.assertEqual({ 'chelsea', 'goal' }, set(terms.keys()))

	def test_ef_extract_candidates_same_scores(self):
		"""
		Test that the EF extractor's scores for known candidates are the same as when candidates are not known.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		extractor = event.EF()
		candidate_terms = extractor.extract(paths, candidates=[ 'chelsea', 'goal' ])
		terms = extractor.extract(paths)
		self.assertEqual(terms['chelsea'], candidate_terms['chelsea'])
		self.assertEqual(terms['goal'], candidate_terms['goal'])

	def test_ef_extract_candidates_unknown_word(self):
		"""
		Test that the EF extractor's score for an unknown word is 0.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		extractor = event.EF()
		terms = extractor.extract(paths, candidates=[ 'superlongword' ])
		self.assertEqual({ 'superlongword': 0 }, terms)

	def test_log_ef_lower_limit(self):
		"""
		Test that the minimum logarithmic event frequency is 0, not 1.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]
		extractor = event.LogEF()
		terms = extractor.extract(paths)
		self.assertEqual(0, min(terms.values()))

	def test_log_ef_max_limit(self):
		"""
		Test that the maximum logarithmic event frequency is equivalent to the logarithm of the number of timelines provided.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]
		extractor = event.LogEF()
		terms = extractor.extract(paths)
		self.assertEqual(math.log(len(paths), 2), max(terms.values()))

	def test_log_ef_base(self):
		"""
		Test that the logarithmic event frequency is just the event frequency  with a logarithm.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]
		extractor = event.EF()
		ef_terms = extractor.extract(paths)

		extractor = event.LogEF(base=2)
		log_ef_terms = extractor.extract(paths)
		self.assertTrue(all( math.log(ef_terms[term], 2) == log_ef_terms[term] for term in ef_terms ))

		extractor = event.LogEF(base=10)
		log_ef_terms = extractor.extract(paths)
		self.assertTrue(all( math.log(ef_terms[term], 10) == log_ef_terms[term] for term in ef_terms ))

	def test_log_ef_extract_candidates(self):
		"""
		Test that the logarithmic EF extractor extracts scores for only select candidates if they are given.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		extractor = event.LogEF()
		terms = extractor.extract(paths, candidates=[ 'chelsea', 'goal' ])
		self.assertEqual({ 'chelsea', 'goal' }, set(terms.keys()))

	def test_log_ef_extract_candidates_same_scores(self):
		"""
		Test that the logarithmic EF extractor's scores for known candidates are the same as when candidates are not known.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		extractor = event.LogEF()
		candidate_terms = extractor.extract(paths, candidates=[ 'chelsea', 'goal' ])
		terms = extractor.extract(paths)
		self.assertEqual(terms['chelsea'], candidate_terms['chelsea'])
		self.assertEqual(terms['goal'], candidate_terms['goal'])

	def test_log_ef_extract_candidates_unknown_word(self):
		"""
		Test that the logarithmic EF extractor's score for an unknown word is 0.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		extractor = event.LogEF()
		terms = extractor.extract(paths, candidates=[ 'superlongword' ])
		self.assertEqual({ 'superlongword': 0 }, terms)

	def test_efidf(self):
		"""
		Test that the EF-IDF scores are assigned correctly.
		"""

		idf_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')
		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		"""
		Calculate the EF-IDF manually.
		"""
		extractor = event.EF()
		ef_terms = extractor.extract(paths)
		with open(idf_path, 'r') as f:
			idf = Exportable.decode(json.loads(''.join(f.readlines())))['tfidf']

		"""
		Ensure that the scores line up.
		"""
		extractor = event.EFIDF(idf)
		terms = extractor.extract(paths)
		self.assertTrue(all( terms[term] == ef_terms[term] * idf.create([ term ]).dimensions[term]
		 					 for term in ef_terms ))

	def test_efidf_log(self):
		"""
		Test that when a base is given, the EF-IDF scores are based on the logarithmic event frequency.
		"""

		idf_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')
		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		"""
		Calculate the EF-IDF manually.
		"""
		extractor = event.LogEF(10)
		ef_terms = extractor.extract(paths)
		with open(idf_path, 'r') as f:
			idf = Exportable.decode(json.loads(''.join(f.readlines())))['tfidf']

		"""
		Ensure that the scores line up.
		"""
		extractor = event.EFIDF(idf, base=10)
		terms = extractor.extract(paths)
		self.assertTrue(all( terms[term] == ef_terms[term] * idf.create([ term ]).dimensions[term]
							 for term in ef_terms ))

	def test_efidf_all_terms(self):
		"""
		Test that the EF-IDF scores include all terms.
		"""

		idf_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')
		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		"""
		Calculate the EF to get a list of terms.
		"""
		extractor = event.EF()
		ef_terms = extractor.extract(paths)
		with open(idf_path, 'r') as f:
			idf = Exportable.decode(json.loads(''.join(f.readlines())))['tfidf']

		"""
		Calculate the EF-IDF and ensure that all terms are present.
		"""
		extractor = event.EFIDF(idf)
		terms = extractor.extract(paths)
		self.assertEqual(ef_terms.keys(), terms.keys())

	def test_efidf_extract_candidates(self):
		"""
		Test that the EF-IDF extractor extracts scores for only select candidates if they are given.
		"""

		idf_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')
		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		with open(idf_path, 'r') as f:
			idf = Exportable.decode(json.loads(''.join(f.readlines())))['tfidf']

		extractor = event.EFIDF(idf)
		terms = extractor.extract(paths, candidates=[ 'chelsea', 'goal' ])
		self.assertEqual({ 'chelsea', 'goal' }, set(terms.keys()))

	def test_efidf_extract_candidates_same_scores(self):
		"""
		Test that the EF-IDF extractor's scores for known candidates are the same as when candidates are not known.
		"""

		idf_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')
		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		with open(idf_path, 'r') as f:
			idf = Exportable.decode(json.loads(''.join(f.readlines())))['tfidf']

		extractor = event.EFIDF(idf)
		candidate_terms = extractor.extract(paths, candidates=[ 'chelsea', 'goal' ])
		terms = extractor.extract(paths)
		self.assertEqual(terms['chelsea'], candidate_terms['chelsea'])
		self.assertEqual(terms['goal'], candidate_terms['goal'])

	def test_efidf_extract_candidates_unknown_word(self):
		"""
		Test that the EF-IDF extractor's score for an unknown word is 0.
		"""

		idf_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')
		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		with open(idf_path, 'r') as f:
			idf = Exportable.decode(json.loads(''.join(f.readlines())))['tfidf']

		extractor = event.EFIDF(idf)
		terms = extractor.extract(paths, candidates=[ 'superlongword' ])
		self.assertEqual({ 'superlongword': 0 }, terms)

	def test_efidf_log_extract_candidates(self):
		"""
		Test that the logarithmic EF-IDF extractor extracts scores for only select candidates if they are given.
		"""

		idf_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')
		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		with open(idf_path, 'r') as f:
			idf = Exportable.decode(json.loads(''.join(f.readlines())))['tfidf']

		extractor = event.EFIDF(idf)
		terms = extractor.extract(paths, candidates=[ 'chelsea', 'goal' ])
		self.assertEqual({ 'chelsea', 'goal' }, set(terms.keys()))

	def test_efidf_log_extract_candidates_same_scores(self):
		"""
		Test that the logarithmic EF-IDF extractor's scores for known candidates are the same as when candidates are not known.
		"""

		idf_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')
		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		with open(idf_path, 'r') as f:
			idf = Exportable.decode(json.loads(''.join(f.readlines())))['tfidf']

		extractor = event.EFIDF(idf, base=2)
		candidate_terms = extractor.extract(paths, candidates=[ 'chelsea', 'goal' ])
		terms = extractor.extract(paths)
		self.assertEqual(terms['chelsea'], candidate_terms['chelsea'])
		self.assertEqual(terms['goal'], candidate_terms['goal'])

	def test_efidf_log_extract_candidates_unknown_word(self):
		"""
		Test that the logarithmic EF-IDF extractor's score for an unknown word is 0.
		"""

		idf_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf.json')
		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'timelines', 'MUNARS.json') ]

		with open(idf_path, 'r') as f:
			idf = Exportable.decode(json.loads(''.join(f.readlines())))['tfidf']

		extractor = event.EFIDF(idf, base=2)
		terms = extractor.extract(paths, candidates=[ 'superlongword' ])
		self.assertEqual({ 'superlongword': 0 }, terms)

	def test_variability_base(self):
		"""
		Test that the variability score is applied before the inverse.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Calculate the variability.
		"""
		extractor = event.Variability(base=2)
		variability_2 = extractor.extract(idfs)
		extractor = event.Variability(base=10)
		variability_10 = extractor.extract(idfs)
		self.assertGreater(variability_10['yellow'], variability_2['liverpool'])

	def test_variability_consistent_word(self):
		"""
		Test that the variability score of a consistent word is higher than a specific word.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Calculate the variability.
		"""
		extractor = event.Variability()
		self.assertGreater(extractor.extract(idfs)['yellow'], extractor.extract(idfs)['liverpool'])

	def test_variability_chi_less_1(self):
		"""
		Test that when the variability is less than 1, the variability is not negative.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'chi-less1-1.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'chi-less1-2.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Variability()

		"""
		Confirm that the chi is between 0 and 1.
		"""
		table = extractor._contingency_table('fastest', idfs[0], [ idfs[1] ])
		self.assertLess(0, extractor._chi(table))
		self.assertLess(extractor._chi(table), 1)
		table = extractor._contingency_table('fastest', idfs[1], [ idfs[0] ])
		self.assertLess(0, extractor._chi(table))
		self.assertLess(extractor._chi(table), 1)

		"""
		Confirm that the variability is between 0 and 1.
		"""
		self.assertGreater(extractor.extract(idfs, candidates=[ 'fastest' ])['fastest'], 0)
		self.assertLess(extractor.extract(idfs, candidates=[ 'fastest' ])['fastest'], 1)

	def test_variability_chi_equal_1(self):
		"""
		Test that when the variability is equal to 1, the variability is 1.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'chi-equal1-1.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'chi-equal1-2.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Variability()

		"""
		Confirm that the chi is 1.
		"""
		table = extractor._contingency_table('fastest', idfs[0], [ idfs[1] ])
		self.assertEqual(0, extractor._chi(table))
		table = extractor._contingency_table('fastest', idfs[1], [ idfs[0] ])
		self.assertEqual(0, extractor._chi(table))

		"""
		Confirm that the variability is 1.
		"""
		self.assertEqual(1, extractor.extract(idfs, candidates=[ 'fastest' ])['fastest'])

	def test_variability_specific_words(self):
		"""
		Test that the variability score of two specific words prefers those that appear in multiple corpora.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Calculate the variability.
		"""
		extractor = event.Variability()
		self.assertGreater(extractor.extract(idfs)['manchest'], extractor.extract(idfs)['chelsea'])

	def test_variability_changing_corpora(self):
		"""
		Test that when changing the corpora, the variability changes.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Calculate the variability.
		"""
		extractor = event.Variability()
		self.assertGreater(extractor.extract(idfs[:2])['liverpool'], extractor.extract(idfs)['liverpool'])

	def test_variability_extract_candidates(self):
		"""
		Test that the variability extractor extracts scores for only select candidates if they are given.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Variability()
		terms = extractor.extract(idfs, candidates=[ 'chelsea', 'goal' ])
		self.assertEqual({ 'chelsea', 'goal' }, set(terms.keys()))

	def test_variability_extract_candidates_same_scores(self):
		"""
		Test that the variability extractor's scores for known candidates are the same as when candidates are not known.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Variability()
		candidate_terms = extractor.extract(idfs, candidates=[ 'chelsea', 'goal' ])
		terms = extractor.extract(idfs)
		self.assertEqual(terms['chelsea'], candidate_terms['chelsea'])
		self.assertEqual(terms['goal'], candidate_terms['goal'])

	def test_variability_extract_candidates_unknown_word(self):
		"""
		Test that the variability extractor's score for an unknown word is 1 because it 'appears' equally across corpora.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Variability()
		terms = extractor.extract(idfs, candidates=[ 'superlongword' ])
		self.assertEqual({ 'superlongword': 1 }, terms)

	def test_variability_vocabulary_all_one_corpus(self):
		"""
		Test that the vocabulary of one corpus includes all terms.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Variability()
		self.assertEqual(set(idfs[0].global_scheme.idf.keys()), set(extractor._vocabulary(idfs)))

	def test_variability_vocabulary_all_multiple_corpora(self):
		"""
		Test that the vocabulary of multiple corpora includes all terms.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Variability()
		vocabulary = extractor._vocabulary(idfs)
		self.assertTrue(all( term in vocabulary for term in idfs[0].global_scheme.idf ))
		self.assertTrue(all( term in vocabulary for term in idfs[1].global_scheme.idf ))

	def test_variability_vocabulary_unique(self):
		"""
		Test that the vocabulary does not include duplicates.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Variability()
		vocabulary = extractor._vocabulary(idfs)
		self.assertEqual(len(set(vocabulary)), len(vocabulary))

	def test_variability_contingency_table_total(self):
		"""
		Test that the variability contingency table sums up to the total number of documents in all IDFs.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Calculate the total number of documents in all the IDFs.
		"""
		total = sum([ idf.global_scheme.documents for idf in idfs ])

		extractor = event.Variability()

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		for idf in idfs:
			comparison = [ other for other in idfs if other is not idf ]
			table = extractor._contingency_table('liverpool', idf, comparison)
			self.assertEqual(total, sum(table))

	def test_variability_contingency_table_four_cells(self):
		"""
		Test that the variability contingency table has four cells.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Calculate the total number of documents in all the IDFs.
		"""
		total = sum([ idf.global_scheme.documents for idf in idfs ])

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		extractor = event.Variability()
		for idf in idfs:
			comparison = [ other for other in idfs if other is not idf ]
			table = extractor._contingency_table('liverpool', idf, comparison)
			self.assertEqual(4, len(table))

	def test_variability_contingency_table_integer_cells(self):
		"""
		Test that the variability contingency table is made up of integers.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Calculate the total number of documents in all the IDFs.
		"""
		total = sum([ idf.global_scheme.documents for idf in idfs ])

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		extractor = event.Variability()
		for idf in idfs:
			comparison = [ other for other in idfs if other is not idf ]
			table = extractor._contingency_table('liverpool', idf, comparison)
			self.assertTrue(all(type(cell) is int for cell in table))

	def test_variability_contingency_table_positive_cells(self):
		"""
		Test that the variability contingency table is made up of positive numbers.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Calculate the total number of documents in all the IDFs.
		"""
		total = sum([ idf.global_scheme.documents for idf in idfs ])

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		extractor = event.Variability()
		for idf in idfs:
			comparison = [ other for other in idfs if other is not idf ]
			table = extractor._contingency_table('zaha', idf, comparison)
			self.assertTrue(all(cell >= 0 for cell in table))

	def test_variability_contingency_table_event_total(self):
		"""
		Test that the first variability contingency table row sums up to the total number of documents in the event IDF.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		extractor = event.Variability()
		for idf in idfs:
			comparison = [ other for other in idfs if other is not idf ]
			(A, B, C, D) = extractor._contingency_table('liverpool', idf, comparison)
			self.assertEqual(idf.global_scheme.documents, A + B)

	def test_variability_contingency_table_comparison_total(self):
		"""
		Test that the second variability contingency table row sums up to the total number of documents in the comparison IDFs.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		extractor = event.Variability()
		for idf in idfs:
			comparison = [ other for other in idfs if other is not idf ]
			(A, B, C, D) = extractor._contingency_table('liverpool', idf, comparison)
			self.assertEqual(sum([ idf.global_scheme.documents for idf in comparison ]), C + D)

	def test_variability_contingency_table_unknown_event_word(self):
		"""
		Test that when a word is unknown in an event, the first cell is 0.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		extractor = event.Variability()
		(A, B, C, D) = extractor._contingency_table('merten', idfs[0], idfs[1:])
		self.assertEqual(0, A)

	def test_variability_contingency_table_unknown_event_word(self):
		"""
		Test that when a word is unknown in an event, the first cell is 0.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		extractor = event.Variability()
		(A, B, C, D) = extractor._contingency_table('milik', idfs[0], idfs[1:])
		self.assertEqual(0, A)
		self.assertEqual(idfs[0].global_scheme.documents, B)

	def test_variability_contingency_table_unique_event_word(self):
		"""
		Test that when a word appears in only one event, the comparison events' cells sum up to zero.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		extractor = event.Variability()
		(A, B, C, D) = extractor._contingency_table('wickham', idfs[0], idfs[1:])
		self.assertEqual(0, C)
		self.assertEqual(sum([ idf.global_scheme.documents for idf in idfs[1:] ]), D)

	def test_variability_contingency_table_correct_counts(self):
		"""
		Test that the variability contingency table counts are correct.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		term = 'liverpool'
		extractor = event.Variability()
		(A, B, C, D) = extractor._contingency_table(term, idfs[0], idfs[1:])
		self.assertEqual(idfs[0].global_scheme.idf[term], A)
		self.assertEqual(sum([ idf.global_scheme.idf[term] for idf in idfs[1:] ]), C)

	def test_variablity_chi(self):
		"""
		Test the chi-square calculation.
		"""

		extractor = event.Variability()

		table = (600, 200, 300, 1000)
		self.assertEqual(545.1923, round(extractor._chi(table), 4))

		table = (30, 20, 331, 3218)
		self.assertEqual(140.2925, round(extractor._chi(table), 4))

	def test_variablity_chi_empty(self):
		"""
		Test that the chi-square statistic of an empty table is 0.
		"""

		extractor = event.Variability()

		table = (0, 0, 0, 0)
		self.assertEqual(0, extractor._chi(table))

	def test_variablity_chi_empty_combinations(self):
		"""
		Test that the chi-square statistic of a table that is not empty, except for a few combinations, is 0.
		"""

		extractor = event.Variability()

		table = (0, 1, 0, 1) # A + C = 0
		self.assertEqual(0, extractor._chi(table))

		table = (1, 0, 1, 0) # B + D = 0
		self.assertEqual(0, extractor._chi(table))

		table = (0, 0, 1, 1) # A + B = 0
		self.assertEqual(0, extractor._chi(table))

		table = (1, 1, 0, 0) # C + D = 0
		self.assertEqual(0, extractor._chi(table))

		table = (1, 0, 0, 1) # B + C = 0
		self.assertLess(0, extractor._chi(table))

		table = (0, 1, 1, 0) # A + D = 0
		self.assertLess(0, extractor._chi(table))

	def test_entropy_vocabulary_all_one_corpus(self):
		"""
		Test that the vocabulary of one corpus includes all terms.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Entropy()
		self.assertEqual(set(idfs[0].global_scheme.idf.keys()), set(extractor._vocabulary(idfs)))

	def test_entropy_vocabulary_all_multiple_corpora(self):
		"""
		Test that the vocabulary of multiple corpora includes all terms.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Entropy()
		vocabulary = extractor._vocabulary(idfs)
		self.assertTrue(all( term in vocabulary for term in idfs[0].global_scheme.idf ))
		self.assertTrue(all( term in vocabulary for term in idfs[1].global_scheme.idf ))

	def test_entropy_vocabulary_unique(self):
		"""
		Test that the vocabulary does not include duplicates.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Entropy()
		vocabulary = extractor._vocabulary(idfs)
		self.assertEqual(len(set(vocabulary)), len(vocabulary))

	def test_entropy_total_no_idfs(self):
		"""
		Test that when calculating the total mentions of a term without any IDFs, the total is 0.
		"""

		extractor = event.Entropy()
		self.assertEqual(0, extractor._total([ ], 'yellow'))

	def test_entropy_total_one_idf(self):
		"""
		Test that when calculating the total mentions of a term with one IDF, the total is equal to the number of times the term appears in that event.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Entropy()
		vocabulary = extractor._vocabulary(idfs)
		self.assertTrue(all( extractor._total(idfs, term) == idfs[0].global_scheme.idf.get(term, 0)
							 for term in vocabulary ))

	def test_entropy_total_multiple_idfs(self):
		"""
		Test that when calculating the total mentions of a term with several IDFs, the total is equal to the number of times the term appears in those events.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Entropy()
		vocabulary = extractor._vocabulary(idfs)
		for term in vocabulary:
			total = 0
			for idf in idfs:
				total += idf.global_scheme.idf.get(term, 0)

			self.assertEqual(extractor._total(idfs, term), total)

	def test_entropy_total_unknown_word(self):
		"""
		Test that the total mentions of an unknown term is zero.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'CRYCHE.json'),
		 		  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVNAP.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'LIVMUN.json'),
				  os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'corpora', 'idf', 'MUNARS.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Entropy()
		self.assertTrue(not any( 'superlongword' in idf.global_scheme.idf for idf in idfs ))
		self.assertEqual(0, extractor._total(idfs, 'superlongword'))
