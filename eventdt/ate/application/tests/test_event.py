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
