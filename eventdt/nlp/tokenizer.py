"""
The processing file is responsible for tokenizing strings.
It is based on, and requires, NLTK.
"""

from nltk.stem.porter import *

import os
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
	:ivar negation_correction: A boolean indicating whether negation correction should be performed.
		This adds a prefix (`NOT`) to words that follow a negation to differentiate them from non-negated counterparts.
	:vartype negation_correction: bool
	:ivar normalize_uni: A boolean indicating whether accents should be removed and replaced with simple unicode characters.
	:vartype normalize_uni: bool
	"""

	stemmer = PorterStemmer()

	def __init__(self, remove_mentions=True, remove_hashtags=False, split_hashtags=True,
				 remove_numbers=True, remove_urls=True, remove_alt_codes=True,
				 normalize_words=False, character_normalization_count=2, case_fold=True,
				 remove_punctuation=True, remove_unicode_entities=False,
				 min_length=3, stopwords=None, stem=True, negation_correction=False,
				 normalize_uni=True):
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
		:param negation_correction: A boolean indicating whether negation correction should be performed.
			This adds a prefix (`NOT`) to words that follow a negation to differentiate them from non-negated counterparts.
		:type negation_correction: bool
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
		self.negation_correction = negation_correction
		self.normalize_uni = normalize_uni

	def tokenize(self, string):
		"""
		Tokenize the given string.

		:param string: The string to tokenize.
		:type string: str

		:return: A list of tokens.
		:rtype: list
		"""

		"""
		The list of regular expressions to be used.
		"""
		url_pattern = re.compile("(https?:\/\/)?([^\s]+)?\.[a-zA-Z0-9]+?\/?([^\s,\.]+)?")
		alt_code_pattern = re.compile("&.+?;")
		unicode_pattern = re.compile("\\\\u[a-zA-Z0-9]{4}")
		mention_pattern = re.compile("@[a-zA-Z0-9_]+")
		hashtag_pattern = re.compile("#([a-zA-Z0-9_]+)")
		word_normalization_pattern = re.compile("(.)\\1{%d,}" % (self.character_normalization_count - 1))
		number_pattern = re.compile("\\b([0-9]{1,3}|[0-9]{5,})\\b") # preserve years
		punctuation_pattern = re.compile("([^a-zA-Z0-9\-'])") # do not remove apostrophes because of negation
		tokenize_pattern = re.compile("\s+")

		string = self._process_hashtags(string) if self.split_hashtags else string

		string = string.lower() if self.case_fold else string

		string = ''.join((c for c in unicodedata.normalize('NFD', string) if unicodedata.category(c) != 'Mn')) if self.normalize_uni else string

		"""
		Remove illegal components.
		"""
		string = url_pattern.sub("", string) if self.remove_urls else string

		string = alt_code_pattern.sub("", string) if self.remove_alt_codes else string

		string = unicode_pattern.sub("", string) if self.remove_unicode_entities else string

		string = word_normalization_pattern.sub("\g<1>", string) if self.normalize_words else string

		string = mention_pattern.sub("", string) if self.remove_mentions else string

		string = hashtag_pattern.sub("", string) if self.remove_hashtags else hashtag_pattern.sub("\g<1>", string)

		string = number_pattern.sub("", string) if self.remove_numbers else string

		string = punctuation_pattern.sub(" \g<1>", string) if self.remove_punctuation else string

		tokens = tokenize_pattern.split(string)

		"""
		Negation precedes stemming and stopword removal because of words like "never" and "not" which could be removed prematurely.
		"""
		tokens = self._correct_negations(tokens) if self.negation_correction else tokens
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

	def _correct_negations(self, tokens,
			negation_words=["n't", "not", "no", "never"],
			prefix="NOT"):
		"""
		Apply negation correction on the list of tokens.

		:param tokens: The list of tokens to correct.
		:type tokens: list
		:param negation_words: The negation words to look oout for.
		:type negation_words: list
		:param prefix: The prefix to add to corrected tokens.
		:type prefix: str

		:return: The list of corrected tokens.
		:rtype: list
		"""
		negation_pattern = re.compile("(" + '|'.join(negation_words) + ")")
		negations = [True if negation_pattern.findall(token) else False for token in tokens]
		negated_tokens = list(tokens)

		if (sum(negations) > 0):
			"""
			If there are negations, add a prefix up until:
				1. the end of the sentence
				2. the next negation word
			"""
			negation_indices = [i for i in range(0, len(negations)) if negations[i]]
			for index in negation_indices:
				i = index + 1
				while (i < len(negated_tokens)
						and i not in negation_indices
						and negated_tokens[i] not in ['?', '!', '.', "..."]):
					negated_tokens[i] = prefix + negated_tokens[i]
					i += 1

		return negated_tokens

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

	def _split_tokens(self, tokens, remove_punctuation=True):
		"""
		Split the token based on punctuation patterns.

		:param tokens: The list of tokens to stem.
		:type tokens: list

		:return: The list of split tokens.
		:rtype: list
		"""

		punctuation_pattern = re.compile("([^a-zA-Z0-9\-'])") # do not remove apostrophes because of negation
		tokenize_pattern = re.compile("\s+")

		split_tokens = list(tokens)
		split_tokens = [tokenize_pattern.split(punctuation_pattern.sub(" ", token.replace("'", " ")) if self.remove_punctuation else token) for token in split_tokens] # remove apostrophes now and re-tokenize
		split_tokens = [token for token_list in split_tokens for token in token_list] # flatten the list
		return split_tokens

	def _postprocess(self, tokens):
		"""
		Post-process the tokens.
		This is usually performed after possible negation correction.

		:param tokens: The list of tokens to stem.
		:type tokens: list
		"""

		tokens = self._split_tokens(tokens, remove_punctuation=self.remove_punctuation)

		tokens = [token for token in tokens if token not in self.stopword_dict]

		tokens = [token for token in tokens if len(token) >= self.min_length]

		tokens =  self._stem(tokens) if self.stem_tokens else tokens
		return tokens
