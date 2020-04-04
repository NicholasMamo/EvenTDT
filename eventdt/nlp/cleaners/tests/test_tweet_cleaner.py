"""
Test the functionality of the tweet cleaner.
"""

import asyncio
import json
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
	sys.path.append(path)

from nlp.cleaners import TweetCleaner

class TestTweetCleaner(unittest.TestCase):
	"""
	Test the implementation of the tweet cleaner.
	"""

	def test_no_configuration_default(self):
		"""
		Test that when no configuration is given, the default configuration is used.
		"""

		cleaner = TweetCleaner()
		self.assertFalse(cleaner.remove_alt_codes)
		self.assertFalse(cleaner.complete_sentences)
		self.assertFalse(cleaner.collapse_new_lines)
		self.assertFalse(cleaner.collapse_whitespaces)

	def test_configuration_saved(self):
		"""
		Test that the configuration given to the tweet cleaner is passed on to the cleaner.
		"""

		cleaner = TweetCleaner(remove_alt_codes=True, complete_sentences=True,
							   collapse_new_lines=True, collapse_whitespaces=True)
		self.assertTrue(cleaner.remove_alt_codes)
		self.assertTrue(cleaner.complete_sentences)
		self.assertTrue(cleaner.collapse_new_lines)
		self.assertTrue(cleaner.collapse_whitespaces)

	def test_strip_after_processing(self):
		"""
		Test that the text is stripped after all processing.
		"""

		cleaner = TweetCleaner(remove_unicode_entities=True)

		text = 'Je veux 😂😂😂🦁'
		self.assertEqual('Je veux', cleaner.clean(text))

	def test_remove_unicode_entities(self):
		"""
		Test that the unicode entity removal functionality removes unicode characters.
		"""

		cleaner = TweetCleaner(remove_unicode_entities=True)

		text = '\u0632\u0648\u062f_\u0641\u0648\u0644\u0648\u0631\u0632_\u0645\u0639_\u0627\u0644\u0645\u0628\u0627\u062d\u062b'
		self.assertEqual('___', cleaner.clean(text))

	def test_remove_unicode_entities_includes_emojis(self):
		"""
		Test that the unicode entity removal functionality also removes emojis.
		"""

		cleaner = TweetCleaner(remove_unicode_entities=True)

		text = 'Je veux 😂😂😂🦁'
		self.assertEqual('Je veux', cleaner.clean(text))

	def test_remove_unicode_entities_retain(self):
		"""
		Test that when unicode character removal is not specified, these characters are retained.
		"""

		cleaner = TweetCleaner(remove_unicode_entities=False)

		text = '\u0632\u0648\u062f_\u0641\u0648\u0644\u0648\u0631\u0632_\u0645\u0639_\u0627\u0644\u0645\u0628\u0627\u062d\u062b'
		self.assertEqual('زود_فولورز_مع_المباحث', cleaner.clean(text))

	def test_remove_unicode_entities_retain_emojis(self):
		"""
		Test that when unicode character removal is not specified, emojis are retained.
		"""

		cleaner = TweetCleaner(remove_unicode_entities=False)

		text = 'Je veux 😂😂😂🦁'
		self.assertEqual('Je veux 😂😂😂🦁', cleaner.clean(text))

	def test_remove_url(self):
		"""
		Test the URL removal functionality.
		"""

		cleaner = TweetCleaner(remove_urls=True)

		text = 'Thank you @BillGates. It\'s amazing, almost as incredible as the fact that you use Gmail. https://t.co/drawyFHHQM'
		self.assertEqual('Thank you @BillGates. It\'s amazing, almost as incredible as the fact that you use Gmail.', cleaner.clean(text))

	def test_remove_url_without_protocol(self):
		"""
		Test the URL removal functionality when there is no protocol.
		"""

		cleaner = TweetCleaner(remove_urls=True)

		text = 'Thank you @BillGates. It\'s amazing, almost as incredible as the fact that you use Gmail. t.co/drawyFHHQM'
		self.assertEqual('Thank you @BillGates. It\'s amazing, almost as incredible as the fact that you use Gmail.', cleaner.clean(text))

	def test_remove_url_with_http_protocol(self):
		"""
		Test the URL removal functionality when the protocol is http.
		"""

		cleaner = TweetCleaner(remove_urls=True)

		text = 'Thank you @BillGates. It\'s amazing, almost as incredible as the fact that you use Gmail. http://t.co/drawyFHHQM'
		self.assertEqual('Thank you @BillGates. It\'s amazing, almost as incredible as the fact that you use Gmail.', cleaner.clean(text))

	def test_remove_url_with_subdomain(self):
		"""
		Test that URL removal includes subdomains.
		"""

		cleaner = TweetCleaner(remove_urls=True)

		text = 'Visit Multiplex\'s documentation for more information: https://nicholasmamo.github.io/multiplex-plot/'
		self.assertEqual('Visit Multiplex\'s documentation for more information:', cleaner.clean(text))

	def test_remove_url_with_subdomain_without_protocol(self):
		"""
		Test that URL removal includes subdomains even if they have no protocol.
		"""

		cleaner = TweetCleaner(remove_urls=True)

		text = 'Visit Multiplex\'s documentation for more information: nicholasmamo.github.io/multiplex-plot/'
		self.assertEqual('Visit Multiplex\'s documentation for more information:', cleaner.clean(text))

	def test_remove_url_retain(self):
		"""
		Test the URL retention functionality.
		"""

		cleaner = TweetCleaner(remove_urls=True)

		text = 'Thank you @BillGates. It\'s amazing, almost as incredible as the fact that you use Gmail. https://t.co/drawyFHHQM'
		self.assertEqual('Thank you @BillGates. It\'s amazing, almost as incredible as the fact that you use Gmail.', cleaner.clean(text))
