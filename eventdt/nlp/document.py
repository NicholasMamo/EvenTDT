"""
Many NLP tasks represent text as documents.
The :class:`~nlp.document.Document` class helps you do just that.
The :class:`~nlp.document.Document` class builds on the :class:`~vsm.vector.Vector` class, which means it represents text in the :class:`~vsm.vector.VectorSpace`.
The big change between the :class:`~vsm.vector.Vector` and the :class:`~nlp.document.Document` is that the latter stores the original text alongside the VSM dimensions.

You can create documents by instantiating the :class:`~nlp.document.Document` class.
However, more generally you would follow these two steps:

1. Convert the text into tokens using a :class:`~nlp.tokenizer.Tokenizer`.
2. Weight the tokens using a :class:`~nlp.weighting.TermWeightingScheme`.
   This automatically transforms tokens into :class:`~vsm.vector.Vector` dimensions and create a :class:`~nlp.document.Document` for you.
"""

import copy
import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.insert(1, path)

import twitter
from vsm import Vector

class Document(Vector):
    """
    The :class:`~nlp.document.Document` class is based on the :class:`~vsm.vector.Vector` class.
    The only big change is the ``text`` instance variable.
    Since a :class:`~nlp.document.Document` is represented as a :class:`~vsm.vector.Vector`, the ``text`` records the original text that generated the :class:`~nlp.document.Document`.

    :ivar text: The document's original text.
    :vartype text: str
    """

    def __init__(self, text='', dimensions=None, scheme=None, *args, **kwargs):
        """
        Initialize the document with the text and, optionally, the underlying vector's dimensions.

        If you only have tokens generated by a :class:`~nlp.tokenizer.Tokenizer`, you can pass them on as dimensions.
        In this case, the :class:`~nlp.document.Document` creates dimensions using the :class:`~nlp.weighting.tf.TF` term-weighting scheme.
        If you want to use a different term-weighting scheme, pass it on using the ``scheme`` parameter.

        Any other arguments or keyword arguments are passed on to the :class:`~vsm.vector.Vector` constructor.
        You can use the keyword arguments to pass on any optional attributes.

        :param text: The document's text.
        :type text: str
        :param dimensions: The initial dimensions of the document.
                           If a list is provided, it is assumed that they are tokens.
                           The dimensions are then created from this list using the given scheme.
        :type dimensions: list or dict
        :param scheme: The term-weighting scheme that is used to convert the tokens into dimensions.
                       If ``None`` is given, the :class:`~nlp.weighting.TermWeighting.TF` term-weighting scheme is used.
        :type scheme: None or :class:`~nlp.weighting.TermWeighting`
        """

        """
        If a list is provided, assume that it is a list of tokens.
        This list of tokens is converted into a dictionary representing the dimensions of the vector.
        The conversion is carried out by the term-weighting scheme.
        """
        if type(dimensions) is list:
            from nlp.weighting.tf import TF # NOTE: The import is located here because of circular dependencies
            scheme = scheme if scheme is not None else TF()
            dimensions = scheme.create(dimensions).dimensions

        super(Document, self).__init__(dimensions, *args, **kwargs)
        self.text = text

    def __str__(self):
        """
        Get the string representation of the document.
        This function returns the document's text.

        :return: The text of the document.
        :rtype: str
        """

        return self.text

    def to_array(self):
        """
        Export the document as an associative array.

        :return: The document as an associative array.
        :rtype: dict
        """

        array = Vector.to_array(self)
        array.update({
            'class': str(Document),
            'text': self.text,
        })
        return array

    @staticmethod
    def from_dict(tweet, dimensions=None):
        """
        Create a document representation of the tweet in the given dict.
        The document has the full text with mentions expanded.

        :param tweet: The dictionary representation of a tweet.
        :type tweet: dict
        :param dimensions: The document's dimensions; if not given, the document has no dimensions.
        :type dimensions: dict or None

        :return: A new :class:`~vector.nlp.document.Document` with the tweet details as attributes.
        :rtype: :class:`~vector.nlp.document.Document`
        """

        document = Document(text=twitter.expand_mentions(twitter.text(tweet), tweet), dimensions=dimensions,
                            attributes={ 'id': twitter.id(tweet), 'version': twitter.version(tweet),
                                         'lang': twitter.lang(tweet), 'timestamp': twitter.timestamp(tweet),
                                         'urls': twitter.urls(tweet), 'hashtags': twitter.hashtags(tweet),
                                         'is_retweet': twitter.is_retweet(tweet), 'is_reply': twitter.is_reply(tweet), 'is_quote': twitter.is_quote(tweet),
                                         'is_verified': twitter.is_verified(tweet), 'tweet': tweet })
        if twitter.version(tweet) == 2:
            document.attributes['annotations'] = twitter.annotations(tweet)
        return document

    @staticmethod
    def from_array(array):
        """
        Create an instance of the document from the given associative array.

        :param array: The associative array with the attributes to create the document.
        :type array: dict

        :return: A new instance of the document with the same attributes stored in the object.
        :rtype: :class:`~vector.nlp.document.Document`
        """

        return Document(text=array.get('text'), dimensions=copy.deepcopy(array.get('dimensions')),
                        attributes=copy.deepcopy(array.get('attributes')))

    @staticmethod
    def concatenate(*args, tokenizer, scheme=None, **kwargs):
        """
        Concatenate all of the documents that are provided as arguments.
        To concatenate the documents, the function:

        1. Concatenates the text of all documents, in the same order as they are given.
        2. Tokenizes the concatenated text using the given tokenizer.
        3. Creates a document with the tokens from the concatenated document.

        Any additional keyword arguments, such as attributes, are passed on to the :class:`~nlp.document.Document` constructor.

        :param scheme: The term-weighting scheme to use to create the concatenated document.
        :type scheme: :class:`~nlp.weighting.TermWeightingScheme`
        :param tokenizer: The tokenizer to use to construct the concatenated document.
        :type tokenizer: :class:`~nlp.tokenizer.Tokenizer`

        :return: A new document representing the concatenated documents.
                 The document is not normalized.
        :rtype: :class:`~nlp.document.Document`
        """

        text = ' '.join([ document.text for document in args ])
        tokens = tokenizer.tokenize(text)
        document = Document(text, tokens, scheme=scheme, **kwargs)
        return document
