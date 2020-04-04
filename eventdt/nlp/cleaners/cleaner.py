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
	"""

	def __init__(self, remove_alt_codes=False):
		"""
		Create the cleaner with the basic configuration.

		:param remove_alt_codes: A boolean indicating whether alt-codes should be removed.
		:type remove_alt_codes: bool
		"""

		self.remove_alt_codes = remove_alt_codes

	def clean(self, text):
		"""
		Clean the given text.

		:param text: The text to clean.
		:type text: str

		:return: The cleaned text.
		:rtype: str
		"""

		text = self._remove_alt_codes(text) if self.remove_alt_codes else text

		return text

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

		:param text: The text to clean.
		:type text: str

		:return: The text without alt-codes.
		:rtype: str
		"""

		text = text.strip()
		punctuation = ['.', '?', '!', '…']
		quotes = ['\'', '"']

		if len(text) > 1 and text[-1] in quotes and text[-2] in punctuation:
			return text
		elif len(text) > 1 and text[-1] in quotes and text[-2] not in punctuation:
			return text[:-1] + '.' + text[-1]
		elif len(text) > 0 and text[-1] not in punctuation:
			return text.strip() + '.'
		else:
			return text

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

	def _preprocess(self, text):
		"""
		Preprocess the text.
		This function first replaces newlines with whitespaces.
		Then, the function removes consecutive whitespaces and replaces them with a single space.

		:param text: The text to clean.
		:type text: str

		:return: The preprocessed text.
		:rtype: str
		"""

		text = text.replace("\n", " ") # replace newlines with whitespaces

		text = text.strip() # remove extra spaces on each end
		return text
