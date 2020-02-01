"""
Run unit tests on the :class:`eventdt.nlp.tokenizer.Tokenizer` class.
"""

from nltk.corpus import stopwords

import os
import sys
import unittest

import warnings

path = os.path.join(os.path.dirname(__file__), "..")
if path not in sys.path:
	sys.path.append(path)

from tokenizer import Tokenizer

class TestTokenizer(unittest.TestCase):
	"""
	Run unit tests on the :class:`eventdt.nlp.tokenizer.Tokenizer` class.
	"""

	def ignore_warnings(test):
		"""
		A decorator function used to ignore NLTK warnings.
		From: http://www.neuraldump.net/2017/06/how-to-suppress-python-unittest-warnings/
		More about decorator functions: https://wiki.python.org/moin/PythonDecorators
		"""
		def perform_test(self, *args, **kwargs):
			with warnings.catch_warnings():
				warnings.simplefilter("ignore")
				test(self, *args, **kwargs)
		return perform_test

	def test_remove_mentions(self):
		"""
		Test the mention removal functionality.
		"""

		s = "@WRenard with the header"
		t = Tokenizer(remove_mentions=True)
		self.assertEqual(t.tokenize(s), [ "with", "the", "header" ])

	def test_remove_multiple_mentions(self):
		"""
		Test that the mention removal functionality removes multiple mentions.
		"""

		s = "@WRenard with the header from @AdaStolsmo's cross"
		t = Tokenizer(remove_mentions=True)
		self.assertEqual(t.tokenize(s), [ "with", "the", "header", "from", "cross" ])

	def test_keep_mentions(self):
		"""
		Test that mentions can be retained by the mention removal functionality.
		"""

		s = "@WRenard with the header"
		t = Tokenizer(remove_mentions=False)
		self.assertEqual(t.tokenize(s), [ "wrenard", "with", "the", "header" ])

	def test_keep_multiple_mentions(self):
		"""
		Test that multiple mentions can be retained by the mention removal functionality.
		"""

		s = "@WRenard with the header from @AdaStolsmo's cross"
		t = Tokenizer(remove_mentions=False)
		self.assertEqual(t.tokenize(s), [ "wrenard", "with", "the", "header", "from", "adastolsmo", "cross" ])

	def test_remove_hashtag(self):
		"""
		Test that the hashtag removal functionality removes a single hashtag.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL"
		t = Tokenizer(remove_hashtags=True, stem=False)
		self.assertEqual(t.tokenize(s), [ "the", "vardy", "party", "has", "gone", "very", "quiet" ])

	def test_remove_hashtags(self):
		"""
		Test that the hashtag removal functionality removes all hashtags.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL #LEICHE"
		t = Tokenizer(remove_hashtags=True, stem=False)
		self.assertEqual(t.tokenize(s), [ "the", "vardy", "party", "has", "gone", "very", "quiet" ])

	def test_remove_hashtags_mixed_case(self):
		"""
		Test that the hashtag removal functionality removes all hashtags, regardless of the case.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL #LeiChe"
		t = Tokenizer(remove_hashtags=True, split_hashtags=False, stem=False)
		self.assertEqual(t.tokenize(s), [ "the", "vardy", "party", "has", "gone", "very", "quiet" ])

	def test_retain_hashtags(self):
		"""
		Test that the hashtag removal functionality can retain all hashtags.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL #LEICHE"
		t = Tokenizer(remove_hashtags=False, split_hashtags=False, stem=False)
		self.assertEqual(t.tokenize(s), [ "the", "vardy", "party", "has", "gone", "very", "quiet", 'fpl', 'leiche' ])

	def test_retain_hashtags_mixed_case(self):
		"""
		Test that the hashtag removal functionality can retain all hashtags, regardless of the case.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL #LeiChe"
		t = Tokenizer(remove_hashtags=False, split_hashtags=False, stem=False)
		self.assertEqual(t.tokenize(s), [ "the", "vardy", "party", "has", "gone", "very", "quiet", 'fpl', 'leiche' ])

	def test_retain_hashtags_with_splitting(self):
		"""
		Test that when hashtags are removed, split hashtags are retained.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL #LeiChe"
		t = Tokenizer(remove_hashtags=True, split_hashtags=True, stem=False)
		self.assertEqual(t.tokenize(s), [ "the", "vardy", "party", "has", "gone", "very", "quiet", 'lei', 'che' ])

	def test_split_hashtag(self):
		"""
		Test the hashtag splitting functionality.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #LeiChe"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual(t.tokenize(s), [ "the", "vardy", "party", "has", "gone", "very", "quiet", 'lei', 'che' ])

	def test_split_hashtag_all_upper(self):
		"""
		Test that trying to split a hashtag that is made up of only uppercase letters does not split it.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual(t.tokenize(s), [ "the", "vardy", "party", "has", "gone", "very", "quiet", 'fpl' ])

	def test_split_hashtag_all_lower(self):
		"""
		Test that trying to split a hashtag that is made up of only lowercase letters does not split it.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #fpl"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual(t.tokenize(s), [ "the", "vardy", "party", "has", "gone", "very", "quiet", 'fpl' ])

	def test_split_hashtag_multiple_components(self):
		"""
		Test that hashtags with multiple components are split properly
		"""

		s = "Hello! I'm Harry Styles, I'm sixteen and I work in a bakery #HappyBirthdayHarry"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual(t.tokenize(s), [ "hello", "harry", "styles", "sixteen", "and", "work", "bakery", 'happy', 'birthday', 'harry' ])

	def test_split_hashtag_repeated(self):
		"""
		Test that when a hashtag is repeated, splitting is applied to both.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #LeiChe #LeiChe"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual(t.tokenize(s), [ "the", "vardy", "party", "has", "gone", "very", "quiet", 'lei', 'che', 'lei', 'che' ])

	def test_split_hashtag_with_numbers(self):
		"""
		Test that hashtags are treated as words when splitting hashtags.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #EPL2020"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual(t.tokenize(s), [ "the", "vardy", "party", "has", "gone", "very", "quiet", 'epl', '2020' ])

		s = "The Vardy party has gone very quiet 💤 😢 #2020EPL"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual(t.tokenize(s), [ "the", "vardy", "party", "has", "gone", "very", "quiet", '2020', 'epl' ])

	def test_do_not_split_hashtags(self):
		"""
		Test that hashtags aren't split if the flag is not provided.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #EPL2020"
		t = Tokenizer(split_hashtags=False, stem=False)
		self.assertEqual(t.tokenize(s), [ "the", "vardy", "party", "has", "gone", "very", "quiet", 'epl2020' ])

	@ignore_warnings # pass the test_stopwords method as a parameter to ignore_warnings (https://stackoverflow.com/questions/6392739/what-does-the-at-symbol-do-in-python)
	def test_stopwords(self):
		"""
		Stopword removal tests
		"""
		s = "Kroos scored the winning goal, assisted by Reus!"

		t = Tokenizer()
		self.assertEqual(t.tokenize(s), ["kroo", "score", "the", "win", "goal", "assist", "reu"])

		t = Tokenizer(stopwords=list(stopwords.words("english")))
		self.assertEqual(t.tokenize(s), ["kroo", "score", "win", "goal", "assist", "reu"])

	def test_case_folding(self):
		"""
		Test the case folding functionality
		"""

		s = "Great pass, Lemar"

		t = Tokenizer(case_fold=False)
		self.assertEqual(t.tokenize(s), ["great", "pass", "lemar"])

		t = Tokenizer(case_fold=False, stem=False)
		self.assertEqual(t.tokenize(s), ["Great", "pass", "Lemar"])

		t = Tokenizer(case_fold=True)
		self.assertEqual(t.tokenize(s), ["great", "pass", "lemar"])

	def test_numbers(self):
		"""
		Test the number removal functionality
		"""

		t = Tokenizer()

		s = "FT #KOR 1-1 #GER"
		self.assertEqual(t.tokenize(s), ["kor", "1-1", "ger"])
		s = "Messi scored 1 goal"
		self.assertEqual(t.tokenize(s), ["messi", "score", "goal"])
		s = "France won the 2018 World Cup"
		self.assertEqual(t.tokenize(s), ["franc", "won", "the", "2018", "world", "cup"])

	def test_punctuation(self):
		"""
		Test the punctuation removal functionality
		"""

		s = "Kroos scored the winning goal, assisted by Reus!"

		t = Tokenizer(remove_punctuation=False)
		self.assertEqual(t.tokenize(s), ["kroo", "score", "the", "win", "goal,", "assist", "reus!"])

		t = Tokenizer(remove_punctuation=True)
		self.assertEqual(t.tokenize(s), ["kroo", "score", "the", "win", "goal", "assist", "reu"])

		t = Tokenizer(remove_punctuation=True, stem=False)
		self.assertEqual(t.tokenize(s), ["kroos", "scored", "the", "winning", "goal", "assisted", "reus"])

	def test_token_length(self):
		"""
		Test the token length filtlering functionality
		"""

		s = "Kroos scored the winning goal, assisted by Reus!"

		t = Tokenizer()
		self.assertEqual(t.tokenize(s), ["kroo", "score", "the", "win", "goal", "assist", "reu"])

		t = Tokenizer(min_length=4)
		self.assertEqual(t.tokenize(s), ["kroo", "score", "win", "goal", "assist", "reu"])

	def test_stemming(self):
		"""
		Test the Porter stemming functionality
		"""

		s = "Kroos scored the winning goal, assisted by Reus!"

		t = Tokenizer(stem=False)
		self.assertEqual(t.tokenize(s), ["kroos", "scored", "the", "winning", "goal", "assisted", "reus"])

		t = Tokenizer(stem=True)
		self.assertEqual(t.tokenize(s), ["kroo", "score", "the", "win", "goal", "assist", "reu"])

	def test_negation_correction(self):
		"""
		Test the negation correction functionality
		"""

		s = "Reus wouldn't have scored"

		t = Tokenizer(remove_punctuation=False, stem=False)
		tokens = t.tokenize(s)
		self.assertEqual(tokens, ["reus", "wouldn't", "have", "scored"] )

		t = Tokenizer(remove_punctuation=False, negation_correction=True)
		self.assertEqual(t.tokenize(s), t._stem(t._correct_negations(tokens)))

		t = Tokenizer(remove_punctuation=True, negation_correction=True)
		self.assertEqual(t.tokenize(s), t._postprocess(t._correct_negations(tokens)))

		s = "Kroos wouldn't have scored if it weren't for Reus. They wouldn't have had anything to play for."
		t = Tokenizer(negation_correction=True)
		self.assertEqual(t.tokenize(s), ["kroo", "wouldn", "nothav", "notscor", "notif", "notit", "weren", "notfor", "notreu", "they", "wouldn", "nothav", "nothad", "notanyth", "notto", "notplay", "notfor"])

	def test_url_removal(self):
		"""
		Test the URL removal functionality
		"""

		s = "Thank you @BillGates. It's amazing, almost as incredible as the fact that you use Gmail. https://t.co/drawyFHHQM"

		t = Tokenizer(remove_urls=False)
		self.assertEqual(t.tokenize(s), ["thank", "you", "amaz", "almost", "incred", "the", "fact", "that", "you", "use", "gmail", "http", "drawyfhhqm"])

		t = Tokenizer(remove_urls=True)
		self.assertEqual(t.tokenize(s), ["thank", "you", "amaz", "almost", "incred", "the", "fact", "that", "you", "use", "gmail"])

	def test_alt_code_removal(self):
		"""
		Test the alt-code removal functionality
		"""

		s = "Our prediction based on #FIFA Rankings, &amp; Country Risk Ratings"

		t = Tokenizer(remove_alt_codes=False)
		self.assertEqual(t.tokenize(s), ["our", "predict", "base", "fifa", "rank", "amp", "countri", "risk", "rate"])

		t = Tokenizer(remove_alt_codes=True)
		self.assertEqual(t.tokenize(s), ["our", "predict", "base", "fifa", "rank", "countri", "risk", "rate"])

	def test_unicode_removal(self):
		"""
		Test the unicode entity removal functionality
		"""

		s = "\u0632\u0648\u062f_\u0641\u0648\u0644\u0648\u0631\u0632_\u0645\u0639_\u0627\u0644\u0645\u0628\u0627\u062d\u062b"

		t = Tokenizer(remove_unicode_entities=False)
		self.assertEqual(t.tokenize(s), [])

		t = Tokenizer(remove_unicode_entities=True)
		self.assertEqual(t.tokenize(s), [])

	def test_word_normalization(self):
		"""
		Test the word normalization functionality
		"""

		s = "GOOOOOAAL GRIZIIII"

		t = Tokenizer(normalize_words=False)
		self.assertEqual(t.tokenize(s), ["goooooaal", "griziiii"])

		t = Tokenizer(normalize_words=True)
		self.assertEqual(t.tokenize(s), ["goal", "grizi"])

		t = Tokenizer(normalize_words=True, character_normalization_count=3)
		self.assertEqual(t.tokenize(s), ["goaal", "grizi"])
