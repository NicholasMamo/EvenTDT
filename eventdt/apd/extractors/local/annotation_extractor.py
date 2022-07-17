"""
The annotation extractor does not use NER to extract named entities as candidate participants.
Instead, it relies on Twitter's own named entity annotations of tweets.

.. note::

    Annotations are only provided for Twitter APIv2 tweets.
    Therefore this extractor does not work with Twitter APIv1.1 tweets.
"""

import json
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ..extractor import Extractor
import twitter

class AnnotationExtractor(Extractor):
    """
    The annotation extractor uses Twitter's own named entity annotations, extracting them from tweets and presenting them as candidate participants.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the extractor.
        """

        pass
    
    def extract(self, corpus, *args, **kwargs):
        """
        Extract all the named entities from the corpus.
        The output is a list of lists.
        Each outer list represents a document.
        Each inner list is the candidates in that document.

        :param corpus: A path to the corpus of documents from where to extract candidate participants.
        :type corpus: str

        :return: A list of candidates separated by the document in which they were found.
        :rtype: list of list of str
        """

        candidates = [ ]

        with open(corpus) as f:
            for line in f:
                tweet = json.loads(line)
                candidates.append(twitter.annotations(tweet))
        return candidates
