"""
A scorer that is used to score tweets.
This scorer can operate both on cleaned tweets, and on raw tweets.
"""

from .scorer import Scorer

import math
import re

class TweetScorer(Scorer):
    """
    A scorer that specializes in tweets.
    """

    def score(self, tweet, token_attribute="tokens", *args, **kwargs):
        """
        Evaluate the score of the given tweet.

        :param tweet: The tweet that will be scored.
        :type tweet: :class:`~vsm.nlp.document.Document`
        :param token_attribute: The attribute that contains the tokens.
        :type token_attribute: str

        :return: The tweet's score.
        :rtype: float
        """

        brevity_score = self._brevity_score(tweet.attributes[token_attribute], *args, **kwargs)
        emotion_score = self._emotion_score(tweet.text)

        return brevity_score * emotion_score

    def _brevity_score(self, tokens, ideal_length=10, *args, **kwargs):
        """
        Calculate the brevity score, bounded between 0 and 1.

        This score is based on Papineni et al.'s BLEU (2002):
        score = max(1, e^(1 - r/c))

        The score is 1 even when the tweet is longer than the desired length.
        In this way, the brevity score is more akin to a brevity penalty.

        :param tokens: The list of tokens in the tweet.
        :type tokens: list

        :return: The brevity score, bounded between 0 and 1.
        :rtype: float
        """

        if len(tokens) <= 0:
            return 0
        elif len(tokens) <= ideal_length:
            return math.exp(1 - ideal_length/len(tokens))
        else:
            return 1

    def _emotion_score(self, text, *args, **kwargs):
        """
        Calculate the emotion in the text. This is based on the number of capitalized characters.
        The higher the score, the less emotional the tweet.

        Note that it is not always desirable for the score to be 1.
        That would mean that there is absolutely no capitalization.

        :param text: The text that will be scored.
        :type text: str

        :return: The emotion score, bounded between 0 and 1.
        :rtype: float
        """

        upper_pattern = re.compile("[A-Z]")
        lower_pattern = re.compile("[a-z]")

        upper_characters = len(upper_pattern.findall(text))
        lower_characters = len(lower_pattern.findall(text))

        return 1 - upper_characters/(upper_characters + lower_characters) if (upper_characters + lower_characters) > 0 else 0
