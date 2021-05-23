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

    def __init__(self, queue, filters, consumer, matches=any, tokenizer=None, scheme=None, *args, **kwargs):
        """
        Initialize the consumer with its :class:`~queues.Queue`, which receives tweets to filter.
        This function creates one :class:`~queues.consumers.Consumer` which will receive the filtered tweets.
        Any additional arguments or keyword arguments are passed on to this consumer's constructor.

        The constructor also creates a :class:`~nlp.tokenizer.Tokenizer`, which it later uses to tokenize and filter tweets.

        :param queue: The queue that receives the entire stream.
        :type queue: :class:`~queues.Queue`
        :param filters: A list of filters, or conditions that determine whether a tweet should be retained or discarded.
                        The filters must lists of tokens.
        :type filters: str or list of str
        :param consumer: The type of :class:`~queues.consumers.Consumer` to create, which will process filtered lists.
        :type consumer: type
        :param matches: The function that is used to check whether a tweet satisfies the filters.

                        - If ``any`` is provided, the consumer assigns a tweet to a stream if it satisfies any of the filters.
                        - If ``all`` is provided, the consumer assigns a tweet to a stream if it satisfies all of the filters.

                        A custom function can be provided.
                        For example, a custom function can define that a tweet satisfies the filter if it includes at least two conditions in it.
                        If one is given, it must receive as input a number of boolean values.
                        Its output must be a boolean indicating whether the tweet satisfies the conditions of the split.
        :type matches: func
        """

        filters = [ filters ] if type(filters) is str else list(filters)

        super(TokenFilterConsumer, self).__init__(queue, filters, consumer, matches,
                                                  scheme=scheme, *args, **kwargs) # save the scheme in the downstream consumer

        self.tokenizer = tokenizer or Tokenizer(stopwords=stopwords.words('english'),
                                                normalize_words=True, character_normalization_count=3,
                                                remove_unicode_entities=True, stem=True)
        self.scheme = scheme or TF()

    def _preprocess(self, tweet):
        """
        Pre-process the given tweet.

        This function assumes that all of the downstream consumers will work with :class:`~nlp.document.Document` instances.
        Therefore it tokenizes the tweets and uses the scheme to convert them into documents.

        :param tweet: The tweet to pre-process.
        :type tweet: dict

        :return: The tweet as a document.
        :rtype: :class:`~nlp.document.Document`
        """

        text = twitter.full_text(tweet)
        text = twitter.expand_mentions(text, tweet)
        tokens = self.tokenizer.tokenize(text)
        document = self.scheme.create(tokens, text=text,
                                      attributes={ 'tweet': tweet,
                                                   'timestamp': twitter.extract_timestamp(tweet) })
        document.normalize()
        return document

    def _satisfies(self, item, condition):
        """
        This function always returns true, adding the tweets to all streams.

        :param item: The tweet, or a pre-processed version of it.
        :type item: any
        :param condition: The condition to check for.
        :type condition: any

        :return: A boolean value of ``True``, adding the tweet to all streams.
        :rtype: bool
        """

        return True
