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

        # TODO: Handle conjunctions in the attribute value
        # TODO: Handle commas in the attribute value
        # TODO: Handle head nouns in the attribute value
        # TODO: Handle proper nouns being the head nouns in the attribute value
        # TODO: Handle prepositions/subordinating conjunctions

        grammar = grammar or """
                  ATRV: { <JJ.*|VBG|NN.*|CD>*<NN.*> }
                  ATRN: { <VB.*> }
                  ATTR: { <ATRN><RB|IN|DT>*?<ATRV> }
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

        profile = Profile()

        sentences = nltk.sent_tokenize(text)
        for sentence in sentences:
            tree = self._parse(sentence)
            subtrees = self._attribute_subtrees(tree)
            for subtree in subtrees:
                name, values = self._to_attributes(subtree)
                for value in values:
                    profile.attributes[name] = profile.attributes.get(name) or [ ]
                    profile.attributes[name].append(self._attribute_value(value))

        return profile

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

    def _attribute_subtrees(self, tree):
        """
        Extract the attributes from the given tree.
        At this point, the function only extracts the attributes as defined by the grammar.

        :param tree: The parse tree of a sentence.
        :type tree: :class:`nltk.tree.Tree`

        :return: Subtrees from the tree that correspond to attributes.
        :rtype: list of :class:`nltk.tree.Tree`
        """

        subtrees = [ node for node in tree if type(node) is nltk.tree.Tree ]
        subtrees = [ subtree for subtree in subtrees if subtree.label() == 'ATTR' ]
        return subtrees

    def _to_attributes(self, subtree):
        """
        Convert the given attribute subtree into a list of attributes.
        One subtree may return multiple attributes because of conjunctions.

        :param subtree: The subtree which will be converted into attributes.
        :type subtree: :class:`nltk.tree.Tree`

        :return: The attribute as a tuple, with the first value being the name and the second being the value.
                 The attribute values are returned as lists of subtrees.
        :rtype: tuple of str and list :class:`nltk.tree.Tree`
        """

        name = [ component for component in subtree.subtrees() if component.label() == 'ATRN' ][0]
        name = [ text for text, pos in name.leaves() ]
        values = [ component for component in subtree.subtrees() if component.label() == 'ATRV' ]

        return ('_'.join(name).lower(), values)

    def _attribute_value(self, subtree):
        """
        Extract the attribute value from the given value subtree.
        The tree has several components, including adjectives; this function extracts only the value.

        :param subtree: The subtree from where to extract the attribute value.
        :type subtree: :class:`nltk.tree.Tree`

        :return: The actual value from the attribute value subtree.
        :rtype: str
        """

        value = [ text for text, pos in subtree.leaves() ]
        return (' '.join(value).lower())
