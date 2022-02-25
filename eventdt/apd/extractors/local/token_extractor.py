"""
The token extractor considers all the tokens in the corpus to be candidate participants.
Therefore it does not perform any filtering whatsoever on the corpus.
"""

import json
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ..extractor import Extractor
import twitter

class TokenExtractor(Extractor):
    """
    The token extractor returns all tokens as potential candidates.
    To extract tokens, the token extractor needs a tokenizer, but it is optional.
    If no tokenizer is given, the token extractor uses documents' dimensions as tokens.

    .. note::

        Document dimensions are unique: if a token appears twice in a document, it will still have one dimension.
        Therefore a token extractor without a tokenizer returns only unique terms from each document.

    :ivar ~.tokenizer: The tokenizer used to extract the tokens.
                       If it is given, the tokens are extracted anew.
                       Otherwise, the document dimensions are used instead.
    :vartype ~.tokenizer: :class:`~nlp.tokenizer.Tokenizer` or None
    """

    def __init__(self, tokenizer=None):
        """
        Create the extractor with a tokenizer.

        :param tokenizer: The tokenizer used to extract the tokens.
                          If it is given, the tokens are extracted anew.
                          Otherwise, the document dimensions are used instead.
        :type tokenizer: :class:`~nlp.tokenizer.Tokenizer` or None
        """

        self.tokenizer = tokenizer

    def extract(self, corpus, *args, **kwargs):
        """
        Extract all the potential participants from the corpus.
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
                text = twitter.full_text(tweet)
                text = twitter.expand_mentions(text, tweet)

                candidates.append(self.tokenizer.tokenize(text) if self.tokenizer else text.split())

        return candidates
