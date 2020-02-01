"""
The processing file is responsible for tokenizing strings.
It is based on, and requires, NLTK.
"""

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

	:cvar stemmer: Since the stemmer is used often, it is created and shared by the whole class.
	:vartype stemmer: :class:`nltk.stem.porter.PorterStemmer`

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
	:ivar normalize_uni: A boolean indicating whether accents should be removed and replaced with simple unicode characters.
	:vartype normalize_uni: bool
	"""

	stemmer = PorterStemmer()

	def __init__(self, remove_mentions=True, remove_hashtags=False, split_hashtags=True,
				 remove_numbers=True, remove_urls=True, remove_alt_codes=True,
				 normalize_words=False, character_normalization_count=3, case_fold=True,
				 remove_punctuation=True, remove_unicode_entities=False,
				 min_length=3, stopwords=None, stem=True, normalize_uni=True):
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
		:param normalize_uni: A boolean indicating whether accents should be removed and replaced with simple unicode characters.
		:type normalize_uni: bool
		"""

		"""
		Convert the stopword list into a dictionary if need be.
		"""
		stopwords = dict() if stopwords is None else stopwords
		self.stopword_dict = stopwords if type(stopwords) == dict else { stopword: 0 for stopword in stopwords }

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
		self.normalize_uni = normalize_uni

	def tokenize(self, text):
		"""
		Tokenize the given text.

		:param text: The text to tokenize.
		:type text: str

		:return: A list of tokens.
		:rtype: list
		"""

		"""
		The list of regular expressions to be used.
		"""
		url_pattern = re.compile("(https?:\/\/)?([^\s]+)?\.[a-zA-Z0-9]+?\/?([^\s,\.]+)?")
		alt_code_pattern = re.compile("&.+?;")
		mention_pattern = re.compile("@[a-zA-Z0-9_]+")
		hashtag_pattern = re.compile("#([a-zA-Z0-9_]+)")
		word_normalization_pattern = re.compile("(.)\\1{%d,}" % (self.character_normalization_count - 1))
		number_pattern = re.compile("\\b([0-9]{1,3}|[0-9]{5,})\\b") # preserve years
		tokenize_pattern = re.compile("\s+")

		text = self._process_hashtags(text) if self.split_hashtags else text

		text = text.lower() if self.case_fold else text

		text = ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')) if self.normalize_uni else text

		"""
		Remove illegal components.
		"""
		text = url_pattern.sub("", text) if self.remove_urls else text

		text = alt_code_pattern.sub("", text) if self.remove_alt_codes else text

		text = text.encode('ascii', 'ignore').decode("utf-8") if self.remove_unicode_entities else text

		text = word_normalization_pattern.sub("\g<1>", text) if self.normalize_words else text

		text = mention_pattern.sub("", text) if self.remove_mentions else text

		text = hashtag_pattern.sub("", text) if self.remove_hashtags else hashtag_pattern.sub("\g<1>", text)

		text = number_pattern.sub("", text) if self.remove_numbers else text

		tokens = tokenize_pattern.split(text)

		tokens = self._postprocess(tokens)

		return tokens

	def _process_hashtags(self, string):
		"""
		Normalize the given hashtag, splitting it based on camel case notation.

		:param string: The string to normalize.
		:type string: str

		:return: The normalized string.
		:rtype: str
		"""

		hashtag_pattern = re.compile("#([a-zA-Z0-9_]+)")
		camel_case_pattern = re.compile("(([a-z]+)?([A-Z]+|[0-9]+))")

		"""
		First find all hashtags.
		Then, split them and replace the hashtag lexeme with the split components.
		"""
		hashtags = hashtag_pattern.findall(string)
		for hashtag in hashtags:
			components = camel_case_pattern.sub("\g<2> \g<3>", hashtag)

			"""
			Only split hashtags that have multiple components.
			If there is only one component, it's just a hashtag.
			"""
			if len(components.split()) > 1:
				string = string.replace(f"#{hashtag}", components)

		return string

	def _stem(self, tokens):
		"""
		Stem the given list of tokens using a Porter Stemmer.

		:param tokens: The list of tokens to stem.
		:type tokens: list

		:return: The list of stemmed tokens.
		:rtype: list
		"""

		stemmed_tokens = list(tokens)
		return [ self.stemmer.stem(token) for token in stemmed_tokens ]

	def _split_tokens(self, tokens):
		"""
		Split the token based on punctuation patterns.

		:param tokens: The list of tokens to split.
		:type tokens: list

		:return: The list of split tokens.
		:rtype: list
		"""

		tokenize_pattern = re.compile("\s+")

		split_tokens = list(tokens)

		"""
		Remove characters that are not in the punctuation list.
		This removal could create new spaces in tokens.
		Therefore tokens are split again.
		The list is finally flattened.
		"""
		split_tokens = [
			''.join([
				char if char not in string.punctuation else ' ' for char in token
			]) for token in split_tokens
		] if self.remove_punctuation else split_tokens

		split_tokens = [ token.split() for token in split_tokens ]
		split_tokens = [token for token_list in split_tokens for token in token_list] # flatten the list
		return split_tokens

	def _postprocess(self, tokens):
		"""
		Post-process the tokens.

		:param tokens: The list of tokens to post-process.
		:type tokens: list
		"""

		tokens = self._split_tokens(tokens)

		tokens = [token for token in tokens if token not in self.stopword_dict]

		tokens = [token for token in tokens if len(token) >= self.min_length]

		tokens =  self._stem(tokens) if self.stem_tokens else tokens
		return tokens
