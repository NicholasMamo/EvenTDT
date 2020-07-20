"""
The TwitterNER entity extractor uses TwitterNER to exctract named entities.
Like the :class:`~apd.extractors.local.entity_extractor.EntityExtractor`, it considers these named entities to be candidate participants.
The difference between the :class:`TwitterNEREntityExtractor` and the :class:`~apd.extractors.local.entity_extractor.EntityExtractor` is that the former uses a NER tool built specificially for Twitter.

.. note::

	A copy of TwitterNER is available in this directory.
	However, the data has to be downloaded.
	The data, and more instructions on how to get GloVe pre-trained on Twitter are available in `TwitterNER's GitHub repository <https://github.com/napsternxg/TwitterNER>`_.
"""

import os
import sys

import nltk

from ..extractor import Extractor

class TwitterNEREntityExtractor(Extractor):
	"""
	The :class:`TwitterNEREntityExtractor` uses TwitterNER to extract entities from documents.
	This class is built specifically for tweets.
	"""

	def extract(self, corpus, *args, **kwargs):
		"""
		Extract all the named entities from the corpus.
		The output is a list of lists.
		Each outer list represents a document.
		Each inner list is the candidates in that document.

		:param corpus: The corpus of documents where to extract candidate participants.
		:type corpus: list

		:return: A list of candidates separated by the document in which they were found.
		:rtype: list of list of str
		"""

		return [ ]
