"""
The :class:`~queues.consumers.token_filter_consumer.TokenFilterConsumer` filters tweets based on whether they contain particular tokens.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from .filter_consumer import FilterConsumer
from nlp import Tokenizer
from nltk.corpus import stopwords
from nlp.weighting import TF
import twitter

class TokenFilterConsumer(FilterConsumer):
    """
    The :class:`~queues.consumers.token_filter_consumer.TokenFilterConsumer` filters tweets based on the tokens inside them.

    This filter consumer uses a :class:`~nlp.tokenizer.Tokenizer` to split the tweets' text into tokens and check if they validate the conditions.
    The class maintains the :class:`~nlp.tokenizer.Tokenizer` in its state.

    This consumer also assumes that its downstream consumer will use :class:`~nlp.document.Document` instances instead of tweets.
    Therefore it converts all tweets into :class:`~nlp.document.Document` instances using the given :class:`~nlp.weighting.TermWeightingScheme`, maintained in its state.
    This is done to improve efficiency, so that the downstream consumer does not have to tokenize the same tweet again.
    This class tokenizes tweets based on the :func:`full text <twitter.full_text>`.

    .. note::

        The class has to tokenize tweets on behalf of its consumers to decide whether to retain it.
        However, the downstream consumer still can tokenize the tweets again.
        All documents have their full text stored in the document's text.
        In addition, the original tweets are stored in the documents' ``tweet`` attribute.

    :ivar ~.tokenizer: The tokenizer to use to tokenize tweets and check if a token is present in the tweets.
    :vartype tokenizer: :class:`~nlp.tokenizer.Tokenizer`
    :ivar scheme: The term-weighting scheme that is used to create documents from tweets.
    :vartype scheme: :class:`~nlp.weighting.TermWeightingScheme`
    """
