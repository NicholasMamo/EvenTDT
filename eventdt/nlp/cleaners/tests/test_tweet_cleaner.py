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

	def test_remove_hashtags(self):
		"""
		Test that the hashtag removal functionality removes a single hashtag.
		"""

		cleaner = TweetCleaner(remove_hashtags=True)

		text = "The Vardy party has gone very quiet 💤 😢 #FPL"
		self.assertEqual("The Vardy party has gone very quiet 💤 😢", cleaner.clean(text))

	def test_remove_hashtags_multiple(self):
		"""
		Test that the hashtag removal functionality removes all hashtags.
		"""

		cleaner = TweetCleaner(remove_hashtags=True)

		text = "The Vardy party has gone very quiet 💤 😢 #FPL #LEICHE"
		self.assertEqual("The Vardy party has gone very quiet 💤 😢", cleaner.clean(text))

	def test_remove_hashtags_mixed_case(self):
		"""
		Test that the hashtag removal functionality removes all hashtags, regardless of the case.
		"""

		cleaner = TweetCleaner(remove_hashtags=True, split_hashtags=False)

		text = "The Vardy party has gone very quiet 💤 😢 #FPL #LeiChe"
		self.assertEqual("The Vardy party has gone very quiet 💤 😢", cleaner.clean(text))

	def test_remove_hashtags(self):
		"""
		Test that the hashtag removal functionality retains all hashtags when not requested.
		"""

		cleaner = TweetCleaner(remove_hashtags=False, split_hashtags=False)

		text = "The Vardy party has gone very quiet 💤 😢 #FPL #LEICHE"
		self.assertEqual("The Vardy party has gone very quiet 💤 😢 #FPL #LEICHE", cleaner.clean(text))

	def test_remove_hashtags_mixed_case(self):
		"""
		Test that the hashtag removal functionality retains all hashtags when not requested, regardless of the case.
		"""

		cleaner = TweetCleaner(remove_hashtags=False, split_hashtags=False)

		text = "The Vardy party has gone very quiet 💤 😢 #FPL #LeiChe"
		self.assertEqual("The Vardy party has gone very quiet 💤 😢 #FPL #LeiChe", cleaner.clean(text))

	def test_remove_hashtags_with_splitting(self):
		"""
		Test that when hashtags are removed, split hashtags are retained.
		"""

		cleaner = TweetCleaner(remove_hashtags=True, split_hashtags=True, collapse_whitespaces=True)

		text = "The Vardy party has gone very quiet 💤 😢 #FPL #LeiChe"
		self.assertEqual("The Vardy party has gone very quiet 💤 😢 Lei Che", cleaner.clean(text))

	def test_split_hashtag(self):
		"""
		Test the hashtag splitting functionality.
		"""

		cleaner = TweetCleaner(split_hashtags=True, collapse_whitespaces=True)

		text = "The Vardy party has gone very quiet 💤 😢 #LeiChe"
		self.assertEqual("The Vardy party has gone very quiet 💤 😢 Lei Che", cleaner.clean(text))

	def test_split_hashtag_all_upper(self):
		"""
		Test that trying to split a hashtag that is made up of only uppercase letters does not split it.
		"""

		cleaner = TweetCleaner(remove_hashtags=False, split_hashtags=True)

		text = "The Vardy party has gone very quiet 💤 😢 #FPL"
		self.assertEqual("The Vardy party has gone very quiet 💤 😢 #FPL", cleaner.clean(text))

	def test_split_hashtag_all_lower(self):
		"""
		Test that trying to split a hashtag that is made up of only lowercase letters does not split it.
		"""

		cleaner = TweetCleaner(remove_hashtags=False, split_hashtags=True)

		text = "The Vardy party has gone very quiet 💤 😢 #fpl"
		self.assertEqual("The Vardy party has gone very quiet 💤 😢 #fpl", cleaner.clean(text))

	def test_split_hashtag_multiple_components(self):
		"""
		Test that hashtags with multiple components are split properly.
		"""

		cleaner = TweetCleaner(split_hashtags=True, collapse_whitespaces=True)

		text = "Hello! I'm Harry Styles, I'm sixteen and I work in a bakery #HappyBirthdayHarry"
		self.assertEqual("Hello! I'm Harry Styles, I'm sixteen and I work in a bakery Happy Birthday Harry", cleaner.clean(text))

	def test_split_hashtag_repeated(self):
		"""
		Test that when a hashtag is repeated, splitting is applied to both.
		"""

		cleaner = TweetCleaner(split_hashtags=True, collapse_whitespaces=True)

		text = "The Vardy party has gone very quiet 💤 😢 #LeiChe #LeiChe"
		self.assertEqual("The Vardy party has gone very quiet 💤 😢 Lei Che Lei Che", cleaner.clean(text))

	def test_split_hashtag_with_numbers(self):
		"""
		Test that hashtags are treated as words when splitting hashtags.
		"""

		cleaner = TweetCleaner(split_hashtags=True, collapse_whitespaces=True)

		text = "The Vardy party has gone very quiet 💤 😢 #EPL2020"
		self.assertEqual("The Vardy party has gone very quiet 💤 😢 EPL 2020", cleaner.clean(text))

		text = "The Vardy party has gone very quiet 💤 😢 #2020EPL"
		self.assertEqual("The Vardy party has gone very quiet 💤 😢 2020 EPL", cleaner.clean(text))

	def test_do_not_split_hashtags(self):
		"""
		Test that hashtags aren't split if the flag is not provided.
		"""

		cleaner = TweetCleaner(remove_hashtags=False, split_hashtags=False)

		text = "The Vardy party has gone very quiet 💤 😢 #EPL2020"
		self.assertEqual("The Vardy party has gone very quiet 💤 😢 #EPL2020", cleaner.clean(text))

	def test_remove_retweet_prefix(self):
		"""
		Test removing the retweet prefix.
		"""

		cleaner = TweetCleaner(remove_retweet_prefix=True)

		text = "RT @NicholasMamo: Great podcast episode about the repercussions of the ongoing pandemic on French football, as well as a brilliant short segment on how we're giving too much importance to TV rights, and too little to the supporters."
		self.assertEqual("Great podcast episode about the repercussions of the ongoing pandemic on French football, as well as a brilliant short segment on how we're giving too much importance to TV rights, and too little to the supporters.", cleaner.clean(text))

	def test_remove_retweet_prefix_retain(self):
		"""
		Test that when the flag to remove the retweet prefix is not given, it is retained.
		"""

		cleaner = TweetCleaner(remove_retweet_prefix=False)

		text = "RT @NicholasMamo: Great podcast episode about the repercussions of the ongoing pandemic on French football, as well as a brilliant short segment on how we're giving too much importance to TV rights, and too little to the supporters."
		self.assertEqual(text, cleaner.clean(text))

	def test_remove_retweet_prefix_without_prefix(self):
		"""
		Test that when a tweet without a retweet prefix is given, the exact same tweet is returned.
		"""

		cleaner = TweetCleaner(remove_retweet_prefix=True)

		text = "Great podcast episode about the repercussions of the ongoing pandemic on French football, as well as a brilliant short segment on how we're giving too much importance to TV rights, and too little to the supporters."
		self.assertEqual(text, cleaner.clean(text))

	def test_remove_retweet_prefix_empty(self):
		"""
		Test that when an empty tweet is given, the exact same tweet is returned.
		"""

		cleaner = TweetCleaner(remove_retweet_prefix=True)

		text = ""
		self.assertEqual(text, cleaner.clean(text))

	def test_remove_retweet_prefix_middle(self):
		"""
		Test that when a retweet prefix is in the middle of the tweet, it is not removed.
		"""

		cleaner = TweetCleaner(remove_retweet_prefix=True)

		text = "Great podcast episode RT @NicholasMamo: the repercussions of the ongoing pandemic on French football, as well as a brilliant short segment on how we're giving too much importance to TV rights, and too little to the supporters."
		self.assertEqual(text, cleaner.clean(text))

	def test_remove_retweet_prefix_consecutive(self):
		"""
		Test that when there are consecutive retweet prefixes, only the first one is removed.
		"""

		cleaner = TweetCleaner(remove_retweet_prefix=True)

		text = "RT @NicholasMamo: RT @NicholasMamo: Great podcast episode about the repercussions of the ongoing pandemic on French football, as well as a brilliant short segment on how we're giving too much importance to TV rights, and too little to the supporters."
		self.assertEqual("RT @NicholasMamo: Great podcast episode about the repercussions of the ongoing pandemic on French football, as well as a brilliant short segment on how we're giving too much importance to TV rights, and too little to the supporters.", cleaner.clean(text))
