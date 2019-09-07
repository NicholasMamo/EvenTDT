"""
The general structure of a cleaner.
A cleaner object takes in text and cleans it according to some regular expression rules.
"""

import re

class Cleaner(object):
	"""
	Defines the general structure of a cleaner object.
	This is meant to be used if no cleaning is required, ironically.
	"""

	def clean(self, text):
		"""
		Do nothing with the text, return it normally.

		:param text: The text to clean.
		:type text: str

		:return: The same text.
		:rtype: str
		"""

		return text

	def _remove_alt_codes(self, text):
		"""
		Remove alt-codes from the given text.

		:param text: The text to clean.
		:type text: str

		:return: The text without alt-codes.
		:rtype: str
		"""

		alt_code_pattern = re.compile("&.+?;")
		return alt_code_pattern.sub("", text)

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
