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
		self.assertEqual([ "with", "the", "header" ], t.tokenize(s))

	def test_remove_multiple_mentions(self):
		"""
		Test that the mention removal functionality removes multiple mentions.
		"""

		s = "@WRenard with the header from @AdaStolsmo's cross"
		t = Tokenizer(remove_mentions=True)
		self.assertEqual([ "with", "the", "header", "from", "cross" ], t.tokenize(s))

	def test_keep_mentions(self):
		"""
		Test that mentions can be retained by the mention removal functionality.
		"""

		s = "@WRenard with the header"
		t = Tokenizer(remove_mentions=False)
		self.assertEqual([ "wrenard", "with", "the", "header" ], t.tokenize(s))

	def test_keep_multiple_mentions(self):
		"""
		Test that multiple mentions can be retained by the mention removal functionality.
		"""

		s = "@WRenard with the header from @AdaStolsmo's cross"
		t = Tokenizer(remove_mentions=False)
		self.assertEqual([ "wrenard", "with", "the", "header", "from", "adastolsmo", "cross" ], t.tokenize(s))

	def test_remove_hashtag(self):
		"""
		Test that the hashtag removal functionality removes a single hashtag.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL"
		t = Tokenizer(remove_hashtags=True, stem=False)
		self.assertEqual([ "the", "vardy", "party", "has", "gone", "very", "quiet" ], t.tokenize(s))

	def test_remove_hashtags(self):
		"""
		Test that the hashtag removal functionality removes all hashtags.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL #LEICHE"
		t = Tokenizer(remove_hashtags=True, stem=False)
		self.assertEqual([ "the", "vardy", "party", "has", "gone", "very", "quiet" ], t.tokenize(s))

	def test_remove_hashtags_mixed_case(self):
		"""
		Test that the hashtag removal functionality removes all hashtags, regardless of the case.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL #LeiChe"
		t = Tokenizer(remove_hashtags=True, split_hashtags=False, stem=False)
		self.assertEqual([ "the", "vardy", "party", "has", "gone", "very", "quiet" ], t.tokenize(s))

	def test_retain_hashtags(self):
		"""
		Test that the hashtag removal functionality can retain all hashtags.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL #LEICHE"
		t = Tokenizer(remove_hashtags=False, split_hashtags=False, stem=False)
		self.assertEqual([ "the", "vardy", "party", "has", "gone", "very", "quiet", 'fpl', 'leiche' ], t.tokenize(s))

	def test_retain_hashtags_mixed_case(self):
		"""
		Test that the hashtag removal functionality can retain all hashtags, regardless of the case.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL #LeiChe"
		t = Tokenizer(remove_hashtags=False, split_hashtags=False, stem=False)
		self.assertEqual([ "the", "vardy", "party", "has", "gone", "very", "quiet", 'fpl', 'leiche' ], t.tokenize(s))

	def test_retain_hashtags_with_splitting(self):
		"""
		Test that when hashtags are removed, split hashtags are retained.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL #LeiChe"
		t = Tokenizer(remove_hashtags=True, split_hashtags=True, stem=False)
		self.assertEqual([ "the", "vardy", "party", "has", "gone", "very", "quiet", 'lei', 'che' ], t.tokenize(s))

	def test_split_hashtag(self):
		"""
		Test the hashtag splitting functionality.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #LeiChe"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual([ "the", "vardy", "party", "has", "gone", "very", "quiet", 'lei', 'che' ], t.tokenize(s))

	def test_split_hashtag_all_upper(self):
		"""
		Test that trying to split a hashtag that is made up of only uppercase letters does not split it.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #FPL"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual([ "the", "vardy", "party", "has", "gone", "very", "quiet", 'fpl' ], t.tokenize(s))

	def test_split_hashtag_all_lower(self):
		"""
		Test that trying to split a hashtag that is made up of only lowercase letters does not split it.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #fpl"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual([ "the", "vardy", "party", "has", "gone", "very", "quiet", 'fpl' ], t.tokenize(s))

	def test_split_hashtag_multiple_components(self):
		"""
		Test that hashtags with multiple components are split properly
		"""

		s = "Hello! I'm Harry Styles, I'm sixteen and I work in a bakery #HappyBirthdayHarry"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual([ "hello", "harry", "styles", "sixteen", "and", "work", "bakery", 'happy', 'birthday', 'harry' ], t.tokenize(s))

	def test_split_hashtag_repeated(self):
		"""
		Test that when a hashtag is repeated, splitting is applied to both.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #LeiChe #LeiChe"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual([ "the", "vardy", "party", "has", "gone", "very", "quiet", 'lei', 'che', 'lei', 'che' ], t.tokenize(s))

	def test_split_hashtag_with_numbers(self):
		"""
		Test that hashtags are treated as words when splitting hashtags.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #EPL2020"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual([ "the", "vardy", "party", "has", "gone", "very", "quiet", 'epl', '2020' ], t.tokenize(s))

		s = "The Vardy party has gone very quiet 💤 😢 #2020EPL"
		t = Tokenizer(split_hashtags=True, stem=False)
		self.assertEqual([ "the", "vardy", "party", "has", "gone", "very", "quiet", '2020', 'epl' ], t.tokenize(s))

	def test_do_not_split_hashtags(self):
		"""
		Test that hashtags aren't split if the flag is not provided.
		"""

		s = "The Vardy party has gone very quiet 💤 😢 #EPL2020"
		t = Tokenizer(split_hashtags=False, stem=False)
		self.assertEqual([ "the", "vardy", "party", "has", "gone", "very", "quiet", 'epl2020' ], t.tokenize(s))

	def test_remove_numbers(self):
		"""
		Test that numbers are removed when the flag is provided.
		"""

		s = "There are 7 changes to last week's XI"
		t = Tokenizer(remove_numbers=True, stem=False)
		self.assertEqual([ "there", "are", "changes", "last", "week" ], t.tokenize(s))

	def test_remove_mixed_numbers(self):
		"""
		Test that numbers that are part of a string are not removed.
		"""

		s = "Nate Diaz wants Conor McGregor, Joe Rogan to apologize to Stephen A. Smith before UFC246"
		t = Tokenizer(remove_numbers=True, stem=False)
		self.assertEqual([ "nate", "diaz", "wants", "conor", "mcgregor", "joe", "rogan", "apologize", "stephen", "smith", "before", "ufc246" ], t.tokenize(s))

	def test_retain_years(self):
		"""
		Test that removing numbers does not remove years.
		"""

		s = "Real paid 5M€ for him back in 2016."
		t = Tokenizer(remove_numbers=True, stem=False)
		self.assertEqual([ "real", "paid", "for", "him", "back", "2016" ], t.tokenize(s))

		s = "Real paid 500 for him back in 2016."
		t = Tokenizer(remove_numbers=True, stem=False)
		self.assertEqual([ "real", "paid", "for", "him", "back", "2016" ], t.tokenize(s))

		s = "Real paid 50000 for him back in 2016."
		t = Tokenizer(remove_numbers=True, stem=False)
		self.assertEqual([ "real", "paid", "for", "him", "back", "2016" ], t.tokenize(s))

	def test_retain_numbers(self):
		"""
		Test that the tokenizer correctly retains numbers.
		"""

		s = "Real paid 5000000 for him back in 2016."
		t = Tokenizer(remove_numbers=False, stem=False)
		self.assertEqual([ "real", "paid", "5000000", "for", "him", "back", "2016" ], t.tokenize(s))

	def test_remove_url(self):
		"""
		Test the URL removal functionality.
		"""

		s = "Thank you @BillGates. It's amazing, almost as incredible as the fact that you use Gmail. https://t.co/drawyFHHQM"
		t = Tokenizer(remove_urls=True, stem=False)
		self.assertEqual([ "thank", "you", "amazing", "almost", "incredible", "the", "fact", "that", "you", "use", "gmail" ], t.tokenize(s))

	def test_remove_url_without_protocol(self):
		"""
		Test the URL removal functionality when there is no protocol.
		"""

		s = "Thank you @BillGates. It's amazing, almost as incredible as the fact that you use Gmail. t.co/drawyFHHQM"
		t = Tokenizer(remove_urls=True, stem=False)
		self.assertEqual([ "thank", "you", "amazing", "almost", "incredible", "the", "fact", "that", "you", "use", "gmail" ], t.tokenize(s))

	def test_remove_url_with_http_protocol(self):
		"""
		Test the URL removal functionality when the protocol is http.
		"""

		s = "Thank you @BillGates. It's amazing, almost as incredible as the fact that you use Gmail. http://t.co/drawyFHHQM"
		t = Tokenizer(remove_urls=True, stem=False)
		self.assertEqual([ "thank", "you", "amazing", "almost", "incredible", "the", "fact", "that", "you", "use", "gmail" ], t.tokenize(s))

	def test_remove_subdomain(self):
		"""
		Test that URL removal includes subdomains.
		"""

		s = "Visit Multiplex's documentation for more information: https://nicholasmamo.github.io/multiplex-plot/"
		t = Tokenizer(remove_urls=True, stem=False)
		self.assertEqual([ "visit", "multiplex", "documentation", "for", "more", "information" ], t.tokenize(s))

	def test_remove_subdomain_without_protocol(self):
		"""
		Test that URL removal includes subdomains even if they have no protocol.
		"""

		s = "Visit Multiplex's documentation for more information: nicholasmamo.github.io/multiplex-plot/"
		t = Tokenizer(remove_urls=True, stem=False)
		self.assertEqual([ "visit", "multiplex", "documentation", "for", "more", "information" ], t.tokenize(s))

	def test_retain_url(self):
		"""
		Test the URL retention functionality.
		"""

		s = "Thank you @BillGates. It's amazing, almost as incredible as the fact that you use Gmail. https://t.co/drawyFHHQM"
		t = Tokenizer(remove_urls=False, stem=False)
		self.assertEqual([ "thank", "you", "amazing", "almost", "incredible", "the", "fact", "that", "you", "use", "gmail", "https", "drawyfhhqm" ], t.tokenize(s))

	def test_alt_code_removal(self):
		"""
		Test the alt-code removal functionality works as it is supposed to.
		"""

		s = "Our prediction based on #FIFA Rankings, &amp; Country Risk Ratings"
		t = Tokenizer(remove_alt_codes=True)
		self.assertEqual(["our", "predict", "base", "fifa", "rank", "countri", "risk", "rate"], t.tokenize(s))

	def test_retain_alt_codes(self):
		"""
		Test that when alt-codes are not set to be removed, they are retained.
		"""

		s = "Our prediction based on #FIFA Rankings, &amp; Country Risk Ratings"
		t = Tokenizer(remove_alt_codes=False)
		self.assertEqual(["our", "predict", "base", "fifa", "rank", "amp", "countri", "risk", "rate"], t.tokenize(s))

	def test_word_normalization(self):
		"""
		Test that word normalization reduces normalized characters.
		"""

		s = "YYYYYEEESSSSSSSSS OOXXXXXXXXXXXX!!!"
		t = Tokenizer(normalize_words=True, character_normalization_count=2, stem=False, min_length=2)
		self.assertEqual([ "yes", "ox" ], t.tokenize(s))

	def test_word_normalization_character_limit(self):
		"""
		Test that word normalization reduces normalized characters.
		"""

		s = "YYYYYEEESSSSSSSSS OOXXXXXXXXXXXX!!!"
		t = Tokenizer(normalize_words=True, character_normalization_count=2, stem=False, min_length=2)
		self.assertEqual([ "yes", "ox" ], t.tokenize(s))

	def test_word_normalization_character_exact_limit(self):
		"""
		Test that word normalization reduces repeated characters if the count is exact.
		"""

		s = "YYYYYEEESSSSSSSSS OOXXXXXXXXXXXX!!!"
		t = Tokenizer(normalize_words=True, character_normalization_count=3, stem=False, min_length=2)
		self.assertEqual([ "yes", "oox" ], t.tokenize(s))

	def test_word_normalization_character_high_limit(self):
		"""
		Test that word normalization does not reduce repeated characters if the limit is higher.
		"""

		s = "YYYYYEEESSSSSSSSS OOXXXXXXXXXXXX!!!"
		t = Tokenizer(normalize_words=True, character_normalization_count=4, stem=False, min_length=2)
		self.assertEqual([ "yeees", "oox" ], t.tokenize(s))

	def test_no_word_normalization(self):
		"""
		Test that word normalization is not permitted, no words are normalized.
		"""

		s = "YYYYYEEESSSSSSSSS OOXXXXXXXXXXXX!!!"
		t = Tokenizer(normalize_words=False, character_normalization_count=2, stem=False, min_length=2)
		self.assertEqual([ "yyyyyeeesssssssss", "ooxxxxxxxxxxxx" ], t.tokenize(s))

	@ignore_warnings # pass the test_stopwords method as a parameter to ignore_warnings (https://stackoverflow.com/questions/6392739/what-does-the-at-symbol-do-in-python)
	def test_stopwords(self):
		"""
		Stopword removal tests
		"""
		s = "Kroos scored the winning goal, assisted by Reus!"

		t = Tokenizer()
		self.assertEqual(["kroo", "score", "the", "win", "goal", "assist", "reu"], t.tokenize(s))

		t = Tokenizer(stopwords=list(stopwords.words("english")))
		self.assertEqual(["kroo", "score", "win", "goal", "assist", "reu"], t.tokenize(s))

	def test_case_folding(self):
		"""
		Test the case folding functionality
		"""

		s = "Great pass, Lemar"

		t = Tokenizer(case_fold=False)
		self.assertEqual(["great", "pass", "lemar"], t.tokenize(s))

		t = Tokenizer(case_fold=False, stem=False)
		self.assertEqual(["Great", "pass", "Lemar"], t.tokenize(s))

		t = Tokenizer(case_fold=True)
		self.assertEqual(["great", "pass", "lemar"], t.tokenize(s))

	def test_punctuation(self):
		"""
		Test the punctuation removal functionality
		"""

		s = "Kroos scored the winning goal, assisted by Reus!"

		t = Tokenizer(remove_punctuation=False)
		self.assertEqual(["kroo", "score", "the", "win", "goal,", "assist", "reus!"], t.tokenize(s))

		t = Tokenizer(remove_punctuation=True)
		self.assertEqual(["kroo", "score", "the", "win", "goal", "assist", "reu"], t.tokenize(s))

		t = Tokenizer(remove_punctuation=True, stem=False)
		self.assertEqual(["kroos", "scored", "the", "winning", "goal", "assisted", "reus"], t.tokenize(s))

	def test_token_length(self):
		"""
		Test the token length filtlering functionality
		"""

		s = "Kroos scored the winning goal, assisted by Reus!"

		t = Tokenizer()
		self.assertEqual(["kroo", "score", "the", "win", "goal", "assist", "reu"], t.tokenize(s))

		t = Tokenizer(min_length=4)
		self.assertEqual(["kroo", "score", "win", "goal", "assist", "reu"], t.tokenize(s))

	def test_stemming(self):
		"""
		Test the Porter stemming functionality
		"""

		s = "Kroos scored the winning goal, assisted by Reus!"

		t = Tokenizer(stem=False)
		self.assertEqual(["kroos", "scored", "the", "winning", "goal", "assisted", "reus"], t.tokenize(s))

		t = Tokenizer(stem=True)
		self.assertEqual(["kroo", "score", "the", "win", "goal", "assist", "reu"], t.tokenize(s))

	def test_negation_correction(self):
		"""
		Test the negation correction functionality
		"""

		s = "Reus wouldn't have scored"

		t = Tokenizer(remove_punctuation=False, stem=False)
		tokens = t.tokenize(s)
		self.assertEqual(tokens, ["reus", "wouldn't", "have", "scored"] )

		t = Tokenizer(remove_punctuation=False, negation_correction=True)
		self.assertEqual(t._stem(t._correct_negations(tokens)), t.tokenize(s))

		t = Tokenizer(remove_punctuation=True, negation_correction=True)
		self.assertEqual(t._postprocess(t._correct_negations(tokens)), t.tokenize(s))

		s = "Kroos wouldn't have scored if it weren't for Reus. They wouldn't have had anything to play for."
		t = Tokenizer(negation_correction=True)
		self.assertEqual(["kroo", "wouldn", "nothav", "notscor", "notif", "notit", "weren", "notfor", "notreu", "they", "wouldn", "nothav", "nothad", "notanyth", "notto", "notplay", "notfor"], t.tokenize(s))

	def test_unicode_removal(self):
		"""
		Test the unicode entity removal functionality
		"""

		s = "\u0632\u0648\u062f_\u0641\u0648\u0644\u0648\u0631\u0632_\u0645\u0639_\u0627\u0644\u0645\u0628\u0627\u062d\u062b"

		t = Tokenizer(remove_unicode_entities=False)
		self.assertEqual([], t.tokenize(s))

		t = Tokenizer(remove_unicode_entities=True)
		self.assertEqual([], t.tokenize(s))
