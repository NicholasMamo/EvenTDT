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

	def test_clean_strip_start(self):
		"""
		Test that the text in the beginning is always stripped.
		"""

		cleaner = Cleaner()

		text = ' Our prediction based on #FIFA Rankings, &amp; Country Risk Ratings'
		self.assertEqual('Our prediction based on #FIFA Rankings, &amp; Country Risk Ratings', cleaner.clean(text))

	def test_clean_strip_end(self):
		"""
		Test that the text in the end is always stripped.
		"""

		cleaner = Cleaner()

		text = 'Our prediction based on #FIFA Rankings, &amp; Country Risk Ratings '
		self.assertEqual('Our prediction based on #FIFA Rankings, &amp; Country Risk Ratings', cleaner.clean(text))

	def test_clean_strip(self):
		"""
		Test that the text is always stripped on both ends.
		"""

		cleaner = Cleaner()

		text = ' Our prediction based on #FIFA Rankings, &amp; Country Risk Ratings '
		self.assertEqual('Our prediction based on #FIFA Rankings, &amp; Country Risk Ratings', cleaner.clean(text))

	def test_remove_alt_codes(self):
		"""
		Test that when remove alt-codes, they are indeed removed.
		"""

		cleaner = Cleaner(remove_alt_codes=True)

		text = 'Our prediction based on #FIFA Rankings, &amp; Country Risk Ratings'
		self.assertEqual('Our prediction based on #FIFA Rankings,  Country Risk Ratings', cleaner.clean(text))

	def test_complete_sentences_empty(self):
		"""
		Test that when completing sentences of empty text, nothing changes.
		"""

		cleaner = Cleaner(complete_sentences=True)

		text = ''
		self.assertEqual(text, cleaner.clean(text))

	def test_complete_sentences_ends_in_punctuation(self):
		"""
		Test completing a sentence that already ends in punctuation.
		"""

		cleaner = Cleaner(complete_sentences=True)

		text = 'Congratulations to  @Keir_Starmer, the new Leader of the Labour Party!'
		self.assertEqual(text, cleaner.clean(text))

	def test_complete_sentences_single_quote_ends_in_punctuation(self):
		"""
		Test completing a sentence that already ends in punctuation before a single quote.
		"""

		cleaner = Cleaner(complete_sentences=True)

		text = '\'Congratulations to  @Keir_Starmer, the new Leader of the Labour Party!\''
		self.assertEqual(text, cleaner.clean(text))

	def test_complete_sentences_quote_ends_in_punctuation(self):
		"""
		Test completing a sentence that already ends in punctuation before a quote.
		"""

		cleaner = Cleaner(complete_sentences=True)

		text = '"Congratulations to  @Keir_Starmer, the new Leader of the Labour Party!"'
		self.assertEqual(text, cleaner.clean(text))

	def test_complete_sentences_french_quote_ends_in_punctuation(self):
		"""
		Test completing a sentence that already ends in punctuation before a French-style quote.
		"""

		cleaner = Cleaner(complete_sentences=True)

		text = '«Congratulations to  @Keir_Starmer, the new Leader of the Labour Party!»'
		self.assertEqual(text, cleaner.clean(text))

	def test_complete_sentences_single_quote_only(self):
		"""
		Test that when completing a sentence that is just a single quote, nothing changes.
		"""

		cleaner = Cleaner(complete_sentences=True)

		text = '\''
		self.assertEqual(text, cleaner.clean(text))

	def test_complete_sentences_quote_only(self):
		"""
		Test that when completing a sentence that is just a quote, nothing changes.
		"""

		cleaner = Cleaner(complete_sentences=True)

		text = '"'
		self.assertEqual(text, cleaner.clean(text))

	def test_complete_sentences_french_quote_only(self):
		"""
		Test that when completing a sentence that is just a French-style quote, nothing changes.
		"""

		cleaner = Cleaner(complete_sentences=True)

		text = '»'
		self.assertEqual(text, cleaner.clean(text))

	def test_complete_sentences_ends_with_single_quote(self):
		"""
		Test that when a sentence ends with a single quote, the period is added before it.
		"""

		cleaner = Cleaner(complete_sentences=True)

		text = '\'Sounds a lot like the last one\''
		self.assertEqual('\'Sounds a lot like the last one.\'', cleaner.clean(text))

	def test_complete_sentences_ends_with_quote(self):
		"""
		Test that when a sentence ends with a quote, the period is added before it.
		"""

		cleaner = Cleaner(complete_sentences=True)

		text = '"Sounds a lot like the last one"'
		self.assertEqual('"Sounds a lot like the last one."', cleaner.clean(text))

	def test_complete_sentences_ends_with_french_quote(self):
		"""
		Test that when a sentence ends with a French-style quote, the period is added before it.
		"""

		cleaner = Cleaner(complete_sentences=True)

		text = '«Sounds a lot like the last one»'
		self.assertEqual('«Sounds a lot like the last one.»', cleaner.clean(text))

	def test_complete_sentences_single_character(self):
		"""
		Test that when a sentence is one character, a period is added at the end.
		"""

		cleaner = Cleaner(complete_sentences=True)

		text = 'a'
		self.assertEqual('a.', cleaner.clean(text))

	def test_complete_sentences_sentence(self):
		"""
		Test that when the text is an incomplete sentence, a period is added at the end.
		"""

		cleaner = Cleaner(complete_sentences=True)

		text = 'The NBA is "angling" to cancel the 2019-20 season after China\'s CBA shutdown'
		self.assertEqual('The NBA is "angling" to cancel the 2019-20 season after China\'s CBA shutdown.', cleaner.clean(text))
