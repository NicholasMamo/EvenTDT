"""
The tweet cleaner builds on the base cleaner, but adds Twitter-specific functionality.
"""

import re

from .cleaner import Cleaner

class TweetCleaner(Cleaner):
	"""
	The tweet cleaner removes needless information from a text to make it presentable.
	This includes retweet syntax and URLs.

	:ivar remove_unicode_entities: A boolean indicating whether unicode entities should be removed.
								   Note that this also includes emojis.
	:vartype remove_unicode_entities: bool
	:ivar remove_urls: A boolean indicating whether URLs should be removed.
	:vartype remove_urls: bool
	:ivar remove_hashtags: A boolean indicating whether hashtags that cannot be split should be removed.
	:vartype remove_hashtags: bool
	:ivar split_hashtags: A boolean indicating whether hashtags should be split.
	:vartype split_hashtags: bool
	:ivar remove_retweet_prefix: A boolean indicating whether the retweet prefix should be removed.
	:vartype remove_retweet_prefix: bool
	"""

	def __init__(self, remove_unicode_entities=False,
					   remove_urls=False,
					   remove_hashtags=False,
					   split_hashtags=False,
					   remove_retweet_prefix=False, *args, **kwargs):
		"""
		Create the tweet cleaner.

		The same configuration accepted by the :class:`~nlp.cleaners.cleaner.Cleaner` are accepted as arguments and keyword arguments.
		They are then passed on to the parent constructor, :func:`~nlp.cleaners.cleaner.Cleaner.__init__`.

		:param remove_unicode_entities: A boolean indicating whether unicode entities should be removed.
										Note that this also includes emojis.
		:type remove_unicode_entities: bool
		:param remove_urls: A boolean indicating whether URLs should be removed.
		:type remove_urls: bool
		:param remove_hashtags: A boolean indicating whether hashtags that cannot be split should be removed.
		:type remove_hashtags: bool
		:param split_hashtags: A boolean indicating whether hashtags should be split.
		:type split_hashtags: bool
		:param remove_retweet_prefix: A boolean indicating whether the retweet prefix should be removed.
		:type remove_retweet_prefix: bool
		"""

		super(TweetCleaner, self).__init__(*args, **kwargs)

		self.remove_unicode_entities = remove_unicode_entities
		self.remove_urls = remove_urls
		self.remove_hashtags = remove_hashtags
		self.split_hashtags = split_hashtags
		self.remove_retweet_prefix = remove_retweet_prefix

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
		text = self._remove_unicode_entities(text) if self.remove_unicode_entities else text
		text = self._remove_urls(text) if self.remove_urls else text
		text = self._split_hashtags(text) if self.split_hashtags else text
		text = self._remove_hashtags(text) if self.remove_hashtags else text
		text = self._remove_retweet_prefix(text) if self.remove_retweet_prefix else text
		text = self._complete_sentences(text) if self.complete_sentences else text
		text = self._collapse_whitespaces(text) if self.collapse_whitespaces else text
		text = text.strip()

		return text

	def _remove_unicode_entities(self, text):
		"""
		Remove unicode entities, including emojis, from the given text.

		:param text: The tweet to be cleaned.
		:type text: str

		:return: The tweet without unicode entities.
		:rtype: str
		"""

		return text.encode('ascii', 'ignore').decode("utf-8")

	def _remove_urls(self, text):
		"""
		Remove Twitter short URLs from the text.

		:param text: The text to clean().
		:type text: str

		:return: The text without URLs.
		:rtype: str
		"""

		url_pattern = re.compile("(https?:\/\/)?([^\s]+)?\.[a-zA-Z0-9]+?\/?([^\s,\.]+)?")
		return url_pattern.sub(' ', text)

	def _split_hashtags(self, text):
		"""
		Split the hashtags in the given text based on camel-case notation.

		:param text: The text to normalize.
		:type text: str

		:return: The text with split hashtags.
		:rtype: str
		"""

		hashtag_pattern = re.compile("#([a-zA-Z0-9_]+)")
		camel_case_pattern = re.compile("(([a-z]+)?([A-Z]+|[0-9]+))")

		"""
		First find all hashtags.
		Then, split them and replace the hashtag lexeme with the split components.
		"""
		hashtags = hashtag_pattern.findall(text)
		for hashtag in hashtags:
			components = camel_case_pattern.sub("\g<2> \g<3>", hashtag)

			"""
			Only split hashtags that have multiple components.
			If there is only one component, it's just a hashtag.
			"""
			if len(components.split()) > 1:
				text = text.replace(f"#{hashtag}", components)

		return text

	def _remove_hashtags(self, text):
		"""
		Remove hashtags from the given text.

		:param text: The text to clean.
		:type text: str

		:return: The text without any hashtags.
		:rtype: str
		"""

		hashtag_pattern = re.compile("#([a-zA-Z0-9_]+)")
		return hashtag_pattern.sub(' ', text)

	def _remove_retweet_prefix(self, text):
		"""
		Remove retweet syntax from a tweet.
		Retweets start with the text 'RT @user: '

		:param text: The text to clean.
		:type text: str

		:return: The cleaned text.
		:rtype: str
		"""

		retweet_pattern = re.compile('^RT @.+?: ')

		return retweet_pattern.sub(' ', text)
