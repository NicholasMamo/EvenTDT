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

        - An entity always starts with a proper noun, but it can also contain numbers (for example, Ligue 1).
        """

        # NOTE: Interesting behavior if NP does not have ENT in it

        grammar = grammar or """
                  ENT: { <NNP.*>+(<CD|NNP.*>)* }
                  JJMOD: { <JJ.*>(<CC|,><JJ.*>)+? }
                  MOD: { <JJ.*|VBG|RB.*>* }
                  NP: { <MOD|JJMOD>?<NN.*>+ }
                  HEAD:{ <NP|ENT>+ }
                  VALUE: { <HEAD> }
                  NAME: { <VB.*> }
                  PPATTR: { <IN>?(<DT>?<VALUE><CC|,>?)+ }
                  ATTR: { <NAME><MOD>?<PPATTR>+ }
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
                name, value_subtrees = self._to_attributes(subtree)
                for value_subtree in value_subtrees:
                    preposition = self._get_preposition(value_subtree)
                    name_pp = f"{name}_{ preposition }" if preposition else name
                    profile.attributes[name_pp] = profile.attributes.get(name_pp) or set()
                    attributes = self._get_attribute(value_subtree)
                    for attribute in attributes:
                        profile.attributes[name_pp].add(self._attribute_value(attribute))

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

        :param subtree: The subtree which will be split into attributes.
        :type subtree: :class:`nltk.tree.Tree`

        :return: The attribute as a tuple, with the first value being the name and the second being the value.
                 The attribute values are returned as lists of subtrees.
        :rtype: tuple of str and list :class:`nltk.tree.Tree`
        """

        name = [ component for component in subtree.subtrees() if component.label() == 'NAME' ][0]
        name = [ text for text, pos in name.leaves() ]
        values = [ component for component in subtree.subtrees() if component.label() == 'PPATTR' ]

        return ('_'.join(name).lower(), values)

    def _get_preposition(self, subtree):
        """
        Extract the preposition from the given subtree, or ``None`` if the subtree doesn't have one.

        :param subtree: The subtree from where to extract the preposition.
        :type subtree: :class:`nltk.tree.Tree`

        :return: The first preposition in the subtree or ``None`` if there is no preposition.
        :rtype: str or None
        """

        prepositions = [ text.lower() for text, pos in subtree.leaves() if pos == 'IN' ]
        return prepositions[0] if prepositions else None

    def _get_attribute(self, subtree):
        """
        Extract the attribute subtree from the given subtree.

        :param subtree: The subtree from where to extract the attribute value.
        :type subtree: :class:`nltk.tree.Tree`

        :return: The attribute value in the subtree.
        :rtype: :class:`nltk.tree.Tree`
        """

        return [ _subtree for _subtree in subtree.subtrees() if _subtree.label() == 'VALUE' ]

    def _attribute_value(self, subtree):
        """
        Extract the attribute value from the given value subtree.
        The tree has several components, including adjectives; this function extracts only the value.

        :param subtree: The subtree from where to extract the attribute value.
        :type subtree: :class:`nltk.tree.Tree`

        :return: The actual value from the attribute value subtree.
        :rtype: str
        """

        value = [ ]
        head = [ node for node in subtree if node.label() == 'HEAD' ][0]
        head = head[-1] if (type(head[-1]) is nltk.tree.Tree and head[-1].label()) == 'ENT' else head
        for text, pos in head.leaves():
            value.append(text)
        return (' '.join(value).lower())
