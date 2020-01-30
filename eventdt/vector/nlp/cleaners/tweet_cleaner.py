"""
A cleaner that specializes in tweets.
"""

import re

from .cleaner import Cleaner

class TweetCleaner(Cleaner):
	"""
	The tweet cleaner removes spurious needless information from a text.
	This includes retweet syntax and URLs.
	"""

	def clean(self, text):
		"""
		Clean the given text.

		:param text: The text to clean.
		:type text: str

		:return: The cleaned text.
		:rtype: str
		"""

		text = self._preprocess(text)

		text = self._remove_twitter_urls(text)
		text = self._remove_emojis(text)
		text = self._remove_alt_codes(text)
		text = self._remove_retweet_prefix(text)
		text = self._normalize_hashtags(text)

		text = self._remove_consecutive_whitespaces(text)
		text = self._complete_sentences(text)
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

		retweet_pattern = re.compile("^RT @.*?: ")

		return retweet_pattern.sub("", text)
