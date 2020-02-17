"""
Run unit tests on the wikinterface package.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from wikinterface import *

class TestWikinterface(unittest.TestCase):
	"""
	Test the wikinterface package.
	"""

	def test_revert_redirects(self):
		"""
		Test that when reverting redirections, the resolved page is not included.
		"""

		"""
		Create the test data.
		"""
		redirects = [
			{ 'from': 'Striker (association football)' , 'to': 'Forward (association football)' },
			{ 'from': 'Inside forward' , 'to': 'Forward (association football)' },
		]
		results = {
			'Forward (association football)': ''
		}

		"""
		Revert the redirections.
		"""

		pages = revert_redirects(results, redirects)
		self.assertTrue('Inside forward' in pages)
		self.assertTrue('Striker (association football)' in pages)
		self.assertFalse('Forward (association football)' in pages)

	def test_keep_redirects(self):
		"""
		Test that when keeping redirections, the redirected pages are retained.
		"""

		"""
		Create the test data.
		"""
		redirects = [
			{ 'from': 'Striker (association football)' , 'to': 'Forward (association football)' },
			{ 'from': 'Inside forward' , 'to': 'Forward (association football)' },
		]
		results = {
			'Forward (association football)': ''
		}

		"""
		Revert the redirections.
		"""

		pages = revert_redirects(results, redirects, keep_redirects=True)
		self.assertTrue('Inside forward' in pages)
		self.assertTrue('Striker (association football)' in pages)
		self.assertTrue('Forward (association football)' in pages)
