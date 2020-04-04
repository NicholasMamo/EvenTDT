"""
A cleaner takes in strings and cleans them according to some rules.
Any configuration is passed on to the constructor :func:`nlp.cleaners.cleaner.Cleaner.__init__`.
Without any configuration, the cleaner should change nothing.
Then, the cleaners' main functionality revolves around the :func:`nlp.cleaners.cleaner.Cleaner.clean` function.
"""

import re

class Cleaner(object):
	"""
	The base cleaner is meant to perform only basing pre-processing and cleaning.
	These functions are generally applicable to any type of text.

	:ivar remove_alt_codes: A boolean indicating whether alt-codes should be removed.
	:vartype remove_alt_codes: bool
	:ivar complete_sentences: A boolean indicating whether the sentences should be completed.
							  The cleaner has no knowledge of any incomplete sentences in the middle of the text.
							  Therefore it only completes the last sentence.
	:vartype complete_sentences: bool
	:ivar collapse_new_lines: A boolean indicating whether new lines should be collapsed into whitespaces.
	:vartype collapse_new_lines: bool
	"""

	def __init__(self, remove_alt_codes=False,
					   complete_sentences=False,
					   collapse_new_lines=False):
		"""
		Create the cleaner with the basic configuration.

		:param remove_alt_codes: A boolean indicating whether alt-codes should be removed.
		:type remove_alt_codes: bool
		:param complete_sentences: A boolean indicating whether the sentences should be completed.
								   The cleaner has no knowledge of any incomplete sentences in the middle of the text.
								   Therefore it only completes the last sentence.
		:type complete_sentences: bool
		:param collapse_new_lines: A boolean indicating whether new lines should be collapsed into whitespaces.
		:type collapse_new_lines: bool
		"""

		self.remove_alt_codes = remove_alt_codes
		self.complete_sentences = complete_sentences
		self.collapse_new_lines = collapse_new_lines

	def clean(self, text):
		"""
		Clean the given text.
		The basic cleaner always strips empty whitespaces before any pre-processing.

		:param text: The text to clean.
		:type text: str

		:return: The cleaned text.
		:rtype: str
		"""

		text = text.strip()
		text = self._collapse_new_lines(text) if self.collapse_new_lines else text
		text = self._remove_alt_codes(text) if self.remove_alt_codes else text
		text = self._complete_sentences(text) if self.complete_sentences else text

		return text

	def _collapse_new_lines(self, text):
		"""
		Collapse new lines into white spaces.
		"""

		return text.replace('\n', ' ')

	def _remove_alt_codes(self, text):
		"""
		Remove alt-codes from the given text.

		:param text: The text to clean.
		:type text: str

		:return: The text without alt-codes.
		:rtype: str
		"""

		alt_code_pattern = re.compile('&.+?;')
		return alt_code_pattern.sub('', text)

	def _complete_sentences(self, text):
		"""
		Add a period if the sentence does not end with punctuation.
		There is one exception to this rule: if the sentence ends with a quote.
		In this case, the period is added before the quote if there is no punctuation there..

		:param text: The text to clean.
		:type text: str

		:return: The text without alt-codes.
		:rtype: str
		"""

		punctuation = ['.', '?', '!', '…']
		quotes = ['\'', '"', '»']

		"""
		If the text is empty, return immediately.
		"""
		if not text:
			return text

		"""
		If the text already ends in punctuation, return immediately.
		"""
		if (text[-1] in punctuation or
			(len(text) > 1 and text[-2] in punctuation)):
			return text

		"""
		If the text is just a quote, return immediately.
		"""
		if text in quotes:
			return text

		"""
		If the text ends with a quote, but is not a complete sentence before the quote, add a period.
		"""
		if len(text) > 1 and text[-1] in quotes and text[-2] not in punctuation:
			return f"{text[:-1]}.{text[-1]}"

		"""
		Otherwise, add a period at the end.
		"""
		return f"{text}."

	def _remove_consecutive_whitespaces(self, text):
		"""
		Remove consecutive whitespaces and replace them with a single space.

		:param text: The text to clean.
		:type text: str

		:return: The normalized text.
		:rtype: str
		"""

		whitespace_pattern = re.compile("\s{2,}")
		return whitespace_pattern.sub(" ", text) # replace consecutive whitespaces with a single one
