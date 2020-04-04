"""
Test the functionality of the base cleaner.
"""

import asyncio
import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
	sys.path.append(path)

from nlp.cleaners import Cleaner

class TestCleaner(unittest.TestCase):
	"""
	Test the implementation of the base cleaner.
	"""

	def test_clean_no_configuration(self):
		"""
		Test that when cleaning without any configuration, the text is returned the same.
		"""

		cleaner = Cleaner()

		text = 'Our prediction based on #FIFA Rankings, &amp; Country Risk Ratings'
		self.assertEqual(text, cleaner.clean(text))

	def test_remove_alt_codes(self):
		"""
		Test that when remove alt-codes, they are indeed removed.
		"""

		cleaner = Cleaner(remove_alt_codes=True)

		text = 'Our prediction based on #FIFA Rankings, &amp; Country Risk Ratings'
		self.assertEqual('Our prediction based on #FIFA Rankings,  Country Risk Ratings', cleaner.clean(text))
