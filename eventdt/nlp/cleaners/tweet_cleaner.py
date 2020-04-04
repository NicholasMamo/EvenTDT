"""
The tweet cleaner builds on the base cleaner, but adds Twitter-specific functionality.
"""

import re

from .cleaner import Cleaner

class TweetCleaner(Cleaner):
	"""
	The tweet cleaner removes needless information from a text to make it presentable.
	This includes retweet syntax and URLs.
	"""

	def __init__(self, *args, **kwargs):
		"""
		Create the tweet cleaner.

		The same configuration accepted by the :class:`~nlp.cleaners.cleaner.Cleaner` are accepted as arguments and keyword arguments.
		They are then passed on to the parent constructor, :func:`~nlp.cleaners.cleaner.Cleaner.__init__`.
		"""

		super(TweetCleaner, self).__init__(*args, **kwargs)

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
		text = self._collapse_whitespaces(text) if self.collapse_whitespaces else text

		return text

	def _remove_emojis(self, text):
		"""
		Remove emojis from the given text.

		:param text: The tweet to be cleaned.
		:type text: str

		:return: The tweet without emojis.
		:rtype: str
		"""

		# TODO: Doesn't really remove emojis, does it?
		emoji_pattern = re.compile(":[DP\(\)]")
		return emoji_pattern.sub("", text)

	def _remove_twitter_urls(self, text):
		"""
		Remove Twitter short URLs from the text.

		:param text: The tweet that may contain URLs.
		:type text: str

		:return: The tweet without URLs.
		:rtype: str
		"""

		url_pattern = re.compile("https:\\/\\/t.co\\/[a-zA-Z0-9]+\\b")
		return url_pattern.sub("", text)

	def _normalize_hashtags(self, text):
		"""
		Normalize the given text, splitting hashtags based on camel case notation.

		:param text: The text to normalize.
		:type text: str

		:return: The normalized string.
		:rtype: str
		"""
		hashtag_pattern = re.compile("#([a-zA-Z0-9_]+)")
		camel_case_pattern = re.compile("#?(([a-z]+?)([A-Z]+))")

		for hashtag in hashtag_pattern.findall(text):
			"""
			If the hashtag has camel-case notation, normalize it.
			Otherwise, remove the hashtag altogethe.
			"""
			if len(camel_case_pattern.findall(hashtag)) > 0:
				text = text.replace("#%s" % hashtag, hashtag, 1) # remove the hashtag symbol
				text = text.replace(hashtag, camel_case_pattern.sub("\g<2> \g<3>", hashtag), 1)
			else:
				text = text.replace("#%s" % hashtag, "", 1)

		return text

	def _remove_retweet_prefix(self, text):
		"""
		Remove retweet syntax from a tweet.
		Retweets start with the text 'RT @user: '

		:param text: The tweet to clean.
		:type text: str

		:return: The cleaned text.
		:rtype: str
		"""

		retweet_pattern = re.compile("^RT @.+?: ")

		return retweet_pattern.sub("", text)
