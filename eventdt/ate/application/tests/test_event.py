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

class TestEvent(unittest.TestCase):
	"""
	Test the functionality of the event-based ATE approaches.
	"""

	def test_ef_one_timeline(self):
		"""
		Test that when providing one timeline, the algorithm extracts terms only from it.
		"""

		path = os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json')
		self.assertTrue(event.EF(path))

	def test_ef_multiple_timeline(self):
		"""
		Test that when providing multiple timelines, the algorithm extracts terms from all of them.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json') ]
		ef = event.EF(paths)
		self.assertTrue(ef)
		self.assertTrue(all( term in ef for term in event.EF(paths[0]) ))
		self.assertTrue(all( term in ef for term in event.EF(paths[1]) ))

	def test_ef_lower_limit(self):
		"""
		Test that the minimum event frequency is 1, not 0.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json') ]
		ef = event.EF(paths)
		self.assertEqual(1, min(ef.values()))

	def test_ef_max_limit(self):
		"""
		Test that the maximum event frequency is equivalent to the number of timelines provided.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json') ]
		ef = event.EF(paths)
		self.assertEqual(len(paths), max(ef.values()))

	def test_ef_integers(self):
		"""
		Test that the event frequency is always an integer.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json') ]
		ef = event.EF(paths)
		self.assertTrue(all( type(value) == int for value in ef.values() ))

	def test_ef_all_terms(self):
		"""
		Test that the event frequency includes all breaking terms.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json') ]

		"""
		Calculate the event frequency.
		"""
		ef = event.EF(paths)

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
		self.assertEqual(all_terms, set(ef))

	def test_ef_all_terms(self):
		"""
		Test that the event frequency includes all breaking terms.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]

		self.assertEqual(event.EF(paths).keys(), event.logEF(paths).keys())

	def test_log_ef_lower_limit(self):
		"""
		Test that the minimum logarithmic event frequency is 0, not 1.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]
		ef = event.logEF(paths)
		self.assertEqual(0, min(ef.values()))

	def test_log_ef_max_limit(self):
		"""
		Test that the maximum logarithmic event frequency is equivalent to the logarithm of the number of timelines provided.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]
		ef = event.logEF(paths)
		self.assertEqual(math.log(len(paths), 2), max(ef.values()))

	def test_log_ef_base(self):
		"""
		Test that the logarithmic event frequency is just the event frequency  with a logarithm.
		"""

		paths = [ os.path.join(os.path.dirname(__file__), 'corpora', 'CRYCHE_FUL.json'),
		 		  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVNAP_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'LIVMUN_FUL.json'),
				  os.path.join(os.path.dirname(__file__), 'corpora', 'MUNARS_FUL.json') ]
		ef = event.EF(paths)

		logef = event.logEF(paths, base=2)
		self.assertTrue(all( math.log(ef[term], 2) == logef[term] for term in ef ))

		logef = event.logEF(paths, base=10)
		self.assertTrue(all( math.log(ef[term], 10) == logef[term] for term in ef ))

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
		ef = event.EF(paths)
		with open(idf_path, 'r') as f:
			idf = Exportable.decode(json.loads(''.join(f.readlines())))['tfidf']

		"""
		Ensure that the scores line up.
		"""
		efidf = event.EFIDF(paths, idf)
		self.assertTrue(all( efidf[term] == ef[term] * idf.create([ term ]).dimensions[term]
		 					 for term in efidf ))

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
 		ef = event.logEF(paths, 10)
 		with open(idf_path, 'r') as f:
 			idf = Exportable.decode(json.loads(''.join(f.readlines())))['tfidf']

 		"""
 		Ensure that the scores line up.
 		"""
 		efidf = event.EFIDF(paths, idf, base=10)
 		self.assertTrue(all( efidf[term] == ef[term] * idf.create([ term ]).dimensions[term]
 		 					 for term in efidf ))

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
		ef = event.EF(paths)
		with open(idf_path, 'r') as f:
			idf = Exportable.decode(json.loads(''.join(f.readlines())))['tfidf']

		"""
		Calculate the EF-IDF and ensure that all terms are present.
		"""
		efidf = event.EFIDF(paths, idf)
		self.assertEqual(ef.keys(), efidf.keys())

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

		"""
		Assert that the total number of documents in each contingency table sums up to the total.
		"""
		for idf in idfs:
			comparison = [ other for other in idfs if other is not idf ]
			table = event._variability_contingency_table('liverpool', idf, comparison)
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
		for idf in idfs:
			comparison = [ other for other in idfs if other is not idf ]
			table = event._variability_contingency_table('liverpool', idf, comparison)
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
		for idf in idfs:
			comparison = [ other for other in idfs if other is not idf ]
			table = event._variability_contingency_table('liverpool', idf, comparison)
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
		for idf in idfs:
			comparison = [ other for other in idfs if other is not idf ]
			table = event._variability_contingency_table('zaha', idf, comparison)
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
		for idf in idfs:
			comparison = [ other for other in idfs if other is not idf ]
			(A, B, C, D) = event._variability_contingency_table('liverpool', idf, comparison)
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
		for idf in idfs:
			comparison = [ other for other in idfs if other is not idf ]
			(A, B, C, D) = event._variability_contingency_table('liverpool', idf, comparison)
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
		(A, B, C, D) = event._variability_contingency_table('mertens', idfs[0], idfs[1:])
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
		(A, B, C, D) = event._variability_contingency_table('mertens', idfs[0], idfs[1:])
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
		(A, B, C, D) = event._variability_contingency_table('wickham', idfs[0], idfs[1:])
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
		(A, B, C, D) = event._variability_contingency_table(term, idfs[0], idfs[1:])
		self.assertEqual(idfs[0].global_scheme.idf[term], A)
		self.assertEqual(sum([ idf.global_scheme.idf[term] for idf in idfs[1:] ]), C)
