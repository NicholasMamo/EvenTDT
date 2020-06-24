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

		path = os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json')
		extractor = event.EF()
		self.assertTrue(extractor.extract(path))

	def test_ef_multiple_timeline(self):
		"""
		Test that when providing multiple timelines, the algorithm extracts terms from all of them.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json') ]
		extractor = event.EF()
		terms = extractor.extract(paths)
		self.assertTrue(terms)
		self.assertTrue(all( term in terms for term in extractor.extract(paths[0]) ))
		self.assertTrue(all( term in terms for term in extractor.extract(paths[1]) ))

	def test_ef_lower_limit(self):
		"""
		Test that the minimum event frequency is 1, not 0.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json') ]
		extractor = event.EF()
		terms = extractor.extract(paths)
		self.assertEqual(1, min(terms.values()))

	def test_ef_max_limit(self):
		"""
		Test that the maximum event frequency is equivalent to the number of timelines provided.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json') ]
		extractor = event.EF()
		terms = extractor.extract(paths)
		self.assertEqual(len(paths), max(terms.values()))

	def test_ef_integers(self):
		"""
		Test that the event frequency is always an integer.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json') ]
		extractor = event.EF()
		terms = extractor.extract(paths)
		self.assertTrue(all( type(value) == int for value in terms.values() ))

	def test_ef_all_terms(self):
		"""
		Test that the event frequency includes all breaking terms.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json') ]

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

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]

		extractor = event.EF()
		ef_terms = extractor.extract(paths)
		extractor = event.LogEF()
		log_ef_terms = extractor.extract(paths)
		self.assertEqual(ef_terms.keys(), log_ef_terms.keys())

	def test_ef_extract_candidates(self):
		"""
		Test that the EF extractor extracts scores for only select candidates if they are given.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]

		extractor = event.EF()
		terms = extractor.extract(paths, candidates=[ 'chelsea', 'goal' ])
		self.assertEqual({ 'chelsea', 'goal' }, set(terms.keys()))

	def test_ef_extract_candidates_same_scores(self):
		"""
		Test that the EF extractor's scores for known candidates are the same as when candidates are not known.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]

		extractor = event.EF()
		candidate_terms = extractor.extract(paths, candidates=[ 'chelsea', 'goal' ])
		terms = extractor.extract(paths)
		self.assertEqual(terms['chelsea'], candidate_terms['chelsea'])
		self.assertEqual(terms['goal'], candidate_terms['goal'])

	def test_ef_extract_candidates_unknown_word(self):
		"""
		Test that the EF extractor's score for an unknown word is 0.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]

		extractor = event.EF()
		terms = extractor.extract(paths, candidates=[ 'superlongword' ])
		self.assertEqual({ 'superlongword': 0 }, terms)

	def test_log_ef_lower_limit(self):
		"""
		Test that the minimum logarithmic event frequency is 0, not 1.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]
		extractor = event.LogEF()
		terms = extractor.extract(paths)
		self.assertEqual(0, min(terms.values()))

	def test_log_ef_max_limit(self):
		"""
		Test that the maximum logarithmic event frequency is equivalent to the logarithm of the number of timelines provided.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]
		extractor = event.LogEF()
		terms = extractor.extract(paths)
		self.assertEqual(math.log(len(paths), 2), max(terms.values()))

	def test_log_ef_base(self):
		"""
		Test that the logarithmic event frequency is just the event frequency  with a logarithm.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]
		extractor = event.EF()
		ef_terms = extractor.extract(paths)

		extractor = event.LogEF(base=2)
		log_ef_terms = extractor.extract(paths)
		self.assertTrue(all( math.log(ef_terms[term], 2) == log_ef_terms[term] for term in ef_terms ))

		extractor = event.LogEF(base=10)
		log_ef_terms = extractor.extract(paths)
		self.assertTrue(all( math.log(ef_terms[term], 10) == log_ef_terms[term] for term in ef_terms ))

	def test_efidf(self):
		"""
		Test that the EF-IDF scores are assigned correctly.
		"""

		idf_path = os.path.join(os.path.dirname(__file__), 'corpora', 'idf.json')
		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]

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

		idf_path = os.path.join(os.path.dirname(__file__), 'corpora', 'idf.json')
		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]

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

		idf_path = os.path.join(os.path.dirname(__file__), 'corpora', 'idf.json')
		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]

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

	def test_variability_base(self):
		"""
		Test that the variability score is applied before the inverse.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json') ]
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

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Calculate the variability.
		"""
		extractor = event.Variability()
		self.assertGreater(extractor.extract(idfs)['yellow'], extractor.extract(idfs)['liverpool'])

	def test_variability_specific_words(self):
		"""
		Test that the variability score of two specific words prefers those that appear in multiple corpora.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json') ]
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

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Calculate the variability.
		"""
		extractor = event.Variability()
		self.assertGreater(extractor.extract(idfs[:2])['liverpool'], extractor.extract(idfs)['liverpool'])

	def test_vocabulary_all_one_corpus(self):
		"""
		Test that the vocabulary of one corpus includes all terms.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Variability()
		self.assertEqual(set(idfs[0].global_scheme.idf.keys()), set(extractor._vocabulary(idfs)))

	def test_vocabulary_all_multiple_corpora(self):
		"""
		Test that the vocabulary of multiple corpora includes all terms.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		extractor = event.Variability()
		vocabulary = extractor._vocabulary(idfs)
		self.assertTrue(all( term in vocabulary for term in idfs[0].global_scheme.idf ))
		self.assertTrue(all( term in vocabulary for term in idfs[1].global_scheme.idf ))

	def test_vocabulary_unique(self):
		"""
		Test that the vocabulary does not include duplicates.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json') ]
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

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json') ]
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
			table = extractor._variability_contingency_table('liverpool', idf, comparison)
			self.assertEqual(total, sum(table))

	def test_variability_contingency_table_four_cells(self):
		"""
		Test that the variability contingency table has four cells.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json') ]
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
			table = extractor._variability_contingency_table('liverpool', idf, comparison)
			self.assertEqual(4, len(table))

	def test_variability_contingency_table_integer_cells(self):
		"""
		Test that the variability contingency table is made up of integers.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json') ]
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
			table = extractor._variability_contingency_table('liverpool', idf, comparison)
			self.assertTrue(all(type(cell) is int for cell in table))

	def test_variability_contingency_table_positive_cells(self):
		"""
		Test that the variability contingency table is made up of positive numbers.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json') ]
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
			table = extractor._variability_contingency_table('zaha', idf, comparison)
			self.assertTrue(all(cell >= 0 for cell in table))

	def test_variability_contingency_table_event_total(self):
		"""
		Test that the first variability contingency table row sums up to the total number of documents in the event IDF.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json') ]
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
			(A, B, C, D) = extractor._variability_contingency_table('liverpool', idf, comparison)
			self.assertEqual(idf.global_scheme.documents, A + B)

	def test_variability_contingency_table_comparison_total(self):
		"""
		Test that the second variability contingency table row sums up to the total number of documents in the comparison IDFs.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json') ]
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
			(A, B, C, D) = extractor._variability_contingency_table('liverpool', idf, comparison)
			self.assertEqual(sum([ idf.global_scheme.documents for idf in comparison ]), C + D)

	def test_variability_contingency_table_unknown_event_word(self):
		"""
		Test that when a word is unknown in an event, the first cell is 0.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		extractor = event.Variability()
		(A, B, C, D) = extractor._variability_contingency_table('merten', idfs[0], idfs[1:])
		self.assertEqual(0, A)

	def test_variability_contingency_table_unknown_event_word(self):
		"""
		Test that when a word is unknown in an event, the first cell is 0.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		extractor = event.Variability()
		(A, B, C, D) = extractor._variability_contingency_table('milik', idfs[0], idfs[1:])
		self.assertEqual(0, A)
		self.assertEqual(idfs[0].global_scheme.documents, B)

	def test_variability_contingency_table_unique_event_word(self):
		"""
		Test that when a word appears in only one event, the comparison events' cells sum up to zero.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		extractor = event.Variability()
		(A, B, C, D) = extractor._variability_contingency_table('wickham', idfs[0], idfs[1:])
		self.assertEqual(0, C)
		self.assertEqual(sum([ idf.global_scheme.documents for idf in idfs[1:] ]), D)

	def test_variability_contingency_table_correct_counts(self):
		"""
		Test that the variability contingency table counts are correct.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_idf.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_idf.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_idf.json') ]
		idfs = [ ]
		for path in paths:
			with open(path, 'r') as f:
				idfs.append(Exportable.decode(json.loads(''.join(f.readlines())))['tfidf'])

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		term = 'liverpool'
		extractor = event.Variability()
		(A, B, C, D) = extractor._variability_contingency_table(term, idfs[0], idfs[1:])
		self.assertEqual(idfs[0].global_scheme.idf[term], A)
		self.assertEqual(sum([ idf.global_scheme.idf[term] for idf in idfs[1:] ]), C)