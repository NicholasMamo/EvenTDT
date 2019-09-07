"""
The processing file is responsible for tokenizing strings.
It is based on, and requires, NLTK.
"""

from nltk.stem.porter import *

from .document import Document

import re
import unicodedata

class Tokenizer(object):
	"""
	The tokenizer takes in strings and converts them into tokens.

	:ivar stemmer: Since the stemmer is used often, it is created and shared by the whole class.
	:vartype stemmer: :class:`nltk.stem.porter.PorterStemmer`
	"""

	stemmer = PorterStemmer()

	def normalize_hashtags(self, string):
		"""
		Normalize the given hashtag, splitting it based on camel case notation.

		:param string: The string to normalize.
		:type string: str

		:return: The normalized string.
		:rtype: str
		"""
		hashtag_pattern = re.compile("#([a-zA-Z0-9_]+)")
		camel_case_pattern = re.compile("#?(([a-z]+?)([A-Z]+))")

		for hashtag in hashtag_pattern.findall(string):
			string = string.replace(hashtag, camel_case_pattern.sub("\g<2> \g<3>", hashtag), 1)
		return string

	def correct_negations(self, tokens,
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

	def stem(self, tokens):
		"""
		Stem the given list of tokens using a Porter Stemmer.

		:param tokens: The list of tokens to stem.
		:type tokens: list

		:return: The list of stemmed tokens.
		:rtype: list
		"""
		stemmed_tokens = list(tokens)
		return [self.stemmer.stem(token) for token in stemmed_tokens]

	def split_tokens(self, tokens, remove_punctuation=True):
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
		split_tokens = [tokenize_pattern.split(punctuation_pattern.sub(" ", token.replace("'", " ")) if remove_punctuation else token) for token in split_tokens] # remove apostrophes now and re-tokenize
		split_tokens = [token for token_list in split_tokens for token in token_list] # flatten the list
		return split_tokens

	def postprocess(self, tokens, remove_punctuation=True,
			min_length=3,
			stopword_dict={},
			stem=True):
		"""
		Post-process the tokens.
		This is usually performed after possible negation correction.

		:param tokens: The list of tokens to stem.
		:type tokens: list
		:param remove_punctuation: A boolean indicating whether punctuation should be removed.
		:type remove_punctuation: bool
		:param min_length: The minimum length of tokens that should be retained.
		:type min_length: int
		:param stopword_dict: A list of stopwords, stored as keys in a dict.
			This approach is adopted since Python uses hashing to check whether a key is in a dict.
		:type stopword_dict: dict
		:param stem: A boolean indicating whether the tokens should be stemmed.
		:type stem: bool
		"""
		tokens = self.split_tokens(tokens, remove_punctuation=remove_punctuation)

		tokens = [token for token in tokens if token not in stopword_dict]

		tokens = [token for token in tokens if len(token) >= min_length]

		tokens =  self.stem(tokens) if stem else tokens
		return tokens

	def tokenize(self, string, # the string to tokenize
			remove_mentions=True, # a boolean indicating whether tweet mentions should be removedd
			remove_hashtags=False, # a boolean indicating whether hashtags should be removed
			normalize_hashtags=True, # a boolean indicating whether hashtags should be removed
			remove_numbers=True, # a boolean indicating whether numbers should be removed
			remove_urls=True, # a boolean indicating whether URLs should be removed
			remove_alt_codes=True, # a boolean indicating whether alt-codes should be removed
			normalize_words=False, # a boolean indicating whether words should be normalized by removing repeating characters
			character_normalization_count=2, # the number of times that a character should repeat if it is to be normalized, used in conjunction with the normalize_words boolean
			case_fold=True, # a boolean indicating whether the tokens should be converted to lower case
			remove_punctuation=True, # a boolean indicating whether punctuation should be removed
			remove_unicode_entities=False, # a boolean indicating whether unicode entities should be removed
			min_length=3, # the minimum length of tokens
			stopwords=None, # the list of stopwords to use
			stem=True, # a boolean indicating whether a Porter stemmer shold be used
			negation_correction=False, # a boolean indicating whether negation correction should be used
			normalize_uni=True, # a boolean indicating whether accents should be removed and replaced with simple unicode characters
		):
		"""
		Tokenize the given string.

		:param string: The string to tokenize.
		:type string: str
		:param remove_mentions: A boolean indicating whether mentions (@) should be removed.
		:type remove_mentions: bool
		:param remove_hashtags: A boolean indicating whether hashtags (#) should be removed.
		:type remove_hashtags: bool
		:param normalize_hashtags: A boolean indicating whether hashtags (#) should be normalized.
			This converts hashtags of the type #HashTag to `Hash Tag`, based on camel-case.
		:type normalize_hashtags: bool
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
		:param stopwords: A list of stopwords.
			Stopwords are common words that are removed from token lists.
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

		:return: A list of tokens.
		:rtype: list
		"""

		"""
		Use a dictionary for stopwords
		"""
		stopwords = dict() if stopwords is None else stopwords
		stopword_dict = stopwords if type(stopwords) == dict else {stopword: 0 for stopword in stopwords}

		"""
		The list of regular expressions to be used
		"""
		url_pattern = re.compile("(https?:\/\/)?([^\s]+)?\.[a-zA-Z0-9]+?\/?([^\s,\.]+)?")
		alt_code_pattern = re.compile("&.+?;")
		unicode_pattern = re.compile("\\\\u[a-zA-Z0-9]{4}")
		mention_pattern = re.compile("@[a-zA-Z0-9_]+")
		hashtag_pattern = re.compile("#([a-zA-Z0-9_]+)")
		word_normalization_pattern = re.compile("(.)\\1{%d,}" % (character_normalization_count - 1))
		number_pattern = re.compile("\b[0-9]{1,3}\b") # preserve years
		punctuation_pattern = re.compile("([^a-zA-Z0-9\-'])") # do not remove apostrophes because of negation
		tokenize_pattern = re.compile("\s+")

		string = self.normalize_hashtags(string) if normalize_hashtags else string

		string = string.lower() if case_fold else string

		string = ''.join((c for c in unicodedata.normalize('NFD', string) if unicodedata.category(c) != 'Mn')) if normalize_uni else string

		"""
		remove illegal components
		"""
		string = url_pattern.sub("", string) if remove_urls else string

		string = alt_code_pattern.sub("", string) if remove_alt_codes else string

		string = unicode_pattern.sub("", string) if remove_unicode_entities else string

		string = word_normalization_pattern.sub("\g<1>", string) if normalize_words else string

		string = mention_pattern.sub("", string) if remove_mentions else string

		string = hashtag_pattern.sub("", string) if remove_hashtags else hashtag_pattern.sub("\g<1>", string)

		string = number_pattern.sub("", string) if remove_numbers else string

		string = punctuation_pattern.sub(" \g<1>", string) if remove_punctuation else string

		tokens = tokenize_pattern.split(string)

		"""
		negation precedes stemming and stopword removal because of words like "never" and "not" which could be removed prematurely
		"""
		tokens = self.correct_negations(tokens) if negation_correction else tokens
		tokens = self.postprocess(tokens, remove_punctuation=remove_punctuation, min_length=min_length, stopword_dict=stopword_dict, stem=stem)

		return tokens
