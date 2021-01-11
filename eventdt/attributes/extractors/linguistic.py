"""
The linguistic extractor extracts attributes based on a few grammatical rules that make up a shallow parser.
As usual, the functionality revolves around the :class:`~attributes.extractors.linguistic.LinguisticExtractor`'s :func:`~attributes.extractors.linguistic.LinguisticExtractor.extract` method.

The default grammar assumes that attributes are defined using verbs, and attribute values are nouns.
However, the default grammar can be overriden in the :func:`constructor <attributes.extractors.linguistic.LinguisticExtractor.__init__>`.

This extractor assumes that the text is about a single entity and therefore does not discriminate among attributes.
"""

import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '..', '..')
if path not in sys.path:
    sys.path.append(path)

import nltk

from attributes import Profile
from attributes.extractors import Extractor

class LinguisticExtractor(Extractor):
    """
    The linguistic extractor accepts an optional grammar and uses it to extract attributes from text.
    The grammar can either be defined in the constructor or, if not given, it is defined automatically by the class.

    .. note::

        More details about the grammar are available `here <https://www.guru99.com/pos-tagging-chunking-nltk.html>`_.

    :ivar parser: The parser to use to extract attributes.
    :vartype parser: :class:`nltk.RegexpParser`
    """

    def __init__(self, grammar=None):
        """
        Create the linguistic extractor with an optional grammar.
        If a grammar is not given, a default grammar is used instead.
        """

        grammar = grammar or """
                  NP: { <DT>?<JJ.*|VBG|NN.*|CD>*<NN.*> }
                  VP: { <VB.*><RB>?<IN>?<NP> }
        """
        self.parser = nltk.RegexpParser(grammar)

    def extract(self, text, *args, **kwargs):
        """
        Extract attributes from the given text.
        This function assumes that the text is about a single entity and therefore does not discriminate among attributes.

        :param text: The text from where to extract attributes.
        :type text: str

        :return: A profile of attributes.
                 Each attribute may have a list of values.
        :rtype: :class:`~attributes.profile.Profile`
        """

        sentences = nltk.sent_tokenize(text)
        for sentence in sentences:
            tree = self._parse(sentence)

        return Profile()

    def _parse(self, sentence):
        """
        Parse the given sentence, creating a tree.

        :param sentence: The sentence to parse.
        :type sentence: str

        :return: A parsed sentence in the form of a POS tree.
        :rtype: :class:`nltk.tree.Tree`
        """

        tokens = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(tokens)
        return self.parser.parse(tagged)
