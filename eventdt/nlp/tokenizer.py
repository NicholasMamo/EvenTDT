"""
The tokenizer takes plain text and splits it into a list of tokens.
Tokens are the equivalent of document features, or vector dimensions.

Tokenization is the first of two steps to create a :class:`~nlp.document.Document`.
The second step is term-weighting using a :class:`~nlp.term_weighting.scheme.TermWeightingScheme`.
A term-weighting scheme receives tokens and creates a weighted :class:`~nlp.document.Document` out of them.

The tokenizer takes its settings in the constructor.
All tokenization happens using the :func:`~nlp.tokenizer.Tokenizer.tokenize` function.
In this way, all documents are tokenized in the same way.
Creating and using a tokenizer is very simple:

.. code-block:: python

  t = Tokenizer(stem=True, split_hashtags=True)
  tokens = t.tokenize()

.. note::

	Stemming is based on, and requires, NLTK.
"""

from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.stem.porter import *

import os
import string
import sys

path = os.path.join(os.path.dirname(__file__))
if path not in sys.path:
	sys.path.insert(1, path)

import re
import unicodedata

class Tokenizer(object):
	"""
	The tokenizer takes in strings and converts them into tokens.

	:ivar stemmer: The Porter Stemmer used by the class.
	:vartype stemmer: :class:`~nltk.stem.porter.PorterStemmer`
	:ivar remove_mentions: A boolean indicating whether mentions (@) should be removed.
	:vartype remove_mentions: bool
	:ivar remove_hashtags: A boolean indicating whether hashtags (#) should be removed.
	:vartype remove_hashtags: bool
	:ivar split_hashtags: A boolean indicating whether hashtags (#) should be normalized.
		This converts hashtags of the type #HashTag to `Hash Tag`, based on camel-case.
	:vartype split_hashtags: bool
	:ivar remove_numbers: A boolean indicating whether numbers should be removed.
	:vartype remove_numbers: bool
	:ivar remove_urls: A boolean indicating whether URLs should be removed.
	:vartype remove_urls: bool
	:ivar remove_alt_codes: A boolean indicating whether ALT-codes should be removed.
	:vartype remove_alt_codes: bool
	:ivar normalize_words: A boolean indicating whether words should be normalized.
		This removes repeated characters.
		The number of repeated characters that are removed is controlled using the `character_normalization_count` parameter.
	:vartype normalize_words: bool
	:ivar character_normalization_count: The number of times a character is repeated before they are reduced to one.
	:vartype character_normalization_count: int
	:ivar case_fold: A boolean indicating whether the tokens should be case-folded to lowercase.
	:vartype case_fold: bool
	:ivar remove_punctuation: A boolean indicating whether punctuation should be removed.
	:vartype remove_punctuation: bool
	:ivar remove_unicode_entities: A boolean indicating whether unicode entities should be removed.
	:vartype remove_unicode_entities: bool
	:ivar min_length: The minimum length of tokens that should be retained.
	:vartype min_length: int
	:ivar stopwords: A list of stopwords.
		Stopwords are common words that are removed from token lists.
		This is based on the assumption that they are not very expressive.
		Normally, stopwords are provided as a list, and then converted into a dict, where the stopwords are the keys.
		This approach is adopted since Python uses hashing to check whether a key is in a dict.
		However, they may also be provided as a dict directly.
	:vartype stopwords: list
	:ivar stem: A boolean indicating whether the tokens should be stemmed.
	:vartype stem: bool
	:ivar normalize_special_characters: A boolean indicating whether accents should be removed and replaced with simple unicode characters.
	:vartype normalize_special_characters: bool
	:ivar stem_cache: A mapping of tokens and their stems.
					  The keys are the original tokens and the values are their stems.
	:vartype stem_cache: dict
	:ivar url_pattern: The pattern used to identify URLs in the text.
	:vartype url_pattern: :class:`re.Pattern`
	:ivar alt_code_pattern: The pattern used to identify and remove alt-codes from the text.
	:vartype alt_code_pattern: :class:`re.Pattern`
	:ivar mention_pattern: The pattern used to identify mentions in the text.
	:vartype mention_pattern: :class:`re.Pattern`
	:ivar hashtag_pattern: The pattern used to identify hashtags in the text.
	:vartype hashtag_pattern: :class:`re.Pattern`
	:ivar word_normalization_pattern: The pattern used to identify words with repeated characters.
	:vartype word_normalization_pattern: :class:`re.Pattern`
	:ivar number_pattern: The pattern used to identify numbers in the text.
	:vartype number_pattern: :class:`re.Pattern`
	:ivar tokenize_pattern: The pattern used to split the text into tokens.
	:vartype tokenize_pattern: :class:`re.Pattern`
	:ivar camel_case_pattern: The pattern used to identify camel-case letters.
	:vartype camel_case_pattern: :class:`re.Pattern`
	:ivar nouns_only: A boolean indicating whether to extract only nouns.
	:vartype nouns_only: bool
	"""

	def __init__(self, remove_mentions=True, remove_hashtags=False, split_hashtags=True,
				 remove_numbers=True, remove_urls=True, remove_alt_codes=True,
				 normalize_words=False, character_normalization_count=3, case_fold=True,
				 remove_punctuation=True, remove_unicode_entities=False,
				 min_length=3, stopwords=None, stem=True, normalize_special_characters=True,
				 nouns_only=False):
		"""
		Initialize the tokenizer.

		:param remove_mentions: A boolean indicating whether mentions (@) should be removed.
		:type remove_mentions: bool
		:param remove_hashtags: A boolean indicating whether hashtags (#) should be removed.
		:type remove_hashtags: bool
		:param split_hashtags: A boolean indicating whether hashtags (#) should be normalized.
			This converts hashtags of the type #HashTag to `Hash Tag`, based on camel-case.
		:type split_hashtags: bool
		:param remove_numbers: A boolean indicating whether numbers should be removed.
		:type remove_numbers: bool
		:param remove_urls: A boolean indicating whether URLs should be removed.
		:type remove_urls: bool
		:param remove_alt_codes: A boolean indicating whether ALT-codes should be removed.
		:type remove_alt_codes: bool
		:param normalize_words: A boolean indicating whether words should be normalized.
								This removes repeated characters.
								The number of repeated characters that are removed is controlled using the `character_normalization_count` parameter.
		:type normalize_words: bool
		:param character_normalization_count: The number of times a character is repeated before they are reduced to one.
		:type character_normalization_count: int
		:param case_fold: A boolean indicating whether the tokens should be case-folded to lowercase.
		:type case_fold: bool
		:param remove_punctuation: A boolean indicating whether punctuation should be removed.
		:type remove_punctuation: bool
		:param remove_unicode_entities: A boolean indicating whether unicode entities should be removed.
										Note that this also includes emojis.
		:type remove_unicode_entities: bool
		:param min_length: The minimum length of tokens that should be retained.
		:type min_length: int
		:param stopwords: A list of stopwords: common words that are removed from token lists.
						  This is based on the assumption that they are not very expressive.
						  Normally, stopwords are provided as a list, and then converted into a dict, where the stopwords are the keys.
						  This approach is adopted since Python uses hashing to check whether a key is in a dict.
						  However, they may also be provided as a dict directly.
		:type stopwords: list
		:param stem: A boolean indicating whether the tokens should be stemmed.
		:type stem: bool
		:param normalize_special_characters: A boolean indicating whether accents should be removed and replaced with simple unicode characters.
		:type normalize_special_characters: bool
		:param nouns_only: A boolean indicating whether to extract only nouns.
		:type nouns_only: bool
		"""

		# TODO: Add number normalization (to remove commas)
		# TODO: Add number normalization (text to numbers)

		"""
		Convert the stopword list into a dictionary if need be.
		"""
		stopwords = dict() if stopwords is None else stopwords
		self.stopword_dict = stopwords if type(stopwords) == dict else { stopword: 0 for stopword in stopwords }

		self.stemmer = PorterStemmer()

		self.remove_mentions = remove_mentions
		self.remove_hashtags = remove_hashtags
		self.split_hashtags = split_hashtags
		self.remove_numbers = remove_numbers
		self.remove_urls = remove_urls
		self.remove_alt_codes = remove_alt_codes
		self.normalize_words = normalize_words
		self.character_normalization_count = character_normalization_count
		self.case_fold = case_fold
		self.remove_punctuation = remove_punctuation
		self.remove_unicode_entities = remove_unicode_entities
		self.min_length = min_length
		self.stopwords = stopwords
		self.stem_tokens = stem
		self.normalize_special_characters = normalize_special_characters
		self.nouns_only = nouns_only

		self.stem_cache = { }

		"""
		The list of regular expressions to be used.
		"""
		self.url_pattern = re.compile("(https?:\/\/)?([^\s]+)?\.[a-zA-Z0-9]+?\/?([^\s,\.]+)?")
		self.alt_code_pattern = re.compile("&.+?;")
		self.mention_pattern = re.compile("@[a-zA-Z0-9_]+")
		self.hashtag_pattern = re.compile("#([a-zA-Z0-9_]+)")
		self.word_normalization_pattern = re.compile("(.)\\1{%d,}" % (self.character_normalization_count - 1))
		self.number_pattern = re.compile("\\b([0-9]{1,3}|[0-9]{5,})\\b") # preserve years
		self.tokenize_pattern = re.compile("\s+")
		self.camel_case_pattern = re.compile("(([a-z]+)?([A-Z]+|[0-9]+))")

	def tokenize(self, text):
		"""
		Tokenize the given text.

		:param text: The text to tokenize.
		:type text: str

		:return: A list of tokens.
		:rtype: list
		"""

		"""
		Split hashtags, casefold and remove accents.
		"""
		text = self._split_hashtags(text) if self.split_hashtags else text
		text = ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')) if self.normalize_special_characters else text

		"""
		Remove illegal components.
		"""
		text = self.url_pattern.sub("", text) if self.remove_urls else text
		text = self.alt_code_pattern.sub("", text) if self.remove_alt_codes else text
		text = text.encode('ascii', 'ignore').decode("utf-8") if self.remove_unicode_entities else text
		text = self.word_normalization_pattern.sub("\g<1>", text) if self.normalize_words else text
		text = self.mention_pattern.sub("", text) if self.remove_mentions else text
		text = self.hashtag_pattern.sub("", text) if self.remove_hashtags else self.hashtag_pattern.sub("\g<1>", text)
		text = self.number_pattern.sub("", text) if self.remove_numbers else text

		"""
		After pre-processing, certain steps occur differently depending on whether POS tagging is applied.
		"""
		if self.nouns_only:
			tokens = self._nouns(text)
		else:
			text = ''.join([ char if char not in string.punctuation + '’' else ' ' for char in text ]) if self.remove_punctuation else text
			tokens = self.tokenize_pattern.split(text)

		"""
		Post-process the tokens.
		"""
		tokens = [ token for token in tokens if token not in self.stopword_dict ]
		tokens = [ token for token in tokens if len(token) >= self.min_length ]
		tokens = [ token.lower() for token in tokens ] if self.case_fold else tokens
		tokens = self._stem(tokens) if self.stem_tokens else tokens

		return tokens

	def _split_hashtags(self, string):
		"""
		Split the hashtags in the given string based on camel-case notation.

		:param string: The string to normalize.
		:type string: str

		:return: The normalized string.
		:rtype: str
		"""

		"""
		First find all hashtags.
		Then, split them and replace the hashtag lexeme with the split components.
		"""
		hashtags = self.hashtag_pattern.findall(string)
		for hashtag in hashtags:
			components = self.camel_case_pattern.sub("\g<2> \g<3>", hashtag)

			"""
			Only split hashtags that have multiple components.
			If there is only one component, it's just a hashtag.
			"""
			if len(components.split()) > 1:
				string = string.replace(f"#{hashtag}", components)

		return string

	def _nouns(self, string):
		"""
		Extract the nouns from the given string.
		This process is based on NLTK.
		It first splits sentences, then it tags words and finally extracts only nouns.

		:param string: The string from which to extract nouns.
		:type string: str

		:return: A list of noun tokens.
		:rtype: list of str
		"""

		sentences = sent_tokenize(string)
		tags = [ tag for sentence in sentences
					 for tag in pos_tag(word_tokenize(sentence)) ]
		nouns = [ word for (word, tag) in tags
					   if tag.startswith('N') ]
		return nouns

	def _stem(self, tokens):
		"""
		Stem the given tokens.
		Stemming is an expensive operation.
		Therefore the function uses a stem cache to avoid re-stemming previously-seen tokens.

		:param tokens: The tokens to stem.
		:type tokens: list of str

		:return: A list of stemmed tokens.
		:rtype: list of str
		"""

		for i, token in enumerate(tokens):
			"""
			Re-use the stemmed token if it is cached.
			Otherwise, stem the token and cache it.
			"""
			if self.stem_cache.get(token):
				tokens[i] = self.stem_cache.get(token)
			else:
				stem = self.stemmer.stem(token)
				tokens[i] = stem
				self.stem_cache[token] = stem

		return tokens
