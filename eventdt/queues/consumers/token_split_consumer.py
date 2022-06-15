"""
The :class:`~queues.consumers.token_split_consumer.TokenSplitConsumer` splits tweets into different streams based on what tokens they include.
This means that all splits have a simple, thematic focus.

This split consumer allows the splits to overlap, which means that tweets can be assigned to multiple streams.
However, it discards tweets that do not satisfy any split.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from .token_filter_consumer import TokenFilterConsumer
from .split_consumer import SplitConsumer
from nlp import Tokenizer
from nltk.corpus import stopwords
from nlp.weighting import TF
from queues import Queue
import twitter

class TokenSplitConsumer(SplitConsumer):
    """
    The :class:`~queues.consumers.token_split_consumer.TokenSplitConsumer` splits tweets into different streams based on what tokens they include.

    This split consumer uses a :class:`~nlp.tokenizer.Tokenizer` to split the tweets' text into tokens and check if they validate the conditions.
    The class maintains the :class:`~nlp.tokenizer.Tokenizer` in its state.

    This consumer also assumes that its downstream consumers will use :class:`~nlp.document.Document` instances instead of tweets.
    Therefore it converts all tweets into :class:`~nlp.document.Document` instances using the given :class:`~nlp.weighting.TermWeightingScheme`, maintained in its state.
    This is done to improve efficiency.
    Since the split consumer can send one tweet into multiple streams, these streams do not have to tokenize and weight the same tweets again.
    This class tokenizes tweets based on the :func:`full text <twitter.full_text>`.

    .. note::

        The class has to tokenize tweets on behalf of its consumers to decide in which queue to send tweets.
        However, the downstream consumers can tokenize the tweets again themselves.
        All documents have their full text stored in the document's text.
        In addition, the original tweets are stored in the documents' ``tweet`` attribute.

    .. note::

        This class is actually more complicated than it looks.
        Each downstream consumer is actually a :class:`~queues.consumers.token_filter_consumer.TokenFilterConsumer`.
        This class sends all tweets to all token filter consumers.
        It is up to the token filter consumers to accept or reject incoming tweets.

    :ivar matches: The function that is used to check whether a tweet includes the tokens defined in the splits.

                   - If ``any`` is provided, the consumer assigns a tweet to a stream if it includes any of the tokens defined in the corresponding split.
                   - If ``all`` is provided, the consumer assigns a tweet to a stream if it includes all of the tokens defined in the corresponding split.

                   A custom function can be provided.
                   For example, a custom function can define that a tweet satisfies the split if it includes at least two tokens in it.
                   If one is given, it must receive as input a number of boolean values.
                   Its output must be a boolean indicating whether the tweet satisfies the conditions of the split.
    :vartype matches: func
    :ivar ~.tokenizer: The tokenizer to use to tokenize tweets and check if a token is present in the tweets.
    :vartype tokenizer: :class:`~nlp.tokenizer.Tokenizer`
    :ivar scheme: The term-weighting scheme that is used to create documents from tweets.
    :vartype scheme: :class:`~nlp.weighting.TermWeightingScheme`
    """

    def __init__(self, queue, splits, consumer, matches=any, tokenizer=None, scheme=None, *args, **kwargs):
        """
        Initialize the consumer with its :class:`~queues.Queue`.

        For each given split, this function creates one :class:`~queues.consumers.Consumer` of the given type.
        This consumer has its own queue, which receive tweets that satisfy the associated condition.

        Any additional arguments or keyword arguments are passed on to the consumer's constructor.

        :param queue: The queue that receives the entire stream.
        :type queue: :class:`~queues.Queue`
        :param splits: A list of splits, or conditions that determine into which queue a tweet goes.
                       The type of the splits depends on what the :func:`~queues.consumers.split_consumer.SplitConsumer._satisfies` function looks for.
        :type splits: list of str or list of list of str or list of tuple of str
        :param consumer: The type of :class:`~queues.consumers.Consumer` to create for each split.
        :type consumer: type
        :param matches: The function that is used to check whether a tweet includes the tokens defined in the splits.

                        - If ``any`` is provided, the consumer assigns a tweet to a stream if it includes any of the tokens defined in the corresponding split.
                        - If ``all`` is provided, the consumer assigns a tweet to a stream if it includes all of the tokens defined in the corresponding split.

                        A custom function can be provided.
                        For example, a custom function can define that a tweet satisfies the split if it includes at least two tokens in it.
                        If one is given, it must receive as input a number of boolean values.
                        Its output must be a boolean indicating whether the tweet satisfies the conditions of the split.
        :type matches: func
        :param tokenizer: The tokenizer to use to tokenize tweets and check if a token is present in the tweets.
                          If one isn't given, the class creates a custom tokenizer.
        :type tokenizer: None or :class:`~nlp.tokenizer.Tokenizer`
        :param scheme: The term-weighting scheme that is used to create documents from tweets.
                       If ``None`` is given, the :class:`~nlp.weighting.tf.TF` term-weighting scheme is used.
        :type scheme: None or :class:`~nlp.weighting.TermWeightingScheme`
        """

        splits = [ [ split ] if type(split) is str else list(split)
                              for split in splits ]

        self.matches = matches
        self.tokenizer = tokenizer or Tokenizer(stopwords=stopwords.words('english'),
                                                normalize_words=True, character_normalization_count=3,
                                                remove_unicode_entities=True, stem=True)
        self.scheme = scheme or TF()
        super(TokenSplitConsumer, self).__init__(queue, splits, consumer, scheme=scheme, *args, **kwargs)

    def _satisfies(self, document, tokens):
        """
        Check whether the given document includes the given tokens.
        The function checks if any of the given tokens are present in the document's dimensions.

        In reality, this is a dummy function.
        This class sends all tweets downstream to all consumers; it is then the responsibiltiy of each :class:`~queues.consumers.token_filter_consumer.TokenFilterConsumer` to accept or reject tweets.

        :param document: The document to validate whether it contains the given tokens.
        :type document: :class:`~nlp.document.Document`
        :param tokens: The list of tokens that need to be present in the given document.
        :type tokens: list of str

        :return: A boolean indicating whether the given document contains the tokens.
        :rtype: bool
        """

        # NOTE: The TokenFilterConsumer consumer will accept or reject tweets
        return True

    def _consumers(self, consumer, *args, **kwargs):
        """
        Create the consumers which will receive the tweets from each stream.

        Any additional arguments or keyword arguments are passed on to the consumer's constructor.

        :param consumer: The type of :class:`~queues.consumers.Consumer` to create.
        :type consumer: type

        :return: A number of consumers, equivalent to the given number.
                 All consumers are identical to each other, but have their own :class:`~queues.Queue`.
        :rtype: list of :class:`~queues.consumers.Consumer`
        """

        # NOTE: The scheme is passed as part of the kwargs
        return [ TokenFilterConsumer(Queue(), split, consumer, name=str(split),
                                     matches=self.matches, tokenizer=self.tokenizer,
                                     *args, **kwargs)
                 for split in self.splits ]
